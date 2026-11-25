export function archiveLink(pair){return 'https://web.archive.org/web/'+pair[0]+'/'+pair[1];}
export function displayStamp(s){return s.slice(0,4)+'-'+s.slice(4,6)+'-'+s.slice(6,8)+' '+s.slice(8,10)+':'+s.slice(10,12)+' UTC';}
export function previousText(years,year){const older=Object.keys(years).filter(k=>k<year&&years[k].text).sort();return older.length?years[older.at(-1)].text:null;}
export function changes(now,prior){return {added:now.filter(x=>!prior.includes(x)),removed:prior.filter(x=>!now.includes(x))};}

export function networkIndex(config){
 if(!Array.isArray(config?.networks)||!config.networks.length)throw Error('No configured networks');
 const output={};
 for(const n of config.networks){
  if(!/^[a-z0-9-]+$/.test(n.id)||output[n.id]||!n.name||!Array.isArray(n.homepages)||!n.homepages.length)throw Error('Invalid network configuration');
  output[n.id]=n;
 }
 return output;
}
export function nearestCapture(records,year){
 const pairs=Object.values(records||{}).flatMap(r=>[r.first,r.last]).filter(Boolean);
 const wanted=Date.UTC(Number(year),0,1);
 return pairs.sort((a,b)=>Math.abs(Date.parse(displayStamp(a[0]).slice(0,10))-wanted)-Math.abs(Date.parse(displayStamp(b[0]).slice(0,10))-wanted)||a[0].localeCompare(b[0]))[0]||null;
}
export function normalizeHost(input){
 const u=new URL(/^[a-z]+:\/\//i.test(input.trim())?input.trim():'https://'+input.trim());
 if(!['http:','https:'].includes(u.protocol)||u.username||u.password||u.port||!/^([a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z][a-z0-9-]*$/i.test(u.hostname))throw Error('Enter a public domain, such as vcn.bc.ca.');
 return u.hostname;
}
