#!/usr/bin/env python3
"""Experimental fully self-contained UCL/2.0 Portable structural envelope.

No central registry, hosted service, cached grammar or remote guide is needed.
The complete UCL/1.0 packet remains embedded, and a full versioned structural
authoring contract accompanies it. Neither SHA-256 hashes nor self-description
authenticate an author or prove a model's claims. This is experimental 2.0,
NOT a replacement for the released 1.0 wire protocol.
"""
from __future__ import annotations
import copy, hashlib, json, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import ucl

FORMAT="UCL/2.0-experimental-portable"
PROFILE_ID="UCL/2.0-SAP-1"
PROFILE_HASH_DOMAIN=b"UCL-2-SAP-1\n"
ENVELOPE_HASH_DOMAIN=b"UCL-2-PORTABLE-1\n"

# This complete authoring profile is data INSIDE every message. A reader can
# implement the specified structural checks with no project checkout.
AUTHORING_PROFILE={
 "id":PROFILE_ID,
 "status":"experimental-2.0; no changes to UCL/1.0 or its 11 core glyphs",
 "scope":"Typed incremental native authorship; full retained UCL/1.0 semantics live in packet.guide",
 "invariants":{
   "message":"Full portable JSON text carries profile, complete packet and integrity. No cache or network required.",
   "extension_policy":"New named concepts require explicit immutable symbol definitions. Proposed new operators are non-normative until a versioned grammar change and independent conformance.",
   "no_semantic_repair":"A validator rejects rather than silently editing authored expressions, target, stance or evidence.",
   "evidence":"Hypothetical examples are not empirical proof. A withhold-judgment ACK is not an epistemic formula."
 },
 "authoring_contribution_schema":{
   "type":"object",
   "required_exact":["act","orientation","explanation","conclusion","acknowledgements","history_summary"],
   "act":{
      "required_exact":["id","kind","speaker","references","text","expressions","details"],
      "id":"unique turn ID, prescribed by active conversation; never reused",
      "kind":"response in SAP-1 response profile",
      "speaker":"nonempty current author's identifier",
      "references":"array of retained earlier act IDs only",
      "text":"nonempty author-supplied description; not a parser replacement",
      "expressions":"array of independently well-typed UCL prefix formulas",
      "details":{"required_exact":["responds_to","stance"],
                 "responds_to":"existing earlier act ID",
                 "stance_enum":["accept","reject","mixed","undetermined"]}
   },
   "orientation":{"for_response":"L","semantics":"A defined orientation term; top-level orientation is not a proposition"},
   "explanation":"UCL proposition expression, NEVER an epistemic ? report",
   "conclusion":"UCL proposition OR a properly provenance-backed epistemic expression",
   "acknowledgements":{
      "count":1,
      "required_exact":["id","by","target","action","qualification","replacement","note"],
      "id":"unique exact expected next acknowledgement ID",
      "by":"new act ID",
      "target":{"required_exact":["claim","path"],
                "claim":"existing quoted claim binding",
                "path":"array of nonnegative JSON integers; each index must reach a proposition/epistemic subtree"},
      "action_enum":["received","understood","accept","reject","qualify","clarify",
                     "propose-revision","adopt-for-discussion","withhold-judgment","withdraw"],
      "qualification":"non-null only for qualify, required when qualify",
      "replacement":"non-null only for propose-revision, validated destination act",
      "note":"string; can describe language-extension proposals without changing grammar"
   },
   "history_summary":"nonempty author-provided summary; retained packet history stays unchanged"
 },
 "symbolic_grammar":{
   "notation":"Prefix operator followed by individually bracketed typed arguments. No parentheses, free-form AND/OR, bare ?, or undeclared operators.",
   "eleven_core_glyphs":["@","#","=","~","&","|","!","?","<","*","{"],
   "structural_glyphs":[":",";","[","]","-"],
   "examples":{
     "P":"~[P][A]",
     "B":"~[B][A]",
     "not_P":"![~[P][A]]",
     "P_and_B":"&[~[P][A]][~[B][A]]",
     "P_or_B":"|[~[P][A]][~[B][A]]"
   },
   "epistemic":"?[p] means sourced uncertainty/conflict, not question and not absence of information. Requires appropriate context.epistemic provenance for epistemic conclusions.",
   "ack_not_negation":"An ACK rejecting P does not require the formula ![P]. ACK stance and proposition are separate typed facts."
 },
 "composition":{
   "procedure":[
     "Read this embedded profile and the complete packet.guide and packet.definitions",
     "Preserve all prior acts, definitions, immutable claim bindings and required history",
     "Create one response act and scoped acknowledgement with exact expected IDs",
     "Use well-typed formulas and cite complete epistemic provenance if needed",
     "Assemble the complete UCL/1.0 packet, compute its canonical checksums and run ordinary UCL/1.0 validation",
     "Attach this complete profile and re-compute the 2.0 profile/envelope checksums",
     "Transmit the entire envelope; a recipient validates it locally and needs no network"
   ],
   "optional_error_feedback":"Model may reauthor a full invalid contribution after seeing exact checker errors. No host changes to semantic fields. Disclose first-try versus assisted success.",
   "nonstandard_operator":"Describe proposed syntax in act text as PROPOSAL; do not place unrecognized operator in normative formula."
 },
 "canonicalization":{
   "algorithm":"UCL-CJSON-1 inherited from enclosed packet.guide.canonicalization",
   "profile_digest":"Base64url SHA256(ASCII 'UCL-2-SAP-1\\n' + canonical JSON profile)",
   "envelope_digest":"Base64url SHA256(ASCII 'UCL-2-PORTABLE-1\\n' + canonical JSON object excluding integrity)",
   "note":"Integrity detects alteration; it is NOT digital signature or authority."
 }
}

def profile_digest(profile):
    return ucl.b64(hashlib.sha256(PROFILE_HASH_DOMAIN+ucl.canon(profile)).digest())

def envelope_digest(envelope):
    return ucl.b64(hashlib.sha256(ENVELOPE_HASH_DOMAIN+
        ucl.canon({k:v for k,v in envelope.items() if k!='integrity'})).digest())

def encode(packet,profile=None):
    ucl.check(packet)
    p=copy.deepcopy(AUTHORING_PROFILE if profile is None else profile)
    obj={'format':FORMAT,
         'structural_profile':p,
         'structural_profile_sha256':profile_digest(p),
         'packet':copy.deepcopy(packet)}
    obj['integrity']={'sha256':envelope_digest(obj)}
    check(obj)
    return obj

def check(envelope):
    if type(envelope) is not dict or set(envelope)!={
       'format','structural_profile','structural_profile_sha256','packet','integrity'}:
        raise ValueError('UCL2 portable envelope must have exact self-contained fields')
    if envelope['format']!=FORMAT:raise ValueError('Wrong UCL2 Portable format')
    profile=envelope['structural_profile']
    if type(profile) is not dict or profile.get('id')!=PROFILE_ID:
        raise ValueError('Unknown or incomplete authoring profile ID')
    if profile!=AUTHORING_PROFILE:
        raise ValueError('Structural authoring profile not the locally recognized SAP-1 standard')
    if envelope['structural_profile_sha256']!=profile_digest(profile):
        raise ValueError('Embedded SAP-1 profile hash mismatch')
    if envelope['integrity']!={'sha256':envelope_digest(envelope)}:
        raise ValueError('UCL2 portable envelope integrity mismatch')
    result=ucl.check(envelope['packet'])
    return {'format':FORMAT,'profile':PROFILE_ID,'packet_result':result,
            'self_contained':True}

def decode(envelope):
    check(envelope)
    return copy.deepcopy(envelope['packet'])

if __name__=='__main__':
    if len(sys.argv)!=3 or sys.argv[1] not in ('check','encode'):
        raise SystemExit('Usage: python tools/ucl2_portable.py check|encode file.json')
    p=Path(sys.argv[2])
    if sys.argv[1]=='check':
        print(json.dumps(check(json.loads(p.read_text())),indent=2))
    else:
        obj=encode(ucl.load_json(p.read_text()))
        p.with_name(p.stem+'.ucl2.txt').write_text(json.dumps(obj,indent=2,ensure_ascii=True)+'\n')
        print('Generated self-contained UCL 2.0 experimental Portable packet')
