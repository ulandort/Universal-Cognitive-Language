#!/usr/bin/env node
/* Independent offline UCL SAP-1 Portable verifier.
   No registry, network, Python runtime, npm modules or cloud dependencies.
   Checks outer guide fingerprint, authenticated-by-trust-anchor rules identity,
   envelope SHA-256, the typed packet through an independent JS checker,
   and optional FR-1 annotations. A checksum is NOT a digital signature.
*/
'use strict';
const fs=require('fs');
const {canonical,hash,semantic}=require('./check_ucl.js');
const {createHash}=require('node:crypto');
const {gunzipSync,inflateRawSync}=require('node:zlib');
const RULE_DOMAIN='UCL-SAP1-RULES-2.0\n';
const ENVELOPE_DOMAIN='UCL-SAP1-ENVELOPE-2.0\n';
const VERSIONS=new Map([
 ['UCL/2.0-SAP1-PORTABLE',{
  rules:'yrac3Zj4lyiGfI6944ZsmFSLdL-VPiXPnVZEPVKEh-k',
  guide:'ZFIZCtsxvrSp7PH12QlsH2re08Xd_kS78JKFunwYO_M',
 }],
 ['UCL/2.1-SAP1-PORTABLE',{
  rules:'IwfCnyR6owRSz6XBEGi1er4u_4Zksy1DrlgyiB7XvmI',
  guide:'y9nzzEGsMLesvWT5qAyaugxXnlMCXHtuj3PweHvYFkc',
 }],
 ['UCL/2.2-SAP1-PORTABLE-DRAFT',{
  rules:'4u9lbsfKp11t9K_rsmO-bXneadKN5SCybC_bulnzDUE',
  guide:'pxkeIcZ2pxM3Rq1000KmzZpDa3941lAKNh6WYUlZz0I',
 }],
 ['UCL/2.2-SAP1-PORTABLE',{
  rules:'LQQIye-mjF8wKYpLdvEwzRLHBfVxnzyBPzBnkqi5LZc',
  guide:'OJq6wvk1iM4amrEhQsxzi-xBNt3tkRRL8NJEHnNTaIY',
 }],
]);
const ROLE_GUIDE=('FR-1 draft: act/index identifies an exact expression in packet.discourse.acts; '+
'role is an author-declared purpose (hypothesis, example, counterexample, '+
'quotation, question), NOT proof or truth. Missing role is unspecified. '+
'Never suppress original novel ideas.');
function requireThat(ok,msg){if(!ok)throw Error('SAP portable: '+msg)}
function keys(obj,required){return !!obj&&typeof obj==='object'&&!Array.isArray(obj)&&
  Object.keys(obj).length===required.length&&required.every(key=>Object.hasOwn(obj,key))}
function rawHash(bytes){return createHash('sha256').update(bytes).digest('base64url')}
function orderedSlots(slots,limit){
 return Array.isArray(slots)&&slots.every((slot,index)=>Number.isSafeInteger(slot)&&slot>=0&&slot<limit&&
  (index===0||slots[index-1]<slot));
}
function expandArchive(envelope){
 const {archive:a,packet:p}=envelope;
 const {acts:readable,current}=p.discourse;
 requireThat(keys(a,['codec','blocks','pinned','act_count','ack_count','readable_ack_slots'])&&
  a.codec==='gzip+base64url','archive metadata or codec');
 requireThat(typeof envelope.archive_guide==='string'&&
  rawHash(envelope.archive_guide)==='I5ii4bIUzldhadQm8YkY3MkPrn49NtCU5Lpw27O5HCc','archive guide');
 requireThat(Number.isSafeInteger(a.act_count)&&a.act_count>1000&&
  Number.isSafeInteger(a.ack_count)&&a.ack_count>=0,'archive counts');
 requireThat(Array.isArray(readable)&&readable.length>=1000&&readable.at(-1).id===current,'archive readable history');
 const readableIds=new Set(readable.map(act=>act.id));
 requireThat(readableIds.size===readable.length&&Array.isArray(a.pinned)&&
  a.pinned.every(id=>typeof id==='string'&&readableIds.has(id)),'archive pinned or readable IDs');
 requireThat(Array.isArray(a.blocks)&&a.blocks.length>0&&orderedSlots(a.readable_ack_slots,a.ack_count)&&
  a.readable_ack_slots.length===p.acknowledgements.length&&p.acknowledgements.every(ack=>readableIds.has(ack.by)),
  'archive block or readable ACK index');
 const actSlots=new Map(), archivedIds=new Set();
 const acks=new Map(a.readable_ack_slots.map((slot,index)=>[slot,p.acknowledgements[index]]));
 let end=-1, expandedBytes=0;
 for(const block of a.blocks){
  requireThat(keys(block,['act_ids','act_slots','expanded_bytes','sha256','data']),'archive block fields');
  const {act_slots:slots,act_ids:ids,expanded_bytes:size}=block;
  requireThat(orderedSlots(slots,a.act_count-1000)&&slots.length>=1&&slots.length<=1000&&
   slots[0]>end&&Math.floor(slots[0]/1000)===Math.floor(slots.at(-1)/1000),'archive block slots');
  end=slots.at(-1);
  requireThat(Array.isArray(ids)&&ids.length===slots.length&&Number.isSafeInteger(size)&&size>0&&size<=4_000_000,
   'archive block size or IDs');
  expandedBytes+=size;
  requireThat(expandedBytes<=96_000_000,'archive full-audit limit');
  const bytes=Buffer.from(block.data,'base64url');
  requireThat(bytes.toString('base64url')===block.data&&bytes.length>=18&&
   bytes.readUInt32BE(0)===0x1f8b0800,'archive gzip header');
  const raw=gunzipSync(bytes,{maxOutputLength:size});
  const deflate=bytes.subarray(10,-8);
  const member=inflateRawSync(deflate,{maxOutputLength:size,info:true});
  requireThat(member.engine.bytesWritten===deflate.length&&raw.length===size&&rawHash(raw)===block.sha256,
   'archive member length or SHA-256');
  const records=JSON.parse(raw.toString('utf8'));
  requireThat(keys(records,['acts','acknowledgements'])&&records.acts.length===slots.length&&
   Array.isArray(records.acknowledgements)&&Buffer.from(canonical(records)).equals(raw),'archive block records');
  const owners=new Set(ids);
  for(const [index,act] of records.acts.entries()){
   requireThat(typeof act.id==='string'&&act.id===ids[index]&&!readableIds.has(act.id)&&
    !archivedIds.has(act.id)&&!act.vocabulary,'archive act ID conflict or protected vocabulary');
   archivedIds.add(act.id);
   actSlots.set(slots[index],act);
  }
  for(const pair of records.acknowledgements){
   requireThat(Array.isArray(pair)&&pair.length===2,'archive ACK record');
   const [slot,ack]=pair;
   requireThat(Number.isSafeInteger(slot)&&slot>=0&&slot<a.ack_count&&!acks.has(slot)&&owners.has(ack.by)&&
    ['received','understood'].includes(ack.action),'archive ACK index or protected author');
   acks.set(slot,ack);
  }
 }
 requireThat(readable.length+actSlots.size===a.act_count&&acks.size===a.ack_count,'archive counts do not match');
 const protectedIds=[
  ...Object.values(p.claims).map(claim=>claim.act), ...p.viewpoints.map(view=>view.source_act),
  ...(envelope.formula_roles||[]).map(role=>role.act), ...readable.slice(-1000).flatMap(act=>act.references),
 ];
 for(const ack of p.acknowledgements){
  if(['received','understood'].includes(ack.action))continue;
  if(Object.hasOwn(ack.target,'act'))protectedIds.push(ack.target.act);
  if(ack.replacement!==null)protectedIds.push(ack.replacement);
 }
 requireThat(protectedIds.every(id=>readableIds.has(id)),'archive hides a protected source');
 let next=0;
 const acts=Array.from({length:a.act_count},(_,slot)=>actSlots.get(slot)??readable[next++]);
 return {...p,discourse:{...p.discourse,acts},acknowledgements:Array.from({length:a.ack_count},(_,slot)=>acks.get(slot))};
}
function validate(envelope){
 requireThat(!!envelope&&typeof envelope==='object'&&!Array.isArray(envelope),'envelope must be object');
 const base=['format','profile','structural_rules','packet','checksum'];
 const archived=Object.hasOwn(envelope,'archive');
 if(archived)base.push('archive_guide','archive');
 const extended=[...base,'formula_roles','formula_role_guide'];
 requireThat(keys(envelope,base)||keys(envelope,extended),'envelope fields invalid');
 const pinned=VERSIONS.get(envelope.format);
 requireThat(pinned&&envelope.profile==='portable','unsupported profile');
 requireThat(!archived||['UCL/2.2-SAP1-PORTABLE','UCL/2.2-SAP1-PORTABLE-DRAFT'].includes(envelope.format),'archive requires Portable 2.2');
 const block=envelope.structural_rules;
 requireThat(keys(block,['rules','sha256']),'rules block invalid');
 requireThat(typeof block.sha256==='string'&&block.sha256===hash(RULE_DOMAIN,block.rules),'rules hash mismatch');
 requireThat(block.sha256===pinned.rules,'unknown or altered structural standard');
 const {checksum,...body}=envelope;
 requireThat(typeof checksum==='string'&&checksum===hash(ENVELOPE_DOMAIN,body),'envelope checksum mismatch');
 let packet=envelope.packet;
 requireThat(keys(packet,['guide','definitions','domains','model','proof','context','body',
  'links','revisions','discourse','acknowledgements','history','claims','viewpoints','integrity']),
  'inner packet field shape');
 requireThat(packet.guide&&typeof packet.guide==='object'&&!Array.isArray(packet.guide),
  'embedded inner guide missing');
 requireThat(hash('UCL-GUIDE-PIN-2\n',packet.guide)===pinned.guide,
  'unknown or altered inner language guide');
 if(archived)packet=expandArchive(envelope);
 const checked=semantic(packet,{archived});
 if(Object.hasOwn(envelope,'formula_roles')){
   requireThat(envelope.formula_role_guide===ROLE_GUIDE,'role guide mismatch');
   const roles=envelope.formula_roles;
   requireThat(Array.isArray(roles)&&roles.length<=512,'invalid role array');
   const acts=new Map(packet.discourse.acts.map(a=>[a.id,a]));
   const allowed=new Set(['hypothesis','example','counterexample','quotation','question']);
   const seen=new Set();
   for(const item of roles){
     requireThat(keys(item,['act','index','role']),'invalid role object');
     requireThat(acts.has(item.act),'role act not retained');
     const formulas=acts.get(item.act).expressions;
     requireThat(Number.isSafeInteger(item.index)&&item.index>=0&&item.index<formulas.length,
      'role index out of range');
     requireThat(allowed.has(item.role),'unknown role');
     const key=item.act+'\0'+item.index;
     requireThat(!seen.has(key),'duplicate role');
     seen.add(key);
   }
 }
 return {valid:true,format:envelope.format,packet_sha256:packet.integrity.sha256,
   rules_sha256:block.sha256,discourse_acts:checked.acts,
   acknowledgements:checked.acknowledgements,definitions:checked.definitions};
}
if(require.main===module){
 try{
   if(process.argv.length!==3)throw Error('Usage: node tools/check_ucl_portable.js packet.txt');
   const source=process.argv[2];
   const maxBytes=8_000_000;
   requireThat(fs.statSync(source).size<=maxBytes,'envelope too large');
   const raw=fs.readFileSync(source,'utf8');
   requireThat(Buffer.byteLength(raw,'utf8')<=maxBytes,'envelope too large');
   process.stdout.write(JSON.stringify(validate(JSON.parse(raw)))+'\n');
 }catch(e){console.error('INVALID:',e.message);process.exitCode=1}
}
module.exports={validate};
