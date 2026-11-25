#!/usr/bin/env python3
"""Internal typed UCL grammar and validated packet engine, reused unchanged by UCL/2.0.
Optional proof certificates and open speculative conversation remain separate.
Not a complete first-order theorem prover or security audit.
"""
import base64, hashlib, json, re, sys
from pathlib import Path

VERSION='UCL/1.0'
DEPENDENCY_VERSION='UCL/1.1'
LONG_VERSION='UCL/1.2'
LONG_DRAFT_VERSION='UCL/1.2-DRAFT'
RETRACTION_VERSION='UCL/1.3'
CURRENT_VERSION='UCL/1.4'
RETRACTION_VERSIONS=(RETRACTION_VERSION, CURRENT_VERSION)
LONG_VERSIONS=(LONG_VERSION, LONG_DRAFT_VERSION, *RETRACTION_VERSIONS)
DEPENDENCY_VERSIONS=(DEPENDENCY_VERSION, *LONG_VERSIONS)
MAX_LONG_ACTS=4096
MAX_LONG_RECORDS=8192
DEPENDENCY_DOMAIN=b'UCL-SEM-10\n'
MAX_DEFINITIONS=512
NAMED_ALIAS=re.compile(r'\$[A-Za-z][A-Za-z0-9_]{0,63}')
SEM_DOMAIN=b'UCL-SEM-9\n'; PACK_DOMAIN=b'UCL-PACKET-7\n'
CORE={'@':['membership',2],'#':['bound-reference',0],'=':['identity',2],
      '~':['predicate-application','signature'],'&':['and',2],'|':['or',2],
      '!':['not',1],'?':['epistemic',1],'<':['named-strict-order',3],
      '*':['function-application','signature'],'{':['exists-in-domain',3]}
STRUCT={':':-1,';':-2,'[':-3,']':-4,'-':-5}
RESERVED=set(CORE)|set(STRUCT)
START='BEGIN_UCL_PAYLOAD\n'; END='\nEND_UCL_PAYLOAD'
MAX_COMPRESSED=250000; MAX_EXPANDED=1000000; MAX_DEPTH=120
MAX_MODEL_WORK=1_000_000

def need(ok,msg):
    if not ok: raise ValueError(msg)
def _canonical_check(value, depth=0):
    need(depth <= 128, 'canonical data nesting limit')
    if value is None or type(value) is bool: return
    if type(value) is int:
        need(-(2**53-1) <= value <= 2**53-1, 'integer outside interoperable safe range')
        return
    if type(value) is str:
        need(not any(0xD800 <= ord(c) <= 0xDFFF for c in value),'unpaired surrogate is forbidden')
        return
    if type(value) is list:
        for v in value: _canonical_check(v,depth+1)
        return
    if type(value) is dict:
        for k,v in value.items():
            need(type(k) is str, 'JSON keys must be strings')
            _canonical_check(k,depth+1);_canonical_check(v,depth+1)
        return
    raise ValueError('canonical profile allows integers, booleans, strings, null, arrays and objects; fractional numbers must be decimal strings')

def canon(x):
    # UCL-CJSON-1: ASCII JSON, scalar-value code-point key ordering, safe integers only.
    # Fractional quantities such as confidence are canonical decimal strings.
    _canonical_check(x)
    return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode('ascii')

def b64(b): return base64.urlsafe_b64encode(b).rstrip(b'=').decode('ascii')
def unb64(s):
    need(isinstance(s,str) and re.fullmatch(r'[A-Za-z0-9_-]+',s) and len(s)%4!=1,'bad base64url')
    try: out=base64.urlsafe_b64decode(s+'='*((-len(s))%4))
    except Exception as e: raise ValueError('bad base64url') from e
    need(b64(out)==s,'noncanonical base64url');return out
def definition_id(d):return b64(hashlib.sha256(SEM_DOMAIN+canon(d)).digest())
def packet_id(p):return b64(hashlib.sha256(PACK_DOMAIN+canon({k:v for k,v in p.items() if k!='integrity'})).digest())

def guide(version=VERSION):
    need(version in (VERSION, *DEPENDENCY_VERSIONS), 'unknown inner guide version')
    result = {'version':VERSION,'core':CORE,'structural':STRUCT,
      'grammar':'Four body layers: [orientation];[explanation];[conclusion];[exact-symbol-declaration]. Prefix expressions; {[#N][domain][prop] exists; universal via negated existential. <[order][a][b] requires named order.',
      'domain':'Declared domain may have finite members or open symbolic population (including infinite or unspecified). Model evaluation enumerates finite only; open domains are not enumerated or assumed empty.',
      'equality':'Identity of denotation, not resemblance. Term interpretation is deterministic and typed.',
      'ordering':'Explicit named strict partial order. Each order definition has a sort; multiple orders may coexist on that sort. Irreflexivity and transitivity checked in finite interpretations.',
      'functions':'Total deterministic typed function for finite model checking; symbolic function terms allowed in proof certificates; no causation implied.',
      'epistemic':'?[prop] is a sourced epistemic record of uncertainty or conflict, never missing data; epistemic type is not Boolean. Records carry assessor, evidence references, basis, optional confidence [0,1].',
      'claims':'Conversation is valid without a proof or model. Claims can be speculative, false, challenged or revised. An optional proof certificate checks entailment relative to explicit premises. A model-check intent evaluates one finite stipulated interpretation. An epistemic report documents uncertainty/conflict, not mere missing information.',
      'proof':'Optional attached certificate (not required for conversation): premises from top-level explanation conjuncts; and-elim-left/right, and-intro, modus-ponens for |[![P]][Q], direct copy, equality reflexivity. Certificate may be invalid/unsupported without invalidating the message. Steps reference earlier indices; final formula must equal claim conclusion. No unrestricted proof or empirical truth.',
      'hashing':'Definition: SHA256(UCL-SEM-9 newline + UCL-CJSON-1); packet: SHA256(UCL-PACKET-7 newline + UCL-CJSON-1 excluding integrity). Full 256-bit unpadded Base64url. No signature/authentication.',
      'canonicalization':'UCL-CJSON-1: ASCII-escaped compact JSON, sort object keys by Unicode scalar code points, forbid surrogate code points, finite JSON numeric values must be integers in safe 53-bit range; represent fractions such as confidence as exact decimal strings. Recompute and compare canonical bytes. Cross-language test vectors are normative; this is not RFC8785.',
      'limits':'<=250KB compressed, <=1MB expanded, <=120 parse depth, <=55 definitions, <=256 proof steps, <=8 function arguments, <=100 discourse acts, <=24KB per act, <=150 acknowledgements, <=100 omission notes, finite models <=10000 tuple products per function.',
      'stability':'UCL/1.0 freezes this exact UCL-CJSON-1 profile; future incompatible changes require a new protocol version.',
      'intents':'Orientation declares conversational act: proposal, hypothesis, question, challenge, response, revision, assertion, deductive-argument, model-check, epistemic-report. No proof required for ordinary acts.',
      'discourse':'Each message includes a self-contained ordered act graph with explicit speaker, act kind, target references, optional typed expressions and act-specific structured details. Questions, analogies, conditional scenarios, revisions, and multi-claim exchanges are valid unproven communications. Act edges are structural, NOT evidence of truth, provenance authenticity, or valid analogy. Current act kind must agree with orientation.',
      'definitions':'Definitions carry immutable hash identities; any revision uses a new glyph+identity, preserves old full definition, and records reason. Receiver must follow normative meaning literally, reveal ambiguity rather than silently reinterpret.',
      'certification':'The message validity result is independent of proof status (not-requested, verified, invalid-proof, unsupported, inconsistent-premises, undetermined). No proof failure blocks a syntactically valid message.',
      'acknowledgements':'Optional structured acknowledgements bind a speaker act to a retained earlier act, indexed formal expression, or exactly quoted claim with a validated path of proposition subexpressions. Understanding and endorsement differ. Withdrawal requires original speaker; revisions preserve original claims. New action meanings can be formally declared as immutable acknowledgement-kind extensions with action ext:<glyph>; their ids are included in the exact used-symbol declaration. Conditional qualifications may use a typed UCL proposition plus optional prose; they are not automatically assumed true.',
      'quotation':'Optional claims bind proposition expressions exactly to IDs and retained origin acts. Viewpoints are acyclic nested attributions (asserts/believes/reports/questions), not proofs of belief or truth. Quoted propositions participate in exact-symbol declarations.',
      'history':'All packets are standalone. history.status is fully-expanded or condensed. Condensed mode MUST disclose non-expanded earlier history, the omitted scope and nature, a meaningful summary, and any unresolved uncertainties. Complete active semantic definitions and all locally referenced acts remain present; no external registry, URL, prior packet or hidden alias may be necessary. A condensed summary is not a verbatim record. Optional reference hashes do not restore missing evidence.'}

    if version in DEPENDENCY_VERSIONS:
        result.update(
            version=version,
            hashing=(
                'Definition ID: full unpadded Base64url SHA256 of UCL-SEM-10 plus LF and '
                'UCL-CJSON-1 of {"definition": normalized_definition}. Replace sort, args entries, and '
                'returns aliases by their domain IDs wherever present. A domain adds "domain": '
                '{"mode": mode, "members": members} to that payload; sort finite members by Unicode '
                'scalar value and use null members for open domains. Packet hashing remains '
                'SHA256 of UCL-PACKET-7 plus LF and canonical packet excluding integrity. '
                'Checksums do not authenticate speakers.'
            ),
            limits=result['limits'].replace('<=55 definitions', '<=512 definitions'),
            grammar=result['grammar'] + (
                ' A named alias is $ followed by an ASCII letter and up to 63 ASCII letters, digits '
                'or underscores, e.g. ~[$background_sync][A]. Consume the full name at an expression '
                'boundary. A lone $ can remain a single-character alias. The declaration uses '
                'alias:id tokens separated by spaces.'
            ),
            stability='UCL/1.1 retains the 11 core operators and UCL-CJSON-1; definition IDs bind their domain dependencies.',
            definitions=(
                'Definitions have immutable IDs. Single-character and named aliases are local to the packet; '
                'typed dependencies bind to domain IDs, including the domain declaration. '
                'Use a fresh alias when introducing a changed definition and preserve the old one.'
            ),
            vocabulary=(
                'An act may include vocabulary, a list of 1 to 16 records. '
                'A retirement is {"action":"retire","definition":"alias","successor":null} '
                "or names a different existing alias as successor. It records that speaker's retirement "
                'stance only. Every earlier binding remains usable and resolves to the same ID. '
                'An example or counterexample is {"action":"example","definition":"alias","expression_index":0} '
                'with action example or counterexample. The indexed expression in this act must use the alias. '
                'Records are attributed to the act speaker and do not change definition IDs or certify truth. '
                'Declare referenced vocabulary aliases and successors in the exact symbol layer.'
            ),
        )
    if version in LONG_VERSIONS:
        result['limits'] = result['limits'].replace('<=1MB expanded', '<=8MB Portable JSON in the CLI').replace(
            '<=100 discourse acts', f'<= {MAX_LONG_ACTS} discourse acts').replace(
            '<=150 acknowledgements', f'<= {MAX_LONG_RECORDS} each of acknowledgements, claims, and viewpoints')
        result['stability'] = (
            'UCL/1.2-DRAFT tests larger retained histories and preserves UCL/1.1 definition IDs.'
            if version == LONG_DRAFT_VERSION else
            'UCL/1.2 supports larger histories and optional Portable gzip archives. Definition IDs preserve the UCL/1.1 scheme.'
        )
    if version in RETRACTION_VERSIONS:
        result['stability'] = 'UCL/1.3 adds exact acknowledgement retraction and preserves UCL/1.2 definition IDs.'
        result['acknowledgements'] += (
            ' To retract your own earlier accept, reject, qualify, adopt-for-discussion or withhold-judgment ACK, '
            'set action to "retract" and target to {"ack":"EARLIER_ACK_ID"}. The original ACK must be authored '
            'by an earlier act with the same speaker label and may be retracted once. Set qualification and '
            'replacement to null. If this was the latest stance at its exact target, it is now retracted '
            'and no older stance resumes. A newer stance remains in effect. Both ACKs remain in the file.'
        )
    if version == CURRENT_VERSION:
        result['stability'] = 'UCL/1.4 adds a typed reply example and preserves UCL/1.3 definition IDs and act semantics.'
        result['reply_authoring'] = {
            'instructions': (
                'Use typed UCL formulas in explanation and conclusion. Put prose reasoning in act.text '
                'and cite retained turn IDs in act.references. Turn IDs and words from prose are not formula symbols. '
                'Use the symbols defined in the packet or explicitly add typed definitions. The local '
                'template --seed-formula option can copy a selected proposition for editing. Run preflight before continuing.'
            ),
            'example': {
                'assumes': 'A is a value and B is a predicate accepting its sort. The packet retains act t1.',
                'explanation': '~[B][A]',
                'conclusion': '~[B][A]',
                'act': {'text': 'The earlier observation is relevant to whether A has B.', 'references': ['t1']},
            },
        }
    return result

def packet_version(packet):
    need(isinstance(packet, dict), 'packet schema')
    header = packet.get('guide')
    version = header.get('version') if isinstance(header, dict) else None
    need(version in (VERSION, *DEPENDENCY_VERSIONS) and header == guide(version), 'guide mismatch')
    return version

def _definition_ids(defs, domains, version):
    if version == VERSION:
        return {glyph: definition_id(record['definition']) for glyph, record in defs.items()}

    ids = {}
    for glyph, declaration in domains.items():
        members = declaration['members']
        payload = {
            'definition': defs[glyph]['definition'],
            'domain': {'mode': declaration['mode'], 'members': sorted(members) if members is not None else None},
        }
        ids[glyph] = b64(hashlib.sha256(DEPENDENCY_DOMAIN + canon(payload)).digest())
    for glyph, record in defs.items():
        if glyph in domains:
            continue
        normalized = record['definition'].copy()
        for field in ('sort', 'returns'):
            if field in normalized:
                normalized[field] = ids[normalized[field]]
        if 'args' in normalized:
            normalized['args'] = [ids[alias] for alias in normalized['args']]
        ids[glyph] = b64(hashlib.sha256(DEPENDENCY_DOMAIN + canon({'definition': normalized})).digest())
    return ids

def layers(body):
    need(isinstance(body,str) and body.isascii(),'body must be ASCII')
    out=[]; depth=0; start=0
    for i,c in enumerate(body):
        if c=='[':depth+=1
        elif c==']': depth-=1;need(depth>=0,'unbalanced body')
        elif c==';' and depth==0:out.append(body[start:i]);start=i+1
    out.append(body[start:]);need(depth==0 and len(out)==4,'four layers required')
    need(all(z.startswith('[') and z.endswith(']') for z in out),'layer delimiters')
    return [z[1:-1] for z in out]

class Parser:
    def __init__(self,defs): self.defs=defs;self.used=set()
    def parse(self,source):
        used = set()
        domains = {g for g, record in self.defs.items() if record['definition']['kind'] == 'domain'}

        def expr(i,scope,depth):
            need(depth<MAX_DEPTH,'expression too deep');need(i<len(source),'missing expression')
            g = source[i]
            name = NAMED_ALIAS.match(source, i) if g == '$' else None
            if name:
                g = name.group()
            i += len(g)
            used.add(g)
            if g=='#':
                m=re.match(r'(0|[1-9][0-9]*)',source[i:]);need(m,'bad variable')
                idx=int(m.group());need(idx in scope,'unbound variable')
                return ('#',scope[idx],idx),i+len(m.group())
            if g in self.defs:
                d=self.defs[g]['definition'];t=d['sort'] if d['kind']=='value' else d['kind']
                return (g,t,()),i
            need(g in CORE,'unknown operator '+g)
            def arg(i,scope):
                need(i<len(source) and source[i]=='[','expected [')
                x,j=expr(i+1,scope,depth+1)
                need(j<len(source) and source[j]==']','expected ]')
                return x,j+1
            if g=='{':
                need(i<len(source) and source[i]=='[','binder [')
                m=re.match(r'#(0|[1-9][0-9]*)\]',source[i+1:]);need(m,'binder #N]')
                idx=int(m.group(1));need(idx not in scope,'variable shadowing')
                used.add('#');i=i+1+len(m.group())
                dom,i=arg(i,scope);need(dom[1]=='domain','binder domain')
                bound=dict(scope);bound[idx]=dom[0]
                body,i=arg(i,bound);need(body[1]=='prop','quantified proposition type')
                return ('{','prop',(idx,dom,body)),i
            if g in ('~','*'):
                sig,i=arg(i,scope)
                want='predicate' if g=='~' else 'function';need(sig[1]==want,'signature kind')
                d=self.defs[sig[0]]['definition'];args=[]
                for sort in d['args']:
                    a,i=arg(i,scope);need(a[1]==sort,'argument type mismatch');args.append(a)
                return (g,'prop' if g=='~' else d['returns'],(sig,*args)),i
            if g=='@':
                a,i=arg(i,scope);d,i=arg(i,scope)
                need(d[1]=='domain' and a[1]==d[0],'domain membership type')
                return (g,'prop',(a,d)),i
            if g=='=':
                a,i=arg(i,scope);b,i=arg(i,scope)
                need(a[1]==b[1] and a[1] in domains,'equality sort')
                return (g,'prop',(a,b)),i
            if g=='<':
                o,i=arg(i,scope);a,i=arg(i,scope);b,i=arg(i,scope)
                need(o[1]=='order','named order required')
                sort=self.defs[o[0]]['definition']['sort'];need(a[1]==sort and b[1]==sort,'order sort mismatch')
                return (g,'prop',(o,a,b)),i
            if g in ('&','|'):
                a,i=arg(i,scope);b,i=arg(i,scope)
                need(a[1]=='prop' and b[1]=='prop','boolean operands must be propositions')
                return (g,'prop',(a,b)),i
            if g in ('!','?'):
                a,i=arg(i,scope);need(a[1]=='prop','unary operand must be proposition')
                return (g,'epistemic' if g=='?' else 'prop',(a,)),i
            raise ValueError('unimplemented operation')
        tree, end = expr(0, {}, 0)
        need(end == len(source), 'trailing expression')
        self.domains = domains
        self.used.update(used)
        return tree

def render(t):
    g,typ,args=t
    if g=='#':return '#'+str(args)
    if not args:return g
    if g=='{':return '{[#'+str(args[0])+']['+render(args[1])+']['+render(args[2])+']'
    return g+''.join('['+render(a)+']' for a in args)

def conjuncts(t):return conjuncts(t[2][0])+conjuncts(t[2][1]) if t[0]=='&' else [t]

def _validate_definition_shapes(defs, version):
    limit = MAX_DEFINITIONS if version in DEPENDENCY_VERSIONS else 55
    need(isinstance(defs,dict) and 1<=len(defs)<=limit,'catalog size')
    for g,rec in defs.items():
        single = isinstance(g, str) and len(g) == 1 and 33 <= ord(g) <= 126 and g not in RESERVED
        named = version in DEPENDENCY_VERSIONS and isinstance(g, str) and NAMED_ALIAS.fullmatch(g)
        need(single or named, 'reserved/invalid extension glyph ' + repr(g))
        need(isinstance(rec,dict) and set(rec) in ({'definition'}, {'id','definition'}),'definition record')
        d=rec['definition'];need(isinstance(d,dict) and isinstance(d.get('gloss'),str) and d['gloss'],'definition gloss')
        kind=d.get('kind')
        signatures={'orientation':{'kind','role','gloss'},'domain':{'kind','role','gloss'},
          'value':{'kind','sort','denotes','gloss'},'predicate':{'kind','args','gloss'},
          'function':{'kind','args','returns','gloss'},'order':{'kind','sort','role','gloss'}, 'acknowledgement':{'kind','role','gloss'}}
        need(isinstance(kind, str) and kind in signatures and set(d)==signatures[kind],'definition signature')
    doms={g for g,v in defs.items() if v['definition']['kind']=='domain'}
    need(bool(doms),'at least one domain required')
    for g,r in defs.items():
        d=r['definition'];kind=d['kind']
        if kind=='value':need(isinstance(d['sort'], str) and d['sort'] in doms and isinstance(d['denotes'],str),'value sort/denotation')
        elif kind in ('predicate','function'):
            need(isinstance(d['args'],list) and len(d['args'])<=8 and all(isinstance(s, str) and s in doms for s in d['args']),'argument sorts')
            if kind=='function':need(isinstance(d['returns'], str) and d['returns'] in doms,'function return sort')
        elif kind=='order':need(isinstance(d['sort'], str) and d['sort'] in doms and isinstance(d['role'],str) and d['role'],'order signature')
        elif kind=='acknowledgement':need(isinstance(d['role'],str) and bool(d['role'].strip()),'acknowledgement extension role')
        elif kind=='orientation':need(d['role'] in ('proposal','hypothesis','question','challenge','response','revision','assertion','deductive-argument','model-check','epistemic-report'),'orientation role')
    return doms

def validate_defs(defs, domains=None, *, version=VERSION):
    domain_aliases = _validate_definition_shapes(defs, version)
    if version in DEPENDENCY_VERSIONS:
        validate_domains(defs, domains)
    expected = _definition_ids(defs, domains, version)
    for alias, record in defs.items():
        need(record.get('id') == expected[alias], 'definition SHA-256 mismatch ' + alias)
    need(len(set(expected.values())) == len(defs), 'duplicate definition identity')
    return domain_aliases

def validate_domains(defs,domains):
    domain_glyphs={g for g,x in defs.items() if x['definition']['kind']=='domain'}
    need(isinstance(domains,dict) and set(domains)==domain_glyphs,'complete domain declarations required')
    for g,d in domains.items():
        need(isinstance(d,dict) and set(d)=={'mode','members'},'domain declaration shape')
        need(d['mode'] in ('finite','open'),'domain mode')
        if d['mode']=='open':need(d['members'] is None,'open domains cannot be enumerated')
        else:need(isinstance(d['members'],list) and all(isinstance(x,str) for x in d['members']) and len(d['members'])==len(set(d['members'])),'finite domain members')
    for g,r in defs.items():
        d=r['definition']
        if d['kind']=='value' and domains[d['sort']]['mode']=='finite':
            need(d['denotes'] in domains[d['sort']]['members'],'constant not a member of finite domain')

class _ModelBudget:
    def __init__(self):
        self.remaining = MAX_MODEL_WORK

    def spend(self, units=1):
        self.remaining -= units
        need(self.remaining >= 0, 'finite model work budget exceeded')


def _decimal_confidence(value):
    return isinstance(value, str) and re.fullmatch(r'(?:0(?:\.[0-9]+)?|1(?:\.0+)?)', value) is not None


def validate_model(defs, domains, model, *, budget=None):
    budget = _ModelBudget() if budget is None else budget
    need(isinstance(model,dict) and set(model)=={'predicates','functions','orders','epistemic'},'model fields')
    need(all(d['mode']=='finite' for d in domains.values()),'open domain is not enumerable: use proof mode')
    kinds = {g: d['definition']['kind'] for g, d in defs.items()}
    for name, kind in (('predicates', 'predicate'), ('functions', 'function'), ('orders', 'order')):
        table = model[name]
        need(isinstance(table, dict) and set(table) == {g for g in kinds if kinds[g] == kind},
             kind + ' interpretation incomplete')

    budget.spend(sum(len(domain['members']) for domain in domains.values()))
    members = {g: set(domain['members']) for g, domain in domains.items()}

    def valid_tuple(row, signature):
        return (isinstance(row, list) and len(row) == len(signature)
                and all(isinstance(value, str) and value in members[sort]
                        for value, sort in zip(row, signature)))

    for g, rows in model['predicates'].items():
        signature = defs[g]['definition']['args']
        need(isinstance(rows, list), 'predicate rows')
        budget.spend(len(rows))
        need(all(valid_tuple(row, signature) for row in rows), 'predicate tuple invalid')
        need(len({tuple(row) for row in rows}) == len(rows), 'duplicate predicate tuple')

    for g, rows in model['functions'].items():
        definition = defs[g]['definition']
        need(isinstance(rows, list), 'function rows')
        count = 1
        for sort in definition['args']:
            count *= len(members[sort])
        need(count <= 10000, 'function table too large')
        budget.spend(len(rows))
        found = set()
        for row in rows:
            need(isinstance(row, dict) and set(row) == {'in', 'out'}, 'function row')
            args, result = row['in'], row['out']
            need(valid_tuple(args, definition['args']) and isinstance(result, str)
                 and result in members[definition['returns']], 'bad function tuple')
            key = tuple(args)
            need(key not in found, 'nondeterministic function')
            found.add(key)
        need(len(found) == count, 'function is not total')

    for g, edges in model['orders'].items():
        sort = defs[g]['definition']['sort']
        need(isinstance(edges, list), 'order rows')
        budget.spend(len(edges))
        successors = {}
        for edge in edges:
            need(valid_tuple(edge, (sort, sort)), 'order edge')
            source, dest = edge
            need(source != dest, 'strict order irreflexive')
            reachable = successors.setdefault(source, set())
            need(dest not in reachable, 'duplicate order edge')
            reachable.add(dest)
        for reachable in successors.values():
            for dest in reachable:
                onward = successors.get(dest)
                if onward:
                    budget.spend(len(onward))
                    need(onward <= reachable, 'strict order transitivity')

    need(isinstance(model['epistemic'],dict),'epistemic catalog')
    budget.spend(len(model['epistemic']))
    for statement,record in model['epistemic'].items():
        need(isinstance(statement,str) and isinstance(record,dict) and set(record)=={'kind','assessor','evidence','basis','confidence'},'epistemic record fields')
        need(record['kind'] in ('uncertainty','conflict'),'missing information cannot be marked ?')
        need(isinstance(record['assessor'],str) and bool(record['assessor']),'assessor required')
        need(isinstance(record['evidence'],list) and all(isinstance(e,str) and e for e in record['evidence']),'evidence reference list')
        need(isinstance(record['basis'],str) and bool(record['basis']),'uncertainty basis')
        confidence = record['confidence']
        need(confidence is None or (type(confidence) is int and confidence in (0, 1))
             or _decimal_confidence(confidence), 'confidence must be a decimal string in [0,1], null, or legacy integer 0 or 1')
        if record['kind']=='conflict':need(len(record['evidence'])>=2,'conflict requires at least two evidence references')


def evaluate(t, defs, domains, model, env=None, *, budget=None):
    budget = _ModelBudget() if budget is None else budget

    def walk(tree, bindings):
        budget.spend()
        op, _, args = tree
        if op == '#':
            return bindings[args]
        if op in defs:
            definition = defs[op]['definition']
            return definition['denotes'] if definition['kind'] == 'value' else op
        if op == '{':
            index, domain, body = args
            return any(walk(body, {**bindings, index: value}) for value in domains[domain[0]]['members'])
        if op in ('~', '*'):
            alias, *terms = args
            values = [walk(term, bindings) for term in terms]
            if op == '~':
                rows = model['predicates'][alias[0]]
                budget.spend(len(rows))
                return values in rows
            rows = model['functions'][alias[0]]
            budget.spend(len(rows))
            for row in rows:
                if row['in'] == values:
                    return row['out']
            raise ValueError('missing deterministic function value')
        if op == '@':
            member = walk(args[0], bindings)
            pool = domains[args[1][0]]['members']
            budget.spend(len(pool))
            return member in pool
        if op == '=':
            return walk(args[0], bindings) == walk(args[1], bindings)
        if op == '<':
            order, a, b = args
            pair = [walk(a, bindings), walk(b, bindings)]
            rows = model['orders'][order[0]]
            budget.spend(len(rows))
            return pair in rows
        if op == '&':
            return walk(args[0], bindings) and walk(args[1], bindings)
        if op == '|':
            return walk(args[0], bindings) or walk(args[1], bindings)
        if op == '!':
            return not walk(args[0], bindings)
        if op == '?':
            return model['epistemic'].get(render(args[0]))
        raise ValueError('unknown expression')

    return walk(t, {} if env is None else env)


def check_proof(explanation,conclusion,steps,defs):
    need(isinstance(steps,list) and 1<=len(steps)<=256,'proof certificate absent/too long')
    parser=Parser(defs);premises=conjuncts(explanation);proven=[]
    for i,step in enumerate(steps):
        need(isinstance(step,dict) and set(step)=={'rule','refs','formula'},'proof step fields')
        rule=step['rule'];refs=step['refs'];need(isinstance(refs,list) and all(type(r)==int and r>=0 for r in refs),'proof references')
        f=parser.parse(step['formula']);need(f[1]=='prop','proof formula must be proposition')
        if rule=='premise':
            need(len(refs)==1 and refs[0]<len(premises) and f==premises[refs[0]],'not an assumption in explanation')
        else:
            need(all(r<i for r in refs),'forward proof reference')
            if rule=='copy':need(len(refs)==1 and f==proven[refs[0]],'invalid copy')
            elif rule=='and-elim-left':
                need(len(refs)==1 and proven[refs[0]][0]=='&' and f==proven[refs[0]][2][0],'invalid and-elim-left')
            elif rule=='and-elim-right':
                need(len(refs)==1 and proven[refs[0]][0]=='&' and f==proven[refs[0]][2][1],'invalid and-elim-right')
            elif rule=='and-intro':
                need(len(refs)==2 and f==('&','prop',(proven[refs[0]],proven[refs[1]])),'invalid and-intro')
            elif rule=='modus-ponens':
                need(len(refs)==2,'modus ponens arity')
                a=proven[refs[0]];imp=proven[refs[1]]
                need(imp[0]=='|' and imp[2][0]==('!','prop',(a,)) and imp[2][1]==f,'invalid modus ponens')
            elif rule=='equality-reflexive':
                need(refs==[] and f[0]=='=' and f[2][0]==f[2][1],'invalid equality reflexivity')
            else:raise ValueError('unsupported proof rule: '+str(rule))
        proven.append(f)
    need(proven[-1]==conclusion,'proof last step is not conclusion')
    return {'steps':len(steps),'status':'valid derivation relative to stated premises; not empirical truth'}

# Open conversational discourse graph. This validates interpretability and reference hygiene,
# NEVER whether the speakers' claims, analogies, or proposed implications are true.
ACT_KINDS={'proposal','hypothesis','question','challenge','response','revision','assertion','deductive-argument','model-check','epistemic-report','conditional','analogy','synthesis','clarification'}

def _validate_vocabulary(entries, expressions, defs, parser):
    need(isinstance(entries, list) and 1 <= len(entries) <= 16, 'vocabulary entry list')
    seen = set()
    for entry in entries:
        need(isinstance(entry, dict), 'vocabulary entry object')
        action, alias = entry.get('action'), entry.get('definition')
        need(isinstance(alias, str) and alias in defs, 'vocabulary definition must name a declared alias')
        parser.used.add(alias)
        if action == 'retire':
            need(set(entry) == {'action', 'definition', 'successor'}, 'retirement fields')
            successor = entry['successor']
            need(successor is None or (isinstance(successor, str) and successor in defs and successor != alias),
                 'retirement successor must name a different declared alias')
            if successor is not None:
                parser.used.add(successor)
            key = (alias, None)
        else:
            need(action in ('example', 'counterexample') and
                 set(entry) == {'action', 'definition', 'expression_index'}, 'vocabulary example fields')
            index = entry['expression_index']
            need(type(index) is int and 0 <= index < len(expressions), 'vocabulary example expression index')
            example_parser = Parser(defs)
            example_parser.parse(expressions[index])
            need(alias in example_parser.used, 'vocabulary example expression must use its definition')
            key = (alias, index)
        need(key not in seen, 'duplicate vocabulary entry')
        seen.add(key)


def validate_discourse(discourse,defs,parser, *, version=VERSION, archived=False, prior_acts=()):
    need(isinstance(discourse,dict) and set(discourse)=={'current','acts'},'discourse schema')
    acts=discourse['acts']
    limit = MAX_LONG_ACTS if version in LONG_VERSIONS else 100
    need(isinstance(acts,list) and len(acts)>=1 and (archived and version in LONG_VERSIONS or len(prior_acts)+len(acts)<=limit),'discourse act cap')
    seen={act['id']:act['kind'] for act in prior_acts}; allowed_ans={'open','yes-no','multiple-choice'}
    def expression(s):
        need(isinstance(s,str) and 0<len(s)<=16000,'discourse expression length')
        expr=parser.parse(s)
        need(expr[1] in ('prop','epistemic'),'discourse expression must be proposition or epistemic')
        return expr
    def strs(v):
        need(isinstance(v,list) and len(v)<=24 and all(isinstance(x,str) and bool(x.strip()) and len(x)<=2048 for x in v),'discourse string list')
    def references(v):
        need(isinstance(v,list) and len(v)<=24 and all(isinstance(x,str) and x in seen for x in v),'missing or forward act reference')
    fields = {'id','speaker','kind','text','references','expressions','details'}
    allowed_fields = (fields, fields | {'vocabulary'}) if version in DEPENDENCY_VERSIONS else (fields,)
    for act in acts:
        need(isinstance(act,dict) and set(act) in allowed_fields,'act fields')
        a=act['id'];k=act['kind'];dt=act['details']
        need(isinstance(a,str) and re.fullmatch('[a-zA-Z][a-zA-Z0-9_-]{0,63}',a) and a not in seen,'act id collision')
        need(isinstance(k, str) and k in ACT_KINDS,'unsupported act kind')
        need(isinstance(act['speaker'],str) and 0<len(act['speaker'])<=120,'speaker required')
        need(isinstance(act['text'],str) and 0<len(act['text'])<=16000,'act text required')
        need(len(canon(act))<=24000,'act size cap')
        references(act['references'])
        need(isinstance(act['expressions'],list) and len(act['expressions'])<=16,'act expressions')
        for e in act['expressions']:expression(e)
        if 'vocabulary' in act:
            _validate_vocabulary(act['vocabulary'], act['expressions'], defs, parser)
        need(isinstance(dt,dict),'act details must be object')
        if k=='question':
            need(set(dt)=={'targets','answer_kind','alternatives'},'question details')
            strs(dt['targets']);need(bool(dt['targets']),'question targets needed')
            need(isinstance(dt['answer_kind'], str) and dt['answer_kind'] in allowed_ans,
                 'question answer kind')
            strs(dt['alternatives'])
            need((dt['answer_kind']=='multiple-choice')==(len(dt['alternatives'])>=2),'question alternatives')
        elif k=='challenge':
            need(set(dt)=={'disputes','scope'},'challenge details');references(dt['disputes'])
            need(bool(dt['disputes']) and dt['scope'] in ('premise','inference','definition','conclusion','other'),'challenge scope')
        elif k=='conditional':
            need(set(dt)=={'antecedent','consequents','status'},'conditional details')
            expression(dt['antecedent']);need(isinstance(dt['consequents'],list) and 1<=len(dt['consequents'])<=8,'conditional consequents')
            for e in dt['consequents']:expression(e)
            need(dt['status'] in ('proposed','asserted','questioned'),'conditional status')
        elif k=='analogy':
            need(set(dt)=={'mappings','limits'},'analogy details')
            need(isinstance(dt['mappings'],list) and 1<=len(dt['mappings'])<=16,'analogy mappings')
            for m in dt['mappings']:
                need(isinstance(m,dict) and set(m)=={'source','target','relation'} and all(isinstance(v,str) and 0<len(v)<=2048 for v in m.values()),'analogy mapping')
            need(isinstance(dt['limits'],str) and bool(dt['limits'].strip()),'analogy limits must be explicit')
        elif k=='revision':
            need(set(dt)=={'revises','change'},'revision details')
            need(isinstance(dt['revises'], str) and dt['revises'] in seen and isinstance(dt['change'],str) and bool(dt['change'].strip()),'revision target')
        elif k=='response':
            need(set(dt)=={'responds_to','stance'},'response details')
            need(isinstance(dt['responds_to'], str) and dt['responds_to'] in seen and dt['stance'] in ('accept','reject','mixed','undetermined'),'response target')
        elif k=='synthesis':
            need(set(dt)=={'integrates','open_questions'},'synthesis details');references(dt['integrates'])
            need(bool(dt['integrates']),'synthesis needs prior acts');strs(dt['open_questions'])
        elif k=='clarification':
            need(set(dt)=={'about','request'},'clarification details')
            need(isinstance(dt['about'], str) and dt['about'] in seen and isinstance(dt['request'],str) and bool(dt['request'].strip()),'clarification target')
        else:need(dt=={},'unexpected act details')
        seen[a]=k
    need(discourse['current']==acts[-1]['id'],'current must identify final act')
    return {'acts':len(acts),'kind':acts[-1]['kind']}

# Dialogue acknowledgements are optional metadata, not propositions, proofs or mandatory acts.
# Each target points to a retained act in this same packet; no external context may be required.
ACK_ACTIONS={'received','understood','accept','reject','qualify','clarify',
             'propose-revision','adopt-for-discussion','withhold-judgment','withdraw'}
RETRACTABLE_ACK_ACTIONS=frozenset({'accept','reject','qualify','adopt-for-discussion','withhold-judgment'})

def resolve_claim_path(parser, expression, path):
    tree = parser.parse(expression)
    for index in path:
        parts = tree[2]
        need(type(parts) is tuple and index < len(parts) and
             type(parts[index]) is tuple and len(parts[index]) == 3,
             'acknowledgement path not an expression node')
        tree = parts[index]
    need(tree[1] in ('prop', 'epistemic'),
         'acknowledgement subclaim must be a proposition or epistemic expression')
    return tree

def validate_acknowledgements(acks,discourse,defs,parser,claims, *, version=VERSION, archived=False, prior_acks=()):
    limit = MAX_LONG_RECORDS if version in LONG_VERSIONS else 150
    need(isinstance(acks,list) and (archived and version in LONG_VERSIONS or len(prior_acks)+len(acks)<=limit),'acknowledgement list size')
    acts=discourse['acts']; byid={a['id']:a for a in acts}
    positions={a['id']:i for i,a in enumerate(acts)}
    seen={ack['id'] for ack in prior_acks}
    if version in RETRACTION_VERSIONS:
        indexed = {ack['id']: ack for ack in prior_acks}
        indexed.update((ack['id'], ack) for ack in acks
                       if isinstance(ack, dict) and isinstance(ack.get('id'), str))
        retracted = {ack['target']['ack'] for ack in prior_acks if ack['action'] == 'retract'}
    for ack in acks:
        need(isinstance(ack,dict) and set(ack)=={'id','by','target','action','qualification','replacement','note'},'acknowledgement fields')
        ident=ack['id'];need(isinstance(ident,str) and re.fullmatch(r'[a-zA-Z][a-zA-Z0-9_-]{0,63}',ident) and ident not in seen,'duplicate/invalid acknowledgement ID')
        seen.add(ident)
        author=ack['by'];target=ack['target'];action=ack['action']
        need(isinstance(author, str) and author in byid,'acknowledgement author act absent')
        need(isinstance(target,dict),'acknowledgement target must be object')
        if action == 'retract':
            need(version in RETRACTION_VERSIONS, 'ACK retraction requires Portable 2.3 or later. Run upgrade first')
            need(set(target) == {'ack'} and isinstance(target['ack'], str),
                 'retraction target must be {"ack":"EARLIER_ACK_ID"}')
            original = indexed.get(target['ack'])
            need(original is not None and isinstance(original.get('action'), str)
                 and original['action'] in RETRACTABLE_ACK_ACTIONS,
                 'retraction must target an existing stance ACK')
            dest = original.get('by')
            need(isinstance(dest, str) and dest in positions and positions[dest] < positions[author],
                 'retraction must target an ACK from an earlier act')
            need(byid[author]['speaker'] == byid[dest]['speaker'], 'cannot retract another speaker’s ACK')
            need(target['ack'] not in retracted, 'ACK already retracted')
            need(ack['qualification'] is None and ack['replacement'] is None,
                 'retraction requires null qualification and replacement')
            need(isinstance(ack['note'], str) and len(ack['note']) <= 2048, 'acknowledgement note')
            retracted.add(target['ack'])
            continue
        if set(target)=={'act','expression_index'}:
            # Legacy act/whole-expression target remains available.
            dest=target['act'];need(isinstance(dest, str) and dest in byid,'acknowledgement target act missing')
            idx=target['expression_index']
            need(idx is None or (type(idx)==int and 0<=idx<len(byid[dest]['expressions'])),'acknowledgement expression target missing')
        elif set(target)=={'claim','path'}:
            # A stable claim binding and a zero-based path through its parsed proposition tree.
            cid=target['claim']
            need(isinstance(claims, dict) and isinstance(cid, str) and cid in claims,
                 'acknowledgement quoted claim absent')
            binding=claims[cid]
            need(isinstance(binding, dict) and set(binding)=={'act','expression_index','expression'},
                 'acknowledgement claim binding fields')
            dest=binding['act']
            need(isinstance(dest, str) and dest in byid and type(binding['expression_index']) is int and
                 0<=binding['expression_index']<len(byid[dest]['expressions']) and
                 binding['expression']==byid[dest]['expressions'][binding['expression_index']],
                 'acknowledgement claim binding not exact')
            path=target['path'];need(type(path) is list and len(path)<=32 and all(type(i) is int and 0<=i<=15 for i in path),'acknowledgement subclaim path invalid')
            resolve_claim_path(parser, binding['expression'], path)
            # The path identifies the exact subtree, not an unverified prose description.
        else:raise ValueError('acknowledgement target shape')
        need(positions[dest]<positions[author],'acknowledgement must target earlier retained act')
        if isinstance(action,str) and action.startswith('ext:'):
            glyph=action[4:]
            need(glyph in defs and defs[glyph]['definition']['kind']=='acknowledgement','unknown acknowledgement extension')
            parser.used.add(glyph)
        else:need(isinstance(action, str) and action in ACK_ACTIONS,'unknown acknowledgement action')
        qual=ack['qualification'];replacement=ack['replacement']
        need(qual is None or (isinstance(qual,str) and 0<len(qual)<=2048) or
             (isinstance(qual,dict) and set(qual)=={'expression','explanation'}),'invalid acknowledgement qualification')
        if isinstance(qual,dict):
            need(isinstance(qual['expression'],str) and bool(qual['expression']) and len(qual['expression'])<=16000,'qualification expression required')
            need(isinstance(qual['explanation'],str) and len(qual['explanation'])<=2048,'qualification explanation type')
            need(parser.parse(qual['expression'])[1]=='prop','qualification must be proposition')
        need(replacement is None or (isinstance(replacement,str) and replacement in byid and positions[replacement]>=positions[author]),'replacement act absent')
        need(isinstance(ack['note'],str) and len(ack['note'])<=2048,'acknowledgement note')
        if action=='qualify':need((isinstance(qual,str) and bool(qual.strip())) or isinstance(qual,dict),'qualification required')
        else:need(qual is None,'qualification only for qualify')
        if action=='propose-revision':
            need(replacement is not None and replacement!=dest,'proposed revision must identify new retained act')
            need(byid[replacement]['kind'] in ('revision','proposal','hypothesis','assertion'),'replacement must introduce revised claim')
        else:need(replacement is None,'replacement only for propose-revision')
        if action=='withdraw':
            need(byid[author]['speaker']==byid[dest]['speaker'],'cannot withdraw another speakers claim')
        # `accept` is the speaker's communicated stance, never proof of truth.
    return {'count':len(acks),'actions':sorted(set(a['action'] for a in acks))}

def validate_history(history,discourse,definitions):
    need(isinstance(history,dict) and set(history)=={'status','summary','omissions','unresolved','scope'},'history structure')
    status=history['status'];need(status in ('fully-expanded','condensed'),'history status')
    need(isinstance(history['summary'],str) and bool(history['summary'].strip()) and len(history['summary'])<=64000,'history summary missing')
    need(isinstance(history['unresolved'],list) and len(history['unresolved'])<=100 and all(isinstance(x,str) and 0<len(x)<=2048 for x in history['unresolved']),'unresolved history markers')
    need(isinstance(history['scope'],str) and bool(history['scope'].strip()) and len(history['scope'])<=2048,'history coverage scope')
    omissions=history['omissions'];need(isinstance(omissions,list) and len(omissions)<=100,'history omission notes')
    for o in omissions:
        need(isinstance(o,dict) and set(o)=={'scope','reason','not_preserved','implications'},'omission note fields')
        need(all(isinstance(o[k],str) and bool(o[k].strip()) and len(o[k])<=2048 for k in o),'omission note incomplete')
    if status=='fully-expanded':need(not omissions,'fully expanded history cannot declare omissions')
    else:need(bool(omissions),'condensed history must disclose omissions')
    # No hidden reference: all acknowledgement/discourse targets must exist locally.
    need(bool(discourse['acts']) and bool(definitions),'critical content must remain available')
    return {'status':status,'omissions':len(omissions),'standalone':True}

def condense_draft(draft,omit_ids,summary,reason='Reduce historical packet size', *, version=None):
    """Conservative draft condensation; rejects all retained graph and ACK dependencies.

    Never condenses when indirect reference safety is uncertain.
    Authors must review the disclosure; this function cannot assess semantic sufficiency.
    """
    import copy
    result=copy.deepcopy(draft)
    acts=result['discourse']['acts']
    ids={a['id'] for a in acts}; remove=set(omit_ids)
    need(bool(remove) and remove<=ids,'condensation targets unknown or empty')
    need(result['discourse']['current'] not in remove,'cannot condense current act')
    kept=[a for a in acts if a['id'] not in remove]
    for act in kept:
        # Conservative rejection covers direct references plus arbitrary act-specific details.
        need(not set(act['references']).intersection(remove),'cannot remove referenced act')
        need(not _contains_reference(act['details'],remove),'cannot remove act referenced in details')
    for ack in result['acknowledgements']:
        need(ack['by'] not in remove,'cannot remove acknowledgement author')
        target=ack['target']
        if 'act' in target:need(target['act'] not in remove,'cannot remove acknowledgement target')
        elif 'claim' in target:
            claim=result['claims'].get(target.get('claim'))
            need(claim is not None and claim['act'] not in remove,'cannot remove quoted acknowledgement source')
        if ack['replacement'] is not None:need(ack['replacement'] not in remove,'cannot remove replacement')
    for claim in result['claims'].values():
        need(claim['act'] not in remove,'cannot remove claim origin')
    for v in result['viewpoints']:
        need(v['source_act'] not in remove,'cannot remove viewpoint source')
    need(isinstance(summary,str) and bool(summary.strip()),'condensation summary required')
    result['discourse']['acts']=kept
    earlier=result['history']
    result['history']={'status':'condensed','summary':summary,'scope':earlier['scope'],
         'unresolved':earlier['unresolved']+['Verbatim wording of selected omitted acts is unavailable.'],
         'omissions':earlier['omissions']+[{'scope':'Omitted act IDs: '+', '.join(sorted(remove)),
             'reason':reason,'not_preserved':'Original text, annotations and rhetorical examples in removed acts',
             'implications':'Receivers cannot reconstruct or quote omitted turns verbatim.'}]}
    build(result, version=draft_version(result) if version is None else version)
    return result

def _contains_reference(value,removed):
    if isinstance(value,str):return value in removed
    if isinstance(value,list):return any(_contains_reference(x,removed) for x in value)
    if isinstance(value,dict):return any(_contains_reference(v,removed) for v in value.values())
    return False


def orientation_matches(role,kind):
    # Rich discourse act kinds need not be added to the fixed orientation vocabulary.
    aliases={'conditional':{'proposal','hypothesis','assertion','question'},
             'analogy':{'proposal','hypothesis','assertion'},
             'synthesis':{'response','assertion','proposal'},
             'clarification':{'question','response'}}
    return role==kind or role in aliases.get(kind,set())

def make_body(orientation,explanation,conclusion,defs,discourse,acks,claims, *, version=VERSION, archived=False):
    parser=Parser(defs);ts=[parser.parse(s) for s in (orientation,explanation,conclusion)]
    need(ts[0][1]=='orientation' and ts[1][1]=='prop','orientation/explanation types')
    need(ts[2][1] in ('prop','epistemic'),'conclusion must be proposition or epistemic report')
    validate_discourse(discourse,defs,parser,version=version,archived=archived)
    validate_acknowledgements(acks,discourse,defs,parser,claims,version=version,archived=archived)
    declared=' '.join(sorted(g if g in CORE else g+':'+defs[g]['id'] for g in parser.used))
    return ';'.join('['+s+']' for s in (orientation,explanation,conclusion,declared))

def check_revisions(revisions,defs, *, version=VERSION):
    limit = MAX_DEFINITIONS if version in DEPENDENCY_VERSIONS else 55
    need(isinstance(revisions,list) and len(revisions)<=limit,'revisions list')
    seen=set()
    for rev in revisions:
        need(isinstance(rev,dict) and set(rev)=={'old_glyph','new_glyph','old_id','new_id','reason'},'revision fields')
        old,new=rev['old_glyph'],rev['new_glyph']
        need(isinstance(old, str) and isinstance(new, str) and old in defs and new in defs and old!=new,'revision must retain both full definitions')
        need(rev['old_id']==defs[old]['id'] and rev['new_id']==defs[new]['id'] and rev['old_id']!=rev['new_id'],'revision identity mismatch')
        need(isinstance(rev['reason'],str) and rev['reason'].strip(),'revision reason required')
        need((old,new) not in seen,'duplicate revision');seen.add((old,new))

def check_epistemic_context(context,expression):
    need(isinstance(context.get('epistemic'),dict),'epistemic claim requires context.epistemic provenance')
    key=render(expression)
    rec=context['epistemic'].get(key)
    need(isinstance(rec,dict) and set(rec)=={'kind','assessor','evidence','basis','confidence'},'no sourced uncertainty/conflict record')
    need(rec['kind'] in ('uncertainty','conflict'),'missing information is not uncertainty')
    need(isinstance(rec['assessor'],str) and bool(rec['assessor']),'assessor required')
    need(isinstance(rec['evidence'],list) and all(isinstance(e,str) and e for e in rec['evidence']),'evidence list')
    need(isinstance(rec['basis'],str) and bool(rec['basis']),'basis required')
    c=rec['confidence']
    if c is not None:
        need(_decimal_confidence(c),'confidence must be decimal string in [0,1]')
    if rec['kind']=='conflict':need(len(rec['evidence'])>=2,'conflict needs two sources')

def proof_verdict(explanation, conclusion, proof, defs):
    if proof is None:return {'status':'not-requested'}
    try:
        result=check_proof(explanation,conclusion,proof,defs)
        return {'status':'verified','details':result}
    except (ValueError,TypeError,KeyError,IndexError) as exc:
        err=str(exc)
        if 'unsupported proof rule' in err:return {'status':'unsupported','reason':err}
        if 'inconsistent premises' in err:return {'status':'inconsistent-premises','reason':err}
        return {'status':'invalid-proof','reason':err}

def validate_quotes(claims,viewpoints,discourse,parser, *, version=VERSION):
    limit = MAX_LONG_RECORDS if version in LONG_VERSIONS else 150
    need(isinstance(claims,dict) and len(claims)<=limit,'claim binding map')
    acts={a['id']:a for a in discourse['acts']}
    for cid,c in claims.items():
        need(type(cid) is str and re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,63}',cid),'claim ID')
        need(isinstance(c,dict) and set(c)=={'act','expression_index','expression'},'claim fields')
        need(isinstance(c['act'], str) and c['act'] in acts, 'claim origin absent')
        a=acts[c['act']]
        i=c['expression_index'];need(type(i) is int and 0<=i<len(a['expressions']),'claim expression index')
        need(c['expression']==a['expressions'][i],'quote must exactly bind existing act expression')
        need(parser.parse(c['expression'])[1] in ('prop','epistemic'),'quoted claim type')
    need(isinstance(viewpoints,list) and len(viewpoints)<=limit,'viewpoints list')
    positions={a['id']:i for i,a in enumerate(discourse['acts'])}; seen={}
    for v in viewpoints:
        need(isinstance(v,dict) and set(v)=={'id','holder','relation','target','source_act','reported_by'},'viewpoint schema')
        vid=v['id'];need(type(vid) is str and re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,63}',vid) and vid not in seen,'viewpoint identity')
        need(v['relation'] in ('asserts','believes','reports','questions','denies'),'viewpoint relation')
        need(type(v['holder']) is str and bool(v['holder']) and type(v['reported_by']) is str and bool(v['reported_by']),'viewpoint participants')
        need(isinstance(v['source_act'], str) and v['source_act'] in acts, 'viewpoint source act absent')
        origin=acts[v['source_act']]
        need(origin['speaker']==v['reported_by'],'viewpoint reporting speaker must match source')
        t=v['target'];need(isinstance(t,dict) and set(t)=={'kind','id'},'viewpoint target schema')
        if t['kind']=='claim':
            need(isinstance(t['id'], str) and t['id'] in claims,'viewpoint quoted claim absent')
            need(positions[claims[t['id']]['act']]<=positions[v['source_act']],'future claim viewpoint')
        elif t['kind']=='viewpoint':
            need(isinstance(t['id'], str) and t['id'] in seen,'viewpoint target must precede parent (no cycle)')
            need(positions[seen[t['id']]['source_act']]<=positions[v['source_act']],'future viewpoint')
        else:raise ValueError('viewpoint target kind')
        if v['relation']=='asserts':
            need(v['holder']==origin['speaker'],'assertion must belong to reporting speaker')
            need(t['kind']=='claim' and claims[t['id']]['act']==v['source_act'],'assertion binds speaker owned act')
        seen[vid]=v
    return {'quoted_claims':len(claims),'nested_viewpoints':len(viewpoints)}

def check(p, *, archived=False):
    need(isinstance(p,dict) and set(p)=={'guide','definitions','domains','model','proof','context','body','links','revisions','discourse','acknowledgements','history','claims','viewpoints','integrity'},'packet schema')
    version = packet_version(p)
    need(p['integrity']=={'sha256':packet_id(p)},'packet integrity')
    defs = p['definitions']
    validate_defs(defs, p['domains'], version=version)
    if version == VERSION:
        validate_domains(defs, p['domains'])
    need(isinstance(p['context'],dict) and bool(p['context']) and isinstance(p['links'],list),'context/links missing')
    check_revisions(p['revisions'],defs,version=version)
    x=layers(p['body']);parser=Parser(defs);trees=[parser.parse(s) for s in x[:3]]
    discourse_result=validate_discourse(p['discourse'],defs,parser,version=version,archived=archived)
    quote_result=validate_quotes(p['claims'],p['viewpoints'],p['discourse'],parser,version=version)
    ack_result=validate_acknowledgements(p['acknowledgements'],p['discourse'],defs,parser,p['claims'],version=version,archived=archived)
    history_result=validate_history(p['history'],p['discourse'],defs)
    need(trees[0][1]=='orientation' and trees[1][1]=='prop','body layer types')
    expected=' '.join(sorted(g if g in CORE else g+':'+defs[g]['id'] for g in parser.used))
    need(expected==x[3],'used-symbol declaration mismatch')
    role=defs[trees[0][0]]['definition']['role']
    need(orientation_matches(role,discourse_result['kind']),'discourse current act disagrees with orientation')
    if role=='epistemic-report':need(trees[2][1]=='epistemic','epistemic-report needs ? conclusion')
    elif role=='model-check':need(trees[2][1]=='prop','model-check needs propositional conclusion')
    if trees[2][1]=='epistemic':check_epistemic_context(p['context'],trees[2][2][0])
    result={'message':'valid','intent':role,'proof':{'status':'not-requested'},'model':{'status':'not-requested'}}
    if role=='model-check':
        need(p['model'] is not None,'model-check requires finite interpretation')
        budget = _ModelBudget()
        validate_model(defs, p['domains'], p['model'], budget=budget)
        need(evaluate(trees[1], defs, p['domains'], p['model'], budget=budget) is True,
             'premise false in stipulated model')
        need(evaluate(trees[2], defs, p['domains'], p['model'], budget=budget) is True,
             'conclusion false in stipulated model')
        result['model']={'status':'verified-in-one-model'}
    else:
        need(p['model'] is None,'ordinary conversation must not have implicit model check')
    if p['proof'] is not None:
        if trees[2][1]!='prop':result['proof']={'status':'invalid-proof','reason':'epistemic result is not a proposition'}
        else:result['proof']=proof_verdict(trees[1],trees[2],p['proof'],defs)
    return {'status':'VALID '+version,'mode':role,'definitions':len(defs),'discourse':discourse_result,'acknowledgements':ack_result,'history':history_result,'quotation':quote_result,'result':result,'packet_sha256':p['integrity']['sha256']}

def draft_version(draft):
    """Use the current scheme for new drafts and preserve existing archived IDs."""
    _validate_definition_shapes(draft['definitions'], DEPENDENCY_VERSION)
    supplied = [record for record in draft['definitions'].values() if 'id' in record]
    if supplied and all(record['id'] == definition_id(record['definition']) for record in supplied):
        return VERSION
    return CURRENT_VERSION


def build(draft, *, version=VERSION, archived=False):
    required={'definitions','domains','model','proof','context','orientation','explanation','conclusion','links','revisions','discourse','acknowledgements','history','claims','viewpoints'}
    need(isinstance(draft,dict) and set(draft)==required,'draft schema')
    embedded_guide = guide(version)
    records = draft['definitions']
    _validate_definition_shapes(records, version)
    if version in DEPENDENCY_VERSIONS:
        validate_domains(records, draft['domains'])
    ids = _definition_ids(records, draft['domains'], version)
    defs = {}
    for alias, record in records.items():
        identity = ids[alias]
        need('id' not in record or record['id'] == identity, 'supplied hash mismatch ' + alias)
        defs[alias] = {'definition': record['definition'], 'id': identity}
    body=make_body(draft['orientation'],draft['explanation'],draft['conclusion'],defs,draft['discourse'],draft['acknowledgements'],draft['claims'],version=version,archived=archived)
    p={'guide':embedded_guide,'definitions':defs,'domains':draft['domains'],'model':draft['model'],
       'proof':draft['proof'],'context':draft['context'],'body':body,'links':draft['links'], 'revisions':draft['revisions'], 'discourse':draft['discourse'], 'acknowledgements':draft['acknowledgements'], 'history':draft['history'], 'claims':draft['claims'], 'viewpoints':draft['viewpoints']}
    p['integrity']={'sha256':packet_id(p)};check(p,archived=archived);return p

def upgrade_packet(packet, *, archived=False):
    version = packet_version(packet)
    if version == CURRENT_VERSION:
        check(packet, archived=archived)
        return packet

    draft = draft_from_packet(packet, archived=archived)
    if version == VERSION:
        for record in draft['definitions'].values():
            record.pop('id')
        identities = _definition_ids(draft['definitions'], draft['domains'], CURRENT_VERSION)
        for revision in draft['revisions']:
            revision['old_id'] = identities[revision['old_glyph']]
            revision['new_id'] = identities[revision['new_glyph']]
    return build(draft, version=CURRENT_VERSION, archived=archived)


# Transport: plain, human-readable JSON by default. Optional Brotli lives in tools/.
def dump_json(packet, *, pretty=False):
    check(packet)
    if pretty:
        return json.dumps(packet,ensure_ascii=True,indent=2,sort_keys=True)+'\n'
    return canon(packet).decode('ascii')+'\n'

def _unique_json_object(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, f'duplicate JSON key: {key!r}')
        result[key] = value
    return result

def parse_json(data, *, limit=MAX_EXPANDED):
    """Parse bounded UTF-8 JSON and reject ambiguous object keys."""
    if isinstance(data, str):
        data = data.encode('utf-8')
    need(len(data) <= limit, f'JSON input exceeds {limit} bytes')
    try:
        return json.loads(data.decode('utf-8'), object_pairs_hook=_unique_json_object)
    except RecursionError as exc:
        raise ValueError('JSON nesting exceeds parser limit') from exc

def read_json(stream, *, limit=MAX_EXPANDED):
    return parse_json(stream.read(limit + 1), limit=limit)

def read_json_file(path, *, limit=MAX_EXPANDED):
    with Path(path).open('rb') as stream:
        return read_json(stream, limit=limit)

def load_json(text):
    packet = parse_json(text)
    check(packet)
    return packet

def draft_from_packet(packet, *, archived=False):
    check(packet, archived=archived)
    seg=layers(packet['body'])
    out={k:__import__('copy').deepcopy(v) for k,v in packet.items() if k not in ('guide','body','integrity')}
    out.update(orientation=seg[0],explanation=seg[1],conclusion=seg[2])
    return out

def main(args):
    if len(args)==4 and args[1]=='build':
        draft=read_json_file(args[2])
        p=build(draft, version=draft_version(draft))
        Path(args[3]).write_text(dump_json(p,pretty=True),encoding='utf-8')
        print(json.dumps(check(p),indent=2))
    elif len(args)==3 and args[1]=='check':
        p=read_json_file(args[2])
        print(json.dumps(check(p),indent=2))
    elif len(args)==4 and args[1]=='canonicalize':
        p=read_json_file(args[2])
        check(p)
        Path(args[3]).write_bytes(canon(p))
        print('canonical UCL-CJSON-1 written')
    elif len(args)==4 and args[1]=='draft':
        p=read_json_file(args[2])
        Path(args[3]).write_text(json.dumps(draft_from_packet(p),indent=2,ensure_ascii=True)+'\n',encoding='utf-8')
    else:raise ValueError('Usage: python src/ucl.py build draft.json packet.txt | check packet.txt | canonicalize packet.txt canonical.json | draft packet.txt draft.json')

if __name__=='__main__':
    try:main(sys.argv)
    except (ValueError,TypeError,KeyError,UnicodeError,OSError) as e:sys.exit('REJECTED: '+str(e))
