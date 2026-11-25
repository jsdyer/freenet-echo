"""Fetch exact-homepage capture metadata and text signals for selected dated captures."""
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
from html.parser import HTMLParser
import argparse,json,re,time,os,tempfile,shutil
from pathlib import Path
from urllib.parse import urlencode,urlsplit
from urllib.request import Request,urlopen

ROOT=Path(__file__).resolve().parents[1]
SERVICES={'dial-up':r'\bdial[ -]?up\b','email':r'\be[ -]?mail\b','web hosting':r'\b(?:web[ -]?hosting|hosted websites)\b','telnet':r'\btelnet\b','gopher':r'\bgopher\b','Lynx':r'\blynx\b','news groups':r'\bnewsgroups?\b','broadband':r'\b(?:broadband|DSL)\b'}
class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__();self.hidden=0;self.text=[];self.title=False;self.name=[]
    def handle_starttag(self,tag,attrs):
        if tag in ('script','style','noscript'):self.hidden+=1
        if tag=='title':self.title=True
    def handle_endtag(self,tag):
        if tag in ('script','style','noscript'):self.hidden=max(0,self.hidden-1)
        if tag=='title':self.title=False
    def handle_data(self,data):
        if not self.hidden:self.text.append(data)
        if self.title:self.name.append(data)
def request(url,limit,timeout=35):
    for attempt in range(3):
        try:
            with urlopen(Request(url,headers={'User-Agent':'CoolCode FreeNet Echo archive research'}),timeout=timeout)as r: data=r.read(limit+1)
            if len(data)>limit:raise ValueError('Unexpected response size')
            return data
        except OSError:
            if attempt==2:raise
            time.sleep(attempt+1)
def replay(stamp,orig):
    return 'https://web.archive.org/web/'+stamp+'/'+orig
def configuration(path=ROOT/'web/config.json'):
    config=json.loads(path.read_text());seen=set()
    if not isinstance(config.get('networks'),list) or not config['networks']:raise ValueError('No configured networks')
    for net in config['networks']:
        if not re.fullmatch(r'[a-z0-9-]+',net['id']) or net['id'] in seen:raise ValueError('Duplicate or invalid network')
        seen.add(net['id'])
        for key in ['name','city','kind','context','source']:
            if not isinstance(net.get(key),str) or not net[key].strip():raise ValueError('Missing network '+key)
        source=urlsplit(net['source'])
        if source.scheme!='https' or not source.hostname or source.username or source.password:raise ValueError('Use an HTTPS historical source')
        if not isinstance(net.get('history'),list):raise ValueError('Missing historical milestones')
        if not net.get('homepages'):raise ValueError('Missing homepages')
        for site in net['homepages']:
            p=urlsplit('https://'+site)
            if not p.hostname or p.username or p.password or p.query or p.fragment or p.port:raise ValueError('Invalid homepage')
        for field in ['from_year','to_year']:
            if field in net and (type(net[field]) is not int or not 1990<=net[field]<=2100):raise ValueError('Invalid year')
    if not isinstance(config.get('sample_years'),list) or not all(type(y) is int and 1990<=y<=2100 for y in config['sample_years']):raise ValueError('Invalid sample years')
    if not 1<=config['max_capture_rows']<=100000:raise ValueError('Invalid row limit')
    return config

def parse_captures(rows,site,limit):
    expected=urlsplit('https://'+site)
    if not rows:return []
    if rows[0]!=['timestamp','original','digest']:raise ValueError('Unknown archive schema')
    if len(rows)-1>limit:raise ValueError('Capture index exceeds configured row limit; narrow its date range')
    valid=[]
    for row in rows[1:]:
        if not isinstance(row,list) or len(row)!=3:raise ValueError('Malformed archive row')
        stamp,orig,digest=row;parsed=urlsplit(orig)
        if (parsed.hostname or '').lower().removeprefix('www.')!=expected.hostname.removeprefix('www.') or parsed.path.rstrip('/')!=expected.path.rstrip('/') or parsed.query:continue
        if re.fullmatch(r'\d{14}',stamp) and parsed.scheme in ('http','https') and not parsed.username and not parsed.password:
            datetime.strptime(stamp,'%Y%m%d%H%M%S')
            valid.append((stamp,orig,digest))
    return valid

def captures(site,net,limit):
    params=[('url',site),('matchType','exact'),('output','json'),('filter','statuscode:200'),('filter','mimetype:text/html'),('fl','timestamp,original,digest'),('limit',str(limit+1))]
    for key,param in [('from_year','from'),('to_year','to')]:
        if key in net:params.append((param,str(net[key])))
    url='https://web.archive.org/cdx/search/cdx?'+urlencode(params)
    return parse_captures(json.loads(request(url,12_000_000)),site,limit)

def read_capture(args):
    network,year,stamp,orig=args
    try:
        html=request(replay(stamp+'id_',orig),2_000_000,14)
        doc=VisibleText();doc.feed(html.decode('utf-8',errors='replace'))
        body=' '.join(doc.text);title=' '.join(''.join(doc.name).split())
        if not title or 'wayback machine' in title.lower() or 'internal server error' in title.lower():return None
        return (network,year,dict(stamp=stamp,url=orig,title=title[:180],mentions=[k for k,p in SERVICES.items() if re.search(p,body,re.I)]))
    except (ValueError,OSError):return None

def atomic_documents(out,documents):
    out.mkdir(parents=True,exist_ok=True)
    backups={name:(out/name).read_bytes() if (out/name).exists() else None for name in documents}
    try:
        with tempfile.TemporaryDirectory(dir=out) as temp:
            for name,doc in documents.items():
                (Path(temp)/name).write_text(json.dumps(doc,ensure_ascii=False,separators=(',',':'))+'\n')
            for name in documents:os.replace(Path(temp)/name,out/name)
    except Exception:
        for name,content in backups.items():
            if content is None:(out/name).unlink(missing_ok=True)
            else:(out/name).write_bytes(content)
        raise

def main(only_new=False):
    config=configuration();out=ROOT/'web/data';path=out/'captures.json'
    old=json.loads(path.read_text()) if path.exists() else {}
    oldstatus=json.loads((out/'status.json').read_text()) if (out/'status.json').exists() else {}
    result=dict(old);sources=dict(oldstatus.get('sources',{}));failures=[];jobs=[]
    now=datetime.now(timezone.utc).isoformat()
    def collect(net):
        rows=set()
        for site in net['homepages']:rows.update(captures(site,net,config['max_capture_rows']))
        years=defaultdict(list)
        for stamp,url,digest in sorted(rows):years[stamp[:4]].append((stamp,url,digest))
        if not years:raise ValueError('No qualifying homepage records returned')
        records={};samples=[]
        for year,group in years.items():
            first,last=group[0],group[-1]
            record={'count':len(group),'versions':len({digest for _,_,digest in group if digest!='-'}),'first':first[:2],'last':last[:2]}
            existing=old.get(net['id'],{}).get(year,{}).get('text')
            if existing and existing['stamp']==first[0]:record['text']=existing
            elif int(year) in set(config['sample_years'])|{int(min(years)),int(max(years))}:samples.append((net['id'],year,*first[:2]))
            records[year]=record
        return records,samples
    wanted=[n for n in config['networks'] if not only_new or n['id'] not in old]
    with ThreadPoolExecutor(3) as pool:
        futures=[(net,pool.submit(collect,net)) for net in wanted]
        for net,future in futures:
            try:
                records,samples=future.result();result[net['id']]=records;jobs.extend(samples)
                sources[net['id']]={'retrieved':now,'state':'ok'}
            except (ValueError,OSError) as error:
                failures.append(net['id'])
                sources[net['id']]={**sources.get(net['id'],{}),'state':'unavailable','checked_at':now}
                print(net['id']+': source unavailable ('+type(error).__name__+')')
    if failures and not only_new:raise ValueError('Source refresh incomplete; existing published edition preserved: '+', '.join(failures))
    with ThreadPoolExecutor(3) as pool:
        for item in pool.map(read_capture,jobs):
            if item:
                net,year,sample=item;result[net][year]['text']=sample
    if not result:raise ValueError('No genuine capture index is available')
    stamps=[r[k][0][:8] for records in result.values() for r in records.values() for k in ['first','last']]
    def iso(stamp):return stamp[:4]+'-'+stamp[4:6]+'-'+stamp[6:]
    status={'retrieved':oldstatus.get('retrieved') if only_new else now[:10], 'checked_at':now,'count':sum(y['count'] for series in result.values() for y in series.values()),'start':iso(min(stamps)),'end':iso(max(stamps)),'samples':sum('text' in y for v in result.values() for y in v.values()),'sources':sources,'configured_networks':len(config['networks']),'indexed_networks':len(result)}
    atomic_documents(out,{'captures.json':result,'status.json':status})
    print(json.dumps(status))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--new-only',action='store_true',help='Seed only new source profiles; preserve existing data and complete-refresh timestamp on failure')
    main(parser.parse_args().new_only)
