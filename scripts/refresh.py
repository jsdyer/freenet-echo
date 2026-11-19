"""Fetch exact-homepage capture metadata and text signals for selected dated captures."""
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
from html.parser import HTMLParser
import json,re,time
from pathlib import Path
from urllib.parse import urlencode,urlsplit
from urllib.request import Request,urlopen

ROOT=Path(__file__).resolve().parents[1]
HOME={'halifax':['www.chebucto.ns.ca/'],'vancouver':['www.vcn.bc.ca/','www2.vcn.bc.ca/'],'ottawa':['www.ncf.ca/','www.ncf.carleton.ca/','www.ncf.ca/en/']}
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
def captures(site):
    url='https://web.archive.org/cdx/search/cdx?'+urlencode([('url',site),('matchType','exact'),('output','json'),('filter','statuscode:200'),('filter','mimetype:text/html'),('fl','timestamp,original,digest')])
    rows=json.loads(request(url,8_000_000)); expected=urlsplit('https://'+site)
    if not rows:return []
    if rows[0]!=['timestamp','original','digest']:raise ValueError('Unknown archive schema')
    valid=[]
    for stamp,orig,digest in rows[1:]:
        parsed=urlsplit(orig)
        if (parsed.hostname or '').lower().removeprefix('www.')!=expected.hostname.removeprefix('www.') or parsed.path.rstrip('/')!=expected.path.rstrip('/') or parsed.query:continue
        if re.fullmatch(r'\d{14}',stamp) and parsed.scheme in ('http','https'):valid.append((stamp,orig,digest))
    return valid
def read_capture(args):
    network,year,stamp,orig=args
    try:
        html=request(replay(stamp+'id_',orig),2_000_000,14)
        doc=VisibleText();doc.feed(html.decode('utf-8',errors='replace'))
        body=' '.join(doc.text);title=' '.join(''.join(doc.name).split())
        if not title or 'wayback machine' in title.lower() or 'internal server error' in title.lower():return None
        return (network,year,dict(stamp=stamp,url=orig,title=title[:180],mentions=[k for k,p in SERVICES.items() if re.search(p,body,re.I)]))
    except (ValueError,OSError):return None

def main():
    out=ROOT/'web/data';path=out/'captures.json'
    old=json.loads(path.read_text()) if path.exists() else {}
    inputs=[(net,url)for net,hosts in HOME.items()for url in hosts]
    with ThreadPoolExecutor(3) as pool:slices=list(pool.map(captures,[url for _,url in inputs]))
    result={}; jobs=[];dates=[]
    for net,hosts in HOME.items():
        rows=set()
        for (key,_),part in zip(inputs,slices):
            if key==net:rows.update(part)
        years=defaultdict(list)
        for stamp,url,digest in sorted(rows):
            years[stamp[:4]].append((stamp,url,digest));dates.append(stamp[:8])
        if len(years)<5:raise ValueError('Insufficient homepage history for '+net)
        result[net]={}
        for year,group in years.items():
            first,last=group[0],group[-1]
            record={'count':len(group),'versions':len({digest for _,_,digest in group if digest!='-'}),'first':first[:2],'last':last[:2]}
            existing=old.get(net,{}).get(year,{}).get('text')
            if existing and existing['stamp']==first[0]:record['text']=existing
            elif year in {min(years),max(years),'2000','2005','2010','2015','2020','2025'}:jobs.append((net,year,*first[:2]))
            result[net][year]=record
    with ThreadPoolExecutor(4) as pool:
        for item in pool.map(read_capture,jobs):
            if item:
                net,year,sample=item;result[net][year]['text']=sample
    def iso(s):return s[:4]+'-'+s[4:6]+'-'+s[6:]
    status={'retrieved':datetime.now(timezone.utc).date().isoformat(),'count':sum(y['count']for series in result.values()for y in series.values()),'start':iso(min(dates)),'end':iso(max(dates)),'samples':sum('text'in y for v in result.values()for y in v.values())}
    for name,doc in [('captures',result),('status',status)]: (out/(name+'.json')).write_text(json.dumps(doc,ensure_ascii=False,separators=(',',':'))+'\n')
    print(status)
if __name__=='__main__':main()
