#!/usr/bin/env python3
"""Self-contained UCL Portable wire envelope and validation.

An ordinary UTF-8 JSON (.txt or .json) file embeds BOTH the entire checked
typed UCL inner conversation packet/guide and the complete human-readable SAP-1
authoring rules. No URI, central registry, hosted service, network access,
or external schema download is needed to read or verify a packet.
Current and historical versions carry their respective pinned guides.
"""
from __future__ import annotations
import argparse
import base64
import copy
import hashlib
import sys
from pathlib import Path
import ucl
import structural_authoring as sap

FORMAT=ucl.LEGACY_PORTABLE_FORMAT  # Retained for archived release tooling.
CURRENT_FORMAT=ucl.PORTABLE_FORMAT
FORMAT_BY_VERSION={ucl.INNER_GRAMMAR_VERSION: CURRENT_FORMAT, 'UCL/1.0': FORMAT}
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

# Portable 2.0 embeds a compact offline authoring preflight.
RULES['type_rules']['local_authoring_preflight']=(
    'Offline preflight: ACK target.path=[0] (integer), never ["0"] (string); '
    'act.expressions is a list of UCL strings; explanation and conclusion '
    'are UCL strings; use only defined operators. For action=qualify, '
    'qualification must be nonempty string or valid object; other actions '
    'require null. Validate locally; return precise errors for author-owned '
    'corrections. Never silently rewrite semantic intent; no network.'
)

CURRENT_RULES = {
    **RULES,
    'status': 'stable-2.1',
    'optional_act_fields': ['vocabulary'],
    'vocabulary_authoring': (
        'Use a fresh single-character alias or a name such as $background_sync in new_definitions. '
        'An act may record a retirement or attach a typed example or counterexample to a definition '
        'using the vocabulary shapes in packet.guide.vocabulary. Preserve every previous definition, '
        'including one a speaker retires.'
    ),
    'definition_identity': (
        'Use packet.guide.hashing for dependency-aware definition IDs. A new typed definition '
        'uses a fresh alias. Preserve prior definitions and domain declarations; local aliases '
        'are resolved to domain IDs before hashing.'
    ),
    'reply_template': {
        'instructions': (
            'Author only the contribution object below. Use it as a template, not as conversation data. '
            'Replace sample IDs, speaker, references, claim path, aliases, expressions, and prose '
            'with values from your task and this packet. JSON path and expression indexes are integers. '
            'Use your own definition, reasoning, and stance. Include retire only when retiring a '
            'declared definition for your own use. Omit vocabulary or new_definitions when unneeded. '
            'The local tool carries forward history and computes IDs and checksums.'
        ),
        'contribution': {
            'act': {
                'id': 't10',
                'kind': 'response',
                'speaker': 'Your speaker name',
                'references': ['t9', 't1'],
                'text': 'Explain your concept and why it addresses the earlier claim.',
                'expressions': ['~[$example_predicate][A]'],
                'details': {'responds_to': 't9', 'stance': 'mixed'},
                'vocabulary': [
                    {'action': 'example', 'definition': '$example_predicate', 'expression_index': 0},
                    {'action': 'retire', 'definition': '$previous_alias', 'successor': '$example_predicate'},
                ],
            },
            'orientation': 'L',
            'explanation': '~[$example_predicate][A]',
            'conclusion': '~[$example_predicate][A]',
            'new_definitions': {
                '$example_predicate': {'kind': 'predicate', 'args': ['D'], 'gloss': 'Define your predicate.'},
            },
            'acknowledgements': [{
                'id': 'x6',
                'by': 't10',
                'target': {'claim': 'theory', 'path': [1]},
                'action': 'qualify',
                'qualification': {
                    'expression': '~[$example_predicate][A]',
                    'explanation': 'Explain when this qualification applies.',
                },
                'replacement': None,
                'note': 'Describe the scope of your qualification.',
            }],
            'history_summary': 'Summarize the new act and retained history.',
        },
    },
}
RULES_BY_FORMAT = {FORMAT: RULES, CURRENT_FORMAT: CURRENT_RULES}


def label(format_id):
    return format_id.split('-')[0] + ' Portable'


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
    format_id = FORMAT_BY_VERSION[ucl.packet_version(packet)]
    rules = copy.deepcopy(RULES_BY_FORMAT[format_id])
    env={'format':format_id,'profile':'portable',
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
    format_id = env['format']
    if not isinstance(format_id, str) or format_id not in RULES_BY_FORMAT or env['profile']!='portable':
        raise ValueError('SAP portable: unsupported profile')
    block=env['structural_rules']
    if type(block) is not dict or set(block)!={'rules','sha256'}:
        raise ValueError('SAP portable: rules block invalid')
    expected_rules = RULES_BY_FORMAT[format_id]
    if block['rules']!=expected_rules:
        raise ValueError('SAP portable: unknown or altered structural standard')
    expected_hash = rules_hash(expected_rules)
    if block['sha256'] != expected_hash or rules_hash(block['rules']) != expected_hash:
        raise ValueError('SAP portable: embedded authoring rules checksum mismatch')
    if env['checksum']!=envelope_checksum(env):
        raise ValueError('SAP portable: envelope checksum mismatch')
    pkt=copy.deepcopy(env['packet'])
    ucl.check(pkt)
    if FORMAT_BY_VERSION[ucl.packet_version(pkt)] != format_id:
        raise ValueError('SAP portable: inner guide version does not match the envelope format')
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
    limit = ucl.MAX_EXPANDED if a.mode == 'encode' else ucl.MAX_PORTABLE_JSON
    data = ucl.read_json_file(a.source, limit=limit)
    if a.mode=='encode':
        result=encode(data)
    else:
        result=decode(data)
    if a.output:
        data = ucl.portable_json_bytes(result) if a.mode == 'encode' else ucl.canon(result)
        a.output.write_bytes(data)
        print(str(a.output))
    else:
        print('VALID self-contained SAP-1 '+a.mode)
def run_cli():
    try:
        main()
    except (ValueError, TypeError, KeyError, OSError) as exc:
        sys.exit('REJECTED: ' + str(exc))

if __name__=='__main__':run_cli()
