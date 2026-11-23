#!/usr/bin/env python3
"""Self-contained UCL/2.0 Portable wire envelope and validation.

An ordinary UTF-8 JSON (.txt or .json) file embeds BOTH the entire checked
UCL/1.0 conversation packet/guide and the complete human-readable SAP-1
authoring rules. No URI, central registry, hosted service, network access,
or external schema download is needed to read or verify a packet. 1.0 is
retains its original typed grammar; this is the stable 2.0 transport.
"""
from __future__ import annotations
import argparse
import base64
import copy
import hashlib
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'benchmarks')]
import ucl
import structural_authoring as sap

FORMAT='UCL/2.0-SAP1-PORTABLE'
RULE_DOMAIN=b'UCL-SAP1-RULES-2.0\n'
ENVELOPE_DOMAIN=b'UCL-SAP1-ENVELOPE-2.0\n'
ROLES=frozenset(('hypothesis','example','counterexample','quotation','question'))
ROLE_GUIDE=('FR-1 draft: act/index identifies an exact expression in packet.discourse.acts; '
            'role is an author-declared purpose (hypothesis, example, counterexample, '
            'quotation, question), NOT proof or truth. Missing role is unspecified. '
            'Never suppress original novel ideas.')

# Full, inspectable rules are part of EVERY message. All required structure,
# extension policy, types and reply-authoring procedure appear inline.
RULES={
  'id':sap.PROFILE,
  'status':'stable-2.0',
  'language_guide_location':'packet.guide (fully embedded)',
  'complete_history_location':'packet.discourse + packet.history',
  'core_glyphs':['@','#','=','~','&','|','!','?','<','*','{'],
  'structural_glyphs':[':', ';', '[', ']', '-'],
  'authoring_kind':'incremental model-authored response contribution',
  'required_contribution_fields':sorted(sap.CONTRIBUTION_FIELDS),
  'required_act_fields':sorted(sap.ACT_FIELDS),
  'required_ack_fields':sorted(sap.ACK_FIELDS),
  'response_details_fields':['responds_to','stance'],
  'response_stances':sorted(sap.STANCES),
  'acknowledgement_actions':sorted(sap.ACTIONS),
  'reference_rules':{
    'act_id':'unique non-empty ID absent from earlier packet.discourse.acts; caller may reserve an expected ID',
    'references':'array of earlier existing act IDs; no forward references',
    'responds_to':'ID of an existing earlier discourse act',
    'ack_id':'unique non-empty ID absent from earlier acknowledgements; caller may reserve an expected ID',
    'ack_by':'new act ID',
    'ack_target':'{"claim":"existing_claim_id","path":[0]} with zero-based INTEGER subtree indices; use [] for entire bound claim',
    'claim_bindings':'packet.claims ties each claim to an exact retained earlier expression',
    'ack_target_precedes_author':'target expression must be in an earlier act',
    'identity_policy':'never silently revise/overwrite earlier definitions or acts'
  },
  'type_rules':{
    'orientation':'for response kind, "L" in SAP-1',
    'explanation':'well-typed UCL proposition; never bare epistemic report',
    'conclusion':'well-typed UCL proposition or sourced epistemic report',
    'act_expressions':'array of valid UCL proposition/epistemic expressions',
    'ack_target_path':'array of integers, never strings',
    'receipt':'null when no preceding delivered GENERATED turn; earlier historical acts do not count',
    'epistemic':'?[p] as epistemic conclusion needs context.epistemic evidence/assessor/basis/confidence as required by guide; ACK withhold-judgment is NOT a ? conclusion',
    'negation':'![p] means not p, NOT merely unproven or not measured'
  },
  'typed_formula_examples':{
    'property':'~[P][A]',
    'negation':'![~[P][A]]',
    'conjunction':'&[~[P][A]][~[B][A]]',
    'disjunction':'|[~[P][A]][~[B][A]]'
  },
  'incremental_authoring_procedure':[
    'Read the complete embedded packet.guide, definitions, history, discourse and claim bindings.',
    'Read these embedded structural rules; derive a fresh act ID and acknowledgement ID.',
    'Author original symbolic expressions, stance, exact old claim reference, explanation and conclusion directly; do NOT first draft English for conversion.',
    'Construct a complete contribution object with only the listed fields; use the benchmark caller-reserved IDs if supplied.',
    'Run local structural checks and standard UCL/1.0 validation; if invalid, reauthor the semantic contribution; do not have an intermediary silently modify it.',
    'Append the contribution to the retained packet mechanically, reconstruct body and SHA-256 integrity locally and embed the same full rules in the new message.',
    'A receiver independently checks embedded rule integrity and packet integrity before using the newly authored message.'
  ],
  'language_extension_policy':{
    'existing_custom_definitions':'valid defined custom concept symbols are allowed when appropriately typed and hashed in the packet',
    'new_core_operators':'NOT silently valid; unknown operators must be proposed in explicitly marked non-normative text pending versioned adoption',
    'new_semantics':'open hypotheses and unexpected inferences allowed; syntax validity does not certify truth',
    'no_central_registry':'all necessary guide, rules, definitions and conversation context are in this message'
  },
  'semantic_verification':{
    'id':'UCL/2.0-SVP-1-DRAFT',
    'execution':'OPTIONAL local check by any recipient; no central judge or network, no mandatory audit metadata on wire',
    'checks':{
      'types':'Use existing UCL typed grammar and validator; syntax validity is distinct from truth',
      'consistency':'Within declared finite Boolean fragments, test satisfiability against explicitly named premises; contradiction must include assumptions and a reproducible counterexample or derivation',
      'alignment':'Compare original act.text with formal expressions and referenced stance; use uncertain/needs-clarification when natural-language meaning is ambiguous; NOT deterministic truth',
      'continuity':'Compare claims, scoped ACK actions, prior reference and evidence status with earlier acts; show exact source locations'
    },
    'verdicts':['formally-consistent-under-assumptions','demonstrated-contradiction-under-assumptions','alignment-question','novel-or-unresolved','unsupported-empirical-claim','not-assessed'],
    'novelty':'NEVER reject, delete, rewrite, auto-normalize, or declare false because an original hypothesis is unfamiliar, unverified, speculative or contrary to expectations',
    'contradictions':'Preserve original even if formally contradictory; report precise premises, scope and derivation; invite model to revise assumptions or explain interpretation',
    'authority':'Audits are local and advisory. Independent auditors may disagree; no single AI opinion may govern acceptance or transport of well-formed UCL.',
    'reporting':'No verdicts or assessment transcripts are required inside UCL wire. Optional signed or unsigned sidecar may reference exact packet checksum; any transmitted result is explicitly labeled as separate assessor opinion.',
    'no_silent_semantic_repair':True
  },
  'integrity_notice':'SHA-256 detects accidental or untrusted rewriting only when trusted anchors exist; a self-hash alone is NOT authentication or authority.'
}

# Portable 2.0 embeds a compact offline authoring preflight.\nRULES['type_rules']['local_authoring_preflight']=(
    'Offline preflight: ACK target.path=[0] (integer), never ["0"] (string); '
    'act.expressions is a list of UCL strings; explanation and conclusion '
    'are UCL strings; use only defined operators. For action=qualify, '
    'qualification must be nonempty string or valid object; other actions '
    'require null. Validate locally; return precise errors for author-owned '
    'corrections. Never silently rewrite semantic intent; no network.'
)

def fingerprint(domain,obj):
    return base64.urlsafe_b64encode(
        hashlib.sha256(domain+ucl.canon(obj)).digest()
    ).decode('ascii').rstrip('=')

def rules_hash(rules):
    return fingerprint(RULE_DOMAIN,rules)

def envelope_checksum(envelope):
    return fingerprint(ENVELOPE_DOMAIN,{k:v for k,v in envelope.items() if k!='checksum'})

def _validate_formula_roles(packet,roles):
    if type(roles) is not list:
        raise ValueError('SAP portable: formula_roles must be an array')
    if len(roles)>512:
        raise ValueError('SAP portable: formula_roles array too long')
    acts={a['id']:a for a in packet['discourse']['acts']}
    used=set()
    for item in roles:
        if type(item) is not dict or set(item)!={'act','index','role'}:
            raise ValueError('SAP portable: formula role entry has invalid fields')
        act=item['act']; index=item['index']; role=item['role']
        if type(act) is not str or act not in acts:
            raise ValueError('SAP portable: formula role references missing act')
        formulas=acts[act]['expressions']
        if type(index) is not int or index<0 or index>=len(formulas):
            raise ValueError('SAP portable: formula role references missing expression')
        if type(role) is not str or role not in ROLES:
            raise ValueError('SAP portable: unknown formula role')
        key=(act,index)
        if key in used:
            raise ValueError('SAP portable: duplicate formula role target')
        used.add(key)
    return True

def encode(packet,formula_roles=None):
    ucl.check(packet)
    rules=copy.deepcopy(RULES)
    env={'format':FORMAT,'profile':'portable',
         'structural_rules':{'rules':rules,'sha256':rules_hash(rules)},
         'packet':copy.deepcopy(packet)}
    if formula_roles is not None:
        _validate_formula_roles(packet,formula_roles)
        env['formula_roles']=copy.deepcopy(formula_roles)
        env['formula_role_guide']=ROLE_GUIDE
    env['checksum']=envelope_checksum(env)
    return env

def decode(env):
    required={'format','profile','structural_rules','packet','checksum'}
    if type(env) is not dict or set(env) not in (required,required|{'formula_roles','formula_role_guide'}):
        raise ValueError('SAP portable: envelope fields invalid')
    if env['format']!=FORMAT or env['profile']!='portable':
        raise ValueError('SAP portable: unsupported profile')
    block=env['structural_rules']
    if type(block) is not dict or set(block)!={'rules','sha256'}:
        raise ValueError('SAP portable: rules block invalid')
    if block['sha256']!=rules_hash(block['rules']):
        raise ValueError('SAP portable: embedded authoring rules checksum mismatch')
    if block['rules']!=RULES:
        raise ValueError('SAP portable: unknown or altered structural standard')
    if env['checksum']!=envelope_checksum(env):
        raise ValueError('SAP portable: envelope checksum mismatch')
    pkt=copy.deepcopy(env['packet'])
    ucl.check(pkt)
    if type(pkt.get('guide')) is not dict:
        raise ValueError('SAP portable: missing full embedded UCL guide')
    if 'formula_roles' in env:
        if env['formula_role_guide']!=ROLE_GUIDE:
            raise ValueError('SAP portable: unknown formula role profile')
        _validate_formula_roles(pkt,env['formula_roles'])
    return pkt

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('mode',choices=('encode','decode','check'))
    ap.add_argument('source',type=Path)
    ap.add_argument('output',type=Path,nargs='?')
    a=ap.parse_args()
    data=json.loads(a.source.read_text(encoding='utf-8'))
    if a.mode=='encode':
        result=encode(data)
    else:
        result=decode(data)
    if a.output:
        a.output.write_bytes(ucl.canon(result))
        print(str(a.output))
    else:
        print('VALID self-contained SAP-1 '+a.mode)
if __name__=='__main__':main()
