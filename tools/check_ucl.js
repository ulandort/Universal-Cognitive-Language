/* Independent JavaScript subset semantic validator for UCL inner packets.
   Does not import Python source. Validates definitions, type checking, discussion
   graph, acknowledgement targets, 4-layer declaration, and content hashes.
   Limitations: not a complete proof/model interpreter, no Brotli here.
*/
const fs=require('fs'), crypto=require('crypto');
function fail(s){throw Error(s)};
function assert(x,s){if(!x)fail(s)}
function parseUclJson(raw){
 const text=new TextDecoder('utf-8',{fatal:true,ignoreBOM:true}).decode(raw);
 const whitespace=/[ \t\r\n]*/y;
 const scalar=/(?:true|false|null|-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?)/y;
 let offset=0;
 function skipWhitespace(){
  whitespace.lastIndex=offset;
  whitespace.exec(text);
  offset=whitespace.lastIndex;
 }
 function take(char){
  skipWhitespace();
  if(text[offset]!==char)return false;
  offset++;
  return true;
 }
 function stringEnd(){
  assert(text[offset]==='"','expected JSON string');
  offset++;
  while(offset<text.length){
   const char=text[offset++];
   if(char==='"')return;
   if(char==='\\')offset++;
  }
  fail('unterminated JSON string');
 }
 function value(depth){
  assert(depth<=128,'canonical nesting');
  skipWhitespace();
  if(take('{')){
   const keys=new Set();
   if(take('}'))return;
   do{
    skipWhitespace();
    const start=offset;
    stringEnd();
    const key=JSON.parse(text.slice(start,offset));
    assert(!keys.has(key),'duplicate JSON key');
    keys.add(key);
    assert(take(':'),'expected JSON colon');
    value(depth+1);
   }while(take(','));
   assert(take('}'),'expected end of JSON object');
  }else if(take('[')){
   if(take(']'))return;
   do{value(depth+1);}while(take(','));
   assert(take(']'),'expected end of JSON array');
  }else if(text[offset]==='"'){
   stringEnd();
  }else{
   scalar.lastIndex=offset;
   const token=scalar.exec(text)?.[0];
   assert(token,'expected JSON value');
   if(token!=='true'&&token!=='false'&&token!=='null'){
    assert(!/[.eE]/.test(token)&&Number.isSafeInteger(Number(token)),'noninteger or unsafe JSON number');
   }
   offset=scalar.lastIndex;
  }
 }
 value(0);
 skipWhitespace();
 assert(offset===text.length,'trailing JSON data');
 return JSON.parse(text);
}
function asciiEscape(s){
  assert(typeof s==='string','JSON string type');
  for(let i=0;i<s.length;i++){
    const x=s.charCodeAt(i);
    if(x>=0xD800&&x<=0xDBFF){assert(i+1<s.length,'unpaired surrogate');const y=s.charCodeAt(i+1);assert(y>=0xDC00&&y<=0xDFFF,'unpaired surrogate');i++;}
    else assert(!(x>=0xDC00&&x<=0xDFFF),'unpaired surrogate');
  }
  return JSON.stringify(s).replace(/[\u007f-\uffff]/g,c=>'\\u'+c.charCodeAt(0).toString(16).padStart(4,'0'));
}
function cpCompare(a,b){let A=Array.from(a,c=>c.codePointAt(0)), B=Array.from(b,c=>c.codePointAt(0));for(let i=0;i<Math.min(A.length,B.length);i++)if(A[i]!==B[i])return A[i]-B[i];return A.length-B.length}
function canonical(v,depth=0){
 assert(depth<=128,'canonical nesting');
 if(v===null)return 'null';
 if(typeof v==='string')return asciiEscape(v);
 if(typeof v==='number'){assert(Number.isSafeInteger(v),'noninteger or unsafe number');return JSON.stringify(v)}
 if(typeof v==='boolean')return JSON.stringify(v);
 if(Array.isArray(v))return '['+v.map(z=>canonical(z,depth+1)).join(',')+']';
 if(typeof v==='object')return '{'+Object.keys(v).sort(cpCompare).map(k=>asciiEscape(k)+':'+canonical(v[k],depth+1)).join(',')+'}';
 fail('nonjson');
}
function hash(prefix,v){return crypto.createHash('sha256').update(prefix).update(canonical(v)).digest('base64url')}
const CORE={'@':2,'#':0,'=':2,'~':-1,'&':2,'|':2,'!':1,'?':1,'<':3,'*':-1,'{':3};
const RESERVED=new Set(' @ # = ~ & | ! ? < * { : ; [ ] -'.trim().split(' '));
const NAMED_ALIAS=/^\$[A-Za-z][A-Za-z0-9_]{0,63}/;
function layers(body){let out=[],depth=0,start=0;for(let i=0;i<body.length;i++){if(body[i]==='[')depth++;if(body[i]===']')depth--;assert(depth>=0,'brackets');if(body[i]===';'&&depth===0){out.push(body.slice(start,i));start=i+1}}out.push(body.slice(start));assert(depth===0&&out.length===4,'layers');return out.map(x=>{assert(x[0]=='['&&x.at(-1)==']','outer layers');return x.slice(1,-1)})}
function semantic(packet,{archived=false}={}){
 const defs=packet.definitions, domains=packet.domains;
 const retractable=['UCL/1.3','UCL/1.4'].includes(packet.guide.version);
 const long=retractable||['UCL/1.2','UCL/1.2-DRAFT'].includes(packet.guide.version);
 const dependent=long||packet.guide.version==='UCL/1.1';
 const recordsLimit=long?8192:150;
 assert(dependent||packet.guide.version==='UCL/1.0','inner version');
 assert(Object.keys(defs).length>=1&&Object.keys(defs).length<=(dependent?512:55),'definition count');
 const ids=new Set();
 for(const [g,rec] of Object.entries(defs)){
  const single=g.length===1&&!RESERVED.has(g)&&g.charCodeAt(0)>=33&&g.charCodeAt(0)<=126;
  assert(single||(dependent&&g.match(NAMED_ALIAS)?.[0]===g),'bad glyph');
  assert(!ids.has(rec.id),'duplicate id');ids.add(rec.id);
  const d=rec.definition;assert(typeof d.gloss==='string'&&d.gloss.length>0,'gloss');
  const fields={orientation:['kind','role','gloss'],domain:['kind','role','gloss'],value:['kind','sort','denotes','gloss'],predicate:['kind','args','gloss'],function:['kind','args','returns','gloss'],order:['kind','sort','role','gloss'],acknowledgement:['kind','role','gloss']}[d.kind];
  assert(fields&&canonical(Object.keys(d).sort())===canonical(fields.sort()),'definition fields');
 }
 for(const [g,rec] of Object.entries(defs)){
  const d=rec.definition;
  if(d.kind==='value')assert(defs[d.sort]?.definition.kind==='domain','value sort');
  if(['predicate','function'].includes(d.kind)){
   assert(Array.isArray(d.args)&&d.args.every(s=>defs[s]?.definition.kind==='domain'),'signature args');
   if(d.kind==='function')assert(defs[d.returns]?.definition.kind==='domain','signature output');
  }
  if(d.kind==='order')assert(defs[d.sort]?.definition.kind==='domain','ordering sort');
 }
 assert(canonical(Object.keys(domains).sort())===canonical(Object.keys(defs).filter(g=>defs[g].definition.kind==='domain').sort()),'domain set');
 const domainIds=new Map();
 if(dependent){
  for(const [alias, declaration] of Object.entries(domains)){
   assert(declaration&&canonical(Object.keys(declaration).sort())===canonical(['members','mode']),'domain declaration shape');
   const {mode,members}=declaration;
   assert(mode==='open'?members===null:mode==='finite'&&Array.isArray(members)&&
    members.every(member=>typeof member==='string')&&new Set(members).size===members.length,'domain membership');
   const domain={mode,members:members===null?null:members.slice().sort(cpCompare)};
   domainIds.set(alias,hash('UCL-SEM-10\n',{definition:defs[alias].definition,domain}));
  }
 }
 for(const [alias,rec] of Object.entries(defs)){
  let expected;
  if(!dependent)expected=hash('UCL-SEM-9\n',rec.definition);
  else if(domainIds.has(alias))expected=domainIds.get(alias);
  else{
   const definition={...rec.definition};
   for(const field of ['sort','returns']){
    if(Object.hasOwn(definition,field))definition[field]=domainIds.get(definition[field]);
   }
   if(Object.hasOwn(definition,'args'))definition.args=definition.args.map(sort=>domainIds.get(sort));
   expected=hash('UCL-SEM-10\n',{definition});
  }
  assert(rec.id===expected,'definition hash '+alias);
 }
 let used=new Set();const src=layers(packet.body);let domainSet=new Set(Object.keys(domains));
 function parse(s,occurrences){let i=0;function one(scope={},depth=0){assert(depth<120,'depth');assert(i<s.length,'eof');
  const name=s[i]==='$'?NAMED_ALIAS.exec(s.slice(i)):null;
  const g=name?name[0]:s[i];i+=g.length;used.add(g);occurrences?.add(g);
  if(g==='#'){const m=/^(0|[1-9][0-9]*)/.exec(s.slice(i));assert(m,'variable');i+=m[0].length;assert(scope[m[0]]!==undefined,'unbound');return scope[m[0]];}
  if(defs[g]){const d=defs[g].definition;return d.kind==='value'?d.sort:d.kind;}
  assert(Object.hasOwn(CORE,g),'operator');function arg(sc=scope){assert(s[i++]==='[','argument opening');let typ=one(sc,depth+1);assert(s[i++ ]===']','argument closing');return typ}
  if(g==='{'){assert(s[i++]==='[','binder');assert(s[i++]==='#','binder glyph');used.add('#');const m=/^(0|[1-9][0-9]*)/.exec(s.slice(i));assert(m,'binder name');i+=m[0].length;assert(s[i++]===']','binder close');assert(scope[m[0]]===undefined,'shadow');let domStart=i,dom=arg();assert(dom==='domain','binder domain');let bracket=s.slice(domStart,i);let glyph=bracket.slice(1,-1);assert(domainSet.has(glyph),'domain glyph');let nScope={...scope,[m[0]]:glyph};assert(arg(nScope)==='prop','body prop');return 'prop'}
  if(g==='~'||g==='*'){assert(s[i]==='[','sig opening');const start=i+1;const typ=arg();const glyph=s.slice(start,i-1);assert(typ===(g==='~'?'predicate':'function'),'signature kind');const d=defs[glyph].definition;for(const t of d.args)assert(arg()===t,'typed arg');return g==='~'?'prop':d.returns;}
  if(g==='@'){let a=arg();assert(s[i]==='[','domain ar');const begin=i+1;let b=arg();const glyph=s.slice(begin,i-1);assert(b==='domain'&&a===glyph,'membership sort');return 'prop'}
  if(g==='='){let a=arg(),b=arg();assert(a===b&&domainSet.has(a),'identity sort');return 'prop'}
  if(g==='<'){assert(s[i]==='[','order arg');const begin=i+1;assert(arg()==='order','order needed');const glyph=s.slice(begin,i-1);const sort=defs[glyph].definition.sort;assert(arg()===sort&&arg()===sort,'order terms');return 'prop'}
  if(g==='&'||g==='|'){assert(arg()==='prop'&&arg()==='prop','bool types');return 'prop'}
  if(g==='!'){assert(arg()==='prop','negation prop');return 'prop'}
  if(g==='?'){assert(arg()==='prop','epistemic prop');return 'epistemic'}
  fail('operator '+g);
 }let r=one();assert(i===s.length,'trailing');return r;}
 assert(parse(src[0])==='orientation','orientation');assert(parse(src[1])==='prop','explanation');assert(['prop','epistemic'].includes(parse(src[2])),'conclusion');
 const acts=packet.discourse.acts;assert(acts.length>=1&&(archived&&long||acts.length<=(long?4096:100)),'act count');let seen=new Map();
 const actIndex=new Map(acts.map((act,index)=>[act.id,index]));
 for(const a of acts){assert(!seen.has(a.id),'duplicate act');assert(typeof a.text==='string'&&a.text.length>0,'act text');assert(typeof a.speaker==='string'&&a.speaker.length>0&&a.speaker.length<=120,'speaker');assert(a.references.every(r=>seen.has(r)),'references');for(const e of a.expressions)assert(['prop','epistemic'].includes(parse(e)),'act expression');const d=a.details;
  if(a.kind==='challenge')assert(d.disputes.length>0&&d.disputes.every(x=>seen.has(x)),'challenge refs');
  if(a.kind==='revision')assert(seen.has(d.revises),'revision ref');
  if(a.kind==='response')assert(seen.has(d.responds_to),'response ref');
  if(a.kind==='clarification')assert(seen.has(d.about),'clarification ref');
  if(a.kind==='synthesis')assert(d.integrates.length>0&&d.integrates.every(x=>seen.has(x)),'synthesis refs');
  if(a.kind==='conditional'){assert(parse(d.antecedent)==='prop','conditional ante');assert(d.consequents.length>0&&d.consequents.every(x=>parse(x)==='prop'),'conditional consequents');}
  if(a.kind==='analogy')assert(d.mappings.length>0&&typeof d.limits==='string'&&d.limits.length>0,'analogy');
  if(Object.hasOwn(a,'vocabulary')){
   assert(dependent&&Array.isArray(a.vocabulary)&&a.vocabulary.length>=1&&a.vocabulary.length<=16,'vocabulary entry list');
   const entries=new Set();
   for(const entry of a.vocabulary){
    assert(entry&&typeof entry.definition==='string'&&Object.hasOwn(defs,entry.definition),'vocabulary definition alias');
    const {action,definition}=entry;
    used.add(definition);
    let key=definition;
    if(action==='retire'){
     assert(Object.keys(entry).sort().join(',')==='action,definition,successor','retirement fields');
     const successor=entry.successor;
     assert(successor===null||(typeof successor==='string'&&successor!==definition&&Object.hasOwn(defs,successor)),'retirement successor');
     if(successor!==null)used.add(successor);
    }else{
     assert(['example','counterexample'].includes(action)&&Object.keys(entry).sort().join(',')==='action,definition,expression_index','vocabulary example fields');
     const index=entry.expression_index;
     assert(Number.isInteger(index)&&index>=0&&index<a.expressions.length,'vocabulary example expression index');
     const occurrences=new Set();
     parse(a.expressions[index],occurrences);
     assert(occurrences.has(definition),'vocabulary example expression must use its definition');
     key+=':'+index;
    }
    assert(!entries.has(key),'duplicate vocabulary entry');
    entries.add(key);
   }
  }
  seen.set(a.id,a);
 }
 assert(packet.discourse.current===acts.at(-1).id,'current act');
 assert(Array.isArray(packet.acknowledgements)&&(archived&&long||packet.acknowledgements.length<=recordsLimit),'acknowledgement count');
 const indexedAcks=new Map(), retractedAcks=new Set();
 for(const a of packet.acknowledgements){
  assert(a&&typeof a.id==='string'&&/^[A-Za-z][A-Za-z0-9_-]{0,63}$/.test(a.id)&&!indexedAcks.has(a.id),'duplicate or invalid ACK ID');
  indexedAcks.set(a.id,a);
 }
 for(const a of packet.acknowledgements){
  const author=seen.get(a.by);assert(author,'ack author');
  const t=a.target;assert(t&&typeof t==='object'&&!Array.isArray(t),'ack target');
  if(a.action==='retract'){
   assert(retractable,'ACK retraction requires UCL/1.3 or later');
   assert(Object.keys(a).sort().join(',')==='action,by,id,note,qualification,replacement,target','retraction fields');
   assert(Object.keys(t).join(',')==='ack'&&typeof t.ack==='string','retraction target');
   const original=indexedAcks.get(t.ack);
   assert(original&&['accept','reject','qualify','adopt-for-discussion','withhold-judgment'].includes(original.action),'retraction must target a stance ACK');
   assert(actIndex.get(original.by)<actIndex.get(a.by),'retraction must target an ACK from an earlier act');
   assert(seen.get(original.by).speaker===author.speaker,'retraction ownership');
   assert(!retractedAcks.has(t.ack),'ACK already retracted');
   assert(a.qualification===null&&a.replacement===null&&typeof a.note==='string'&&[...a.note].length<=2048,'retraction payload');
   retractedAcks.add(t.ack);
   continue;
  }
  let dest;
  if(Object.keys(t).sort().join(',')==='act,expression_index'){
   dest=t.act;const target=seen.get(dest);assert(target,'ack refs');
   assert(t.expression_index===null||(Number.isInteger(t.expression_index)&&t.expression_index>=0&&t.expression_index<target.expressions.length),'expression index');
  }else if(Object.keys(t).sort().join(',')==='claim,path'){
   const bound=packet.claims[t.claim];assert(bound,'ack claim reference');
   dest=bound.act;const target=seen.get(dest);
   assert(target&&target.expressions[bound.expression_index]===bound.expression,'ack claim binding');
   assert(Array.isArray(t.path)&&t.path.length<=32&&t.path.every(i=>Number.isInteger(i)&&i>=0&&i<=15),'ack path');
   // Validate a path by structural bracket parsing, independently of Python's AST.
   let fragment=bound.expression;
   for(const idx of t.path){
     const children=[];let pos=1;
     if(fragment[0]==='{'){
       const m=/^\{\[#(?:0|[1-9][0-9]*)\]/.exec(fragment);assert(m,'quantifier');pos=m[0].length;children.push(null);
     }
     while(pos<fragment.length){
       assert(fragment[pos]==='[','ack path child start');const begin=++pos;let depth=1;
       while(pos<fragment.length&&depth){if(fragment[pos]==='[')depth++;else if(fragment[pos]===']')depth--;pos++}
       assert(depth===0,'ack path brackets');children.push(fragment.slice(begin,pos-1));
     }
     assert(idx<children.length&&typeof children[idx]==='string','ack path range');fragment=children[idx];
     assert(fragment.length>0,'ack path empty');
   }
   assert((fragment.includes('#') && /^[~@=<!&|?{]/.test(fragment)) || ['prop','epistemic'].includes(parse(fragment)),'ack path must resolve to proposition');
  }else fail('ack target shape');
  assert(actIndex.get(dest)<actIndex.get(author.id),'ack temporal');
  if(a.action==='withdraw')assert(author.speaker===seen.get(dest).speaker,'withdraw ownership');
  const builtins=new Set(['received','understood','accept','reject','qualify','clarify','propose-revision','adopt-for-discussion','withhold-judgment','withdraw']);
  assert(builtins.has(a.action)||(typeof a.action==='string'&&a.action.startsWith('ext:')),'unknown acknowledgement action');
  if(a.action==='qualify')assert(a.qualification!==null,'qualify needs condition');
  if(typeof a.action==='string'&&a.action.startsWith('ext:')){let g=a.action.slice(4);assert(defs[g]?.definition.kind==='acknowledgement','ext ack');used.add(g)}
  if(a.qualification&&typeof a.qualification==='object')assert(parse(a.qualification.expression)==='prop','typed qualifier');
 }
 const claims=packet.claims, viewpointList=packet.viewpoints;
 assert(claims&&typeof claims==='object'&&!Array.isArray(claims)&&Object.keys(claims).length<=recordsLimit,'claims shape');
 for(const [id,c] of Object.entries(claims)){
  assert(/^[A-Za-z][A-Za-z0-9_-]{0,63}$/.test(id),'claim ID');
  assert(c && Object.keys(c).sort().join(',')==='act,expression,expression_index','claim fields');
  const origin=seen.get(c.act);
  assert(origin&&Number.isInteger(c.expression_index)&&c.expression_index>=0&&c.expression_index<origin.expressions.length,'claim origin');
  assert(c.expression===origin.expressions[c.expression_index],'quote exact binding');
  assert(['prop','epistemic'].includes(parse(c.expression)),'quoted type');
 }
 assert(Array.isArray(viewpointList)&&viewpointList.length<=recordsLimit,'viewpoints shape');
 const viewpoints=new Map();
 for(const v of viewpointList){
  assert(Object.keys(v).sort().join(',')==='holder,id,relation,reported_by,source_act,target','viewpoint fields');
  assert(/^[A-Za-z][A-Za-z0-9_-]{0,63}$/.test(v.id)&&!viewpoints.has(v.id),'viewpoint ID');
  assert(['asserts','believes','reports','questions','denies'].includes(v.relation),'viewpoint relation');
  const origin=seen.get(v.source_act);
  assert(origin&&typeof v.holder==='string'&&v.holder.length>0&&v.reported_by===origin.speaker,'viewpoint speaker/source');
  assert(v.target&&Object.keys(v.target).sort().join(',')==='id,kind','viewpoint target shape');
  if(v.target.kind==='claim'){
   assert(Object.hasOwn(claims,v.target.id),'claim target missing');
   assert(actIndex.get(claims[v.target.id].act)<=actIndex.get(v.source_act),'future claim reference');
  }else if(v.target.kind==='viewpoint'){
   assert(viewpoints.has(v.target.id),'viewpoint cycle/forward');
   assert(actIndex.get(viewpoints.get(v.target.id).source_act)<=actIndex.get(v.source_act),'future viewpoint ref');
  }else fail('viewpoint target kind');
  if(v.relation==='asserts')assert(v.holder===origin.speaker&&v.target.kind==='claim'&&claims[v.target.id].act===v.source_act,'assertion source ownership');
  viewpoints.set(v.id,v);
 }
 const hist=packet.history;assert(['fully-expanded','condensed'].includes(hist.status),'history mode');
 assert(typeof hist.summary==='string'&&hist.summary.trim()&&typeof hist.scope==='string'&&hist.scope.trim(),'history summary/scope');
 assert(Array.isArray(hist.omissions),'omission structure');
 assert(hist.status==='condensed'?hist.omissions.length>0:hist.omissions.length===0,'history omission disclosure');
 const decl=[...used].map(g=>Object.hasOwn(CORE,g)?g:g+':'+defs[g].id).sort().join(' ');
 assert(src[3]===decl,'exact symbol declaration');
 assert(packet.integrity.sha256===hash('UCL-PACKET-7\n',Object.fromEntries(Object.entries(packet).filter(([k])=>k!=='integrity'))),'packet hash');
 return {valid:true,acts:acts.length,acknowledgements:packet.acknowledgements.length,definitions:Object.keys(defs).length,mode:packet.history.status,claims:Object.keys(claims).length,viewpoints:viewpoints.size};
}
if(require.main===module)try{
 const raw=fs.readFileSync(process.argv[2]), p=parseUclJson(raw);
 const cb=canonical(p);
 assert(Buffer.from(cb).equals(raw),'input must already use exact UCL-CJSON-1 canonical bytes');
 if(process.argv[3]==='--canonical'){process.stdout.write(cb);}
 else process.stdout.write(JSON.stringify(semantic(p))+'\n');
}catch(e){console.error('INVALID:',e.message);process.exit(1)}

// Allow independent offline UCL/2.0 Portable wrappers to reuse this JS checker.
module.exports={canonical,hash,parseUclJson,semantic};
