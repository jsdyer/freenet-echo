export const NETWORKS={
 halifax:{name:'Chebucto Community Net',city:'Halifax',scope:'chebucto.ns.ca/',source:'https://chebucto.ns.ca/Chebucto/Membership/history.html',history:[
  ['Summer 1993','Organizers began meeting at the Halifax Library.'],['October 1993','Chebucto began operating on a loaned Sun SPARCstation 2.'],['June 16, 1994','Chebucto opened to the public.']]},
 vancouver:{name:'Vancouver Community Network',city:'Vancouver',scope:'vcn.bc.ca/ and www2.vcn.bc.ca/',source:'https://www.vcn.bc.ca/volnet/int.htm',history:[
  ['1993','The organization began as Vancouver FreeNet.'],['1994','VCN began offering online services.'],['By 1996','The network had moved to a web-based information system and offered web hosting and support for community groups.']]},
 ottawa:{name:'National Capital FreeNet',city:'Ottawa',scope:'ncf.carleton.ca/, ncf.ca/ and ncf.ca/en/',source:'https://www.ncf.ca/ncf/freeport2html/papers/history.html',history:[
  ['November 1991','The organizing project began at Carleton University.'],['September 1992','Donated modems and communications equipment connected the Ottawa Public Library.'],['February 1, 1993','The public opening took place at the regional headquarters in Ottawa.']]}
};
export function archiveLink(pair){return 'https://web.archive.org/web/'+pair[0]+'/'+pair[1];}
export function displayStamp(s){return s.slice(0,4)+'-'+s.slice(4,6)+'-'+s.slice(6,8)+' '+s.slice(8,10)+':'+s.slice(10,12)+' UTC';}
export function previousText(years,year){const older=Object.keys(years).filter(k=>k<year&&years[k].text).sort();return older.length?years[older.at(-1)].text:null;}
export function changes(now,prior){return {added:now.filter(x=>!prior.includes(x)),removed:prior.filter(x=>!now.includes(x))};}
