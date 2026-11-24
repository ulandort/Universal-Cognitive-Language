#!/usr/bin/env node
/* Independent offline UCL SAP-1 Portable verifier.
   No registry, network, Python runtime, npm modules or cloud dependencies.
   Checks outer guide fingerprint, authenticated-by-trust-anchor rules identity,
   envelope SHA-256, original UCL 1.0 packet through independent JS checker,
   and optional FR-1 annotations. A checksum is NOT a digital signature.
*/
'use strict';
const fs=require('fs');
const {hash,semantic}=require('./check_ucl.js');
const RULE_DOMAIN='UCL-SAP1-RULES-2.0\n';
const ENVELOPE_DOMAIN='UCL-SAP1-ENVELOPE-2.0\n';
const VERSIONS=new Map([
 ['UCL/2.0-SAP1-PORTABLE',{
  rules:'yrac3Zj4lyiGfI6944ZsmFSLdL-VPiXPnVZEPVKEh-k',
  guide:'ZFIZCtsxvrSp7PH12QlsH2re08Xd_kS78JKFunwYO_M',
 }],
 ['UCL/2.1-SAP1-PORTABLE',{
  rules:'JJC_P_4nhysFsB-1YOY-m3pWtJR8IBCloH06b4eOsE4',
  guide:'gwOP2P5TdHQ7ZY92znMm80KFUnN6HJEKxUuyfCWdVKs',
 }],
]);
const ROLE_GUIDE=('FR-1 draft: act/index identifies an exact expression in packet.discourse.acts; '+
'role is an author-declared purpose (hypothesis, example, counterexample, '+
'quotation, question), NOT proof or truth. Missing role is unspecified. '+
'Never suppress original novel ideas.');
function requireThat(ok,msg){if(!ok)throw Error('SAP portable: '+msg)}
function keys(obj,required){return !!obj&&typeof obj==='object'&&!Array.isArray(obj)&&
  Object.keys(obj).sort().join(',')===required.slice().sort().join(',')}
function validate(envelope){
 requireThat(!!envelope&&typeof envelope==='object'&&!Array.isArray(envelope),'envelope must be object');
 const base=['format','profile','structural_rules','packet','checksum'];
 const extended=[...base,'formula_roles','formula_role_guide'];
 requireThat(keys(envelope,base)||keys(envelope,extended),'envelope fields invalid');
 const pinned=VERSIONS.get(envelope.format);
 requireThat(pinned&&envelope.profile==='portable','unsupported profile');
 const block=envelope.structural_rules;
 requireThat(keys(block,['rules','sha256']),'rules block invalid');
 requireThat(typeof block.sha256==='string'&&block.sha256===hash(RULE_DOMAIN,block.rules),'rules hash mismatch');
 requireThat(block.sha256===pinned.rules,'unknown or altered structural standard');
 const {checksum,...body}=envelope;
 requireThat(typeof checksum==='string'&&checksum===hash(ENVELOPE_DOMAIN,body),'envelope checksum mismatch');
 const packet=envelope.packet;
 requireThat(keys(packet,['guide','definitions','domains','model','proof','context','body',
  'links','revisions','discourse','acknowledgements','history','claims','viewpoints','integrity']),
  'inner packet field shape');
 requireThat(packet.guide&&typeof packet.guide==='object'&&!Array.isArray(packet.guide),
  'embedded inner guide missing');
 requireThat(hash('UCL-GUIDE-PIN-2\n',packet.guide)===pinned.guide,
  'unknown or altered inner language guide');
 const checked=semantic(packet);
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
   const raw=fs.readFileSync(process.argv[2],'utf8');
   requireThat(Buffer.byteLength(raw,'utf8')<=1_000_000,'envelope too large');
   process.stdout.write(JSON.stringify(validate(JSON.parse(raw)))+'\n');
 }catch(e){console.error('INVALID:',e.message);process.exitCode=1}
}
module.exports={validate};
