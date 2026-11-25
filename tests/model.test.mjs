import test from 'node:test';import assert from 'node:assert/strict';import {previousText,changes,archiveLink,displayStamp} from '../web/model.mjs';
test('Service comparison uses earlier reviewed samples',()=>{const d={'2001':{text:{mentions:['email']}},'2002':{},'2003':{text:{mentions:['telnet']}}};assert.equal(previousText(d,'2001'),null);assert.deepEqual(changes(d['2003'].text.mentions,previousText(d,'2003').mentions),{added:['telnet'],removed:['email']});});
test('Preserve the complete replay address and UTC timestamp',()=>{assert.equal(archiveLink(['20000502030405','http://vcn.bc.ca:80/']),'https://web.archive.org/web/20000502030405/http://vcn.bc.ca:80/');assert.equal(displayStamp('20000502030405'),'2000-05-02 03:04 UTC');});

import {networkIndex,nearestCapture,normalizeHost} from '../web/model.mjs';
import {readFileSync} from 'node:fs';
test('an extra configured network is picked up without changing application code',()=>{
 const config=JSON.parse(readFileSync(new URL('../web/config.json',import.meta.url)));
 config.networks.push({id:'test-net',name:'Another community network',homepages:['example.ca/']});
 assert.equal(networkIndex(config)['test-net'].name,'Another community network');
 assert.throws(()=>networkIndex({networks:[config.networks[0],config.networks[0]]}));
});
test('milestone links use a real saved capture, with deterministic nearest-date selection',()=>{
 const records={'1998':{first:['19980101000000','http://example.ca/'],last:['19981231000000','http://example.ca/']},'2000':{first:['20000201000000','http://example.ca/'],last:['20000301000000','http://example.ca/']}};
 assert.deepEqual(nearestCapture(records,'1999'),records['1998'].last);assert.equal(nearestCapture({},'1999'),null);
});
test('custom archive links accept extra public domains and reject credentials or local addresses',()=>{
 assert.equal(normalizeHost('https://WWW.Example.ca/a'),'www.example.ca');
 for(const v of ['localhost','https://u:p@example.ca/','192.0.2.1','https://example.ca:8443/'])assert.throws(()=>normalizeHost(v));
});
