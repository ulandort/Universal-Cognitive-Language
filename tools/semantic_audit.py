#!/usr/bin/env python3
"""Optional decentralized semantic audit for self-contained SVP-1 UCL 2.0.

Purely local, zero-network, zero-cost. Runs an exact Boolean abstraction for
well-typed &,|,! formulas with at most eight distinct atomic propositions.
Every result records its assumptions and limitations. Inferences about
natural-language glosses and scientific truth are NEVER automatic.
No audit report becomes part of the transmitted UCL packet.
"""
from __future__ import annotations
import argparse,itertools,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'tools')]
import ucl
import sap_portable as portable

def atoms(tree):
    if tree[0] in ('!','&','|'):
        return set().union(*(atoms(t) for t in tree[2]))
    return {ucl.render(tree)}

def boolean_value(tree,assignment):
    op=tree[0]
    if op=='!':return not boolean_value(tree[2][0],assignment)
    if op=='&':return all(boolean_value(x,assignment) for x in tree[2])
    if op=='|':return any(boolean_value(x,assignment) for x in tree[2])
    return assignment[ucl.render(tree)]

def analyze_expression(formula,defs,assumptions=(),atom_limit=8):
    parser=ucl.Parser(defs)
    t=parser.parse(formula)
    if t[1]!='prop':
        return {'verdict':'not-assessed','reason':'epistemic expression; not Boolean truth'}
    premises=[ucl.Parser(defs).parse(p) for p in assumptions]
    if any(x[1]!='prop' for x in premises):
        return {'verdict':'not-assessed','reason':'premise not a proposition'}
    all_atoms=sorted(set().union(atoms(t),*(atoms(p) for p in premises)))
    if len(all_atoms)>atom_limit:
        return {'verdict':'not-assessed','reason':'Boolean atom cap exceeded',
                'atom_count':len(all_atoms)}
    candidates=[]
    for bits in itertools.product((False,True),repeat=len(all_atoms)):
        a=dict(zip(all_atoms,bits))
        if all(boolean_value(p,a) for p in premises):
            candidates.append((a,boolean_value(t,a)))
    if not candidates:
        return {'verdict':'not-assessed','reason':'assumptions unsatisfiable in Boolean abstraction',
                'assumptions':list(assumptions)}
    true_cases=[a for a,val in candidates if val]
    if not true_cases:
        return {'verdict':'demonstrated-contradiction-under-assumptions',
                'assumptions':list(assumptions),'atom_count':len(all_atoms),
                'method':'exhaustive Boolean truth table for uninterpreted atoms',
                'interpretation':'No assignments satisfying listed assumptions also satisfy tested formula; not a claim that the idea is empirically false'}
    return {'verdict':'formally-consistent-under-assumptions',
            'assumptions':list(assumptions),'atom_count':len(all_atoms),
            'method':'exhaustive Boolean truth table for uninterpreted atoms',
            'witness':true_cases[0],
            'interpretation':'A Boolean satisfying assignment exists; this does not establish empirical truth or semantic alignment'}

def audit(envelope):
    packet=portable.decode(envelope)
    defs=packet['definitions']
    acts=packet['discourse']['acts']
    observations=[]
    for act in acts:
        for index,formula in enumerate(act.get('expressions',[])):
            result=analyze_expression(formula,defs)
            observations.append({
                'act_id':act['id'],'expression_index':index,'expression':formula,
                'formal_check':result,
                'natural_language_alignment':'not-assessed',
                'novelty':'unresolved; no rejection or suppression'
            })
    return {'profile':'UCL/2.0-SVP-1-DRAFT','packet_checksum':envelope['checksum'],
            'independent_sidecar':True,'transport_packet_modified':False,
            'observations':observations,
            'limits':'Uninterpreted Boolean abstraction; atom independence is assumed only for this check. Formal compatibility cannot establish meaning, truth, causation or novelty. Natural-language alignment needs separate accountable interpretation. No automatic semantic veto.'}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('source',type=Path)
    p.add_argument('--output',type=Path)
    a=p.parse_args()
    packet=json.loads(a.source.read_text(encoding='utf-8'))
    result=audit(packet)
    text=json.dumps(result,indent=2,ensure_ascii=True)+'\n'
    if a.output:a.output.write_text(text,encoding='utf-8')
    else:print(text)

if __name__=='__main__':main()
