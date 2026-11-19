import {$,el,num,select,load,fail,link} from './ui.mjs';
import {NETWORKS,archiveLink,displayStamp,previousText,changes} from './model.mjs';
let captures={},years=[];
function card(id,year){
 const net=NETWORKS[id],records=captures[id],yearly=records[year],box=el('article',undefined,'card');
 box.append(el('p',net.city+' · '+year,'meta'),el('h2',net.name));
 if(!yearly){box.append(el('p','No indexed capture for this year.'));return box;}
 box.append(el('p',num(yearly.count)+' captures','metric'),el('p',num(yearly.versions)+' distinct archived content digests'));
 const links=el('p');links.append(link('First · '+displayStamp(yearly.first[0]),archiveLink(yearly.first)));
 if(yearly.first[0]!==yearly.last[0])links.append(el('br'),link('Last · '+displayStamp(yearly.last[0]),archiveLink(yearly.last)));
 box.append(links);
 if(yearly.text){
  const t=yearly.text;box.append(el('h3','From the captured homepage'),el('p',t.title),el('p',t.mentions.length?'Service terms found: '+t.mentions.join(', ')+'.':'None of the indexed service terms appeared in the extracted text.'));
  const prev=previousText(records,year);
  if(prev){
   const diff=changes(t.mentions,prev.mentions);
   const cmp=el('p');cmp.append('Compared with ',link(displayStamp(prev.stamp),archiveLink([prev.stamp,prev.url])),'. ');
   if(diff.added.length)cmp.append('Newly mentioned: '+diff.added.join(', ')+'. ');
   if(diff.removed.length)cmp.append('Previously mentioned only: '+diff.removed.join(', ')+'.');
   if(!diff.added.length&&!diff.removed.length)cmp.append('The two samples contain the same indexed service terms.');
   box.append(cmp);
  }
 } else box.append(el('p','Text comparison is unavailable for this year. Open a capture to inspect its contents.'));
 return box;
}
function render(){
 const left=$('left').value,right=$('right').value,year=$('year').value;
 const pair=[...new Set([left,right])];$('cards').replaceChildren(...pair.map(id=>card(id,year)));
 const head=el('tr');head.append(el('th','Year'),...pair.map(id=>el('th',NETWORKS[id].city)));$('head').replaceChildren(head);
 const max=Math.max(...years.flatMap(y=>pair.map(id=>captures[id][y]?.count||0)));
 $('rows').replaceChildren(...years.map(y=>{
  const tr=el('tr');if(y===year)tr.className='chosen';const td=el('th'),button=el('button',y,'link');button.onclick=()=>{$('year').value=y;render();$('year').focus();};td.append(button);tr.append(td);
  for(const id of pair){const v=captures[id][y],cell=el('td',v?num(v.count):'—');if(v){const bar=el('span',undefined,'bar');bar.style.width=(v.count/max*100)+'%';cell.append(bar);}tr.append(cell);}return tr;
 }));
 const blocks=pair.map(id=>{const net=NETWORKS[id],section=el('section'),ul=el('ul');ul.append(...net.history.map(([d,v])=>el('li',d+' · '+v)));section.append(el('h3',net.name),ul,link('Read the network’s history ↗',net.source));return section;});
 $('history').replaceChildren(...blocks);$('scope').textContent=Object.values(NETWORKS).map(n=>n.city+' · '+n.scope).join(' | ')+'. Hostnames with or without www are included.';
 const url=new URL(location.href);for(const id of ['left','right','year'])url.searchParams.set(id,$(id).value);history.replaceState(null,'',url);
}
async function start(){
 const [data,s]=await Promise.all([load('captures'),load('status')]);captures=data;
 years=[...new Set(Object.values(data).flatMap(x=>Object.keys(x)))].sort();
 for(const id of ['left','right'])select(id,Object.entries(NETWORKS).map(([id,n])=>[id,n.city+' · '+n.name]));
 select('year',years.map(y=>[y,y]));const q=new URLSearchParams(location.search);
 $('left').value=Object.hasOwn(NETWORKS,q.get('left'))?q.get('left'):'halifax';$('right').value=Object.hasOwn(NETWORKS,q.get('right'))?q.get('right'):'vancouver';$('year').value=years.includes(q.get('year'))?q.get('year'):'2000';
 $('status').textContent=num(s.count)+' indexed captures · '+s.start+' – '+s.end+' · '+s.samples+' homepage text samples · Retrieved '+s.retrieved;
 for(const id of ['left','right','year'])$(id).onchange=render;render();
}
start().catch(fail);
