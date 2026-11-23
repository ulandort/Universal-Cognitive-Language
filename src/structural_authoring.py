"""UCL/2.0 embedded Structural Authoring Profile (SAP-1).

A deterministic structural schema for direct model-authored contributions.
NOT a replacement for UCL/1.0 grammar, core glyphs or normative validator.
No authored semantic fields are transformed or silently corrected.
"""
PROFILE="UCL/2.0-SAP-1"
ACT_FIELDS={'id','kind','speaker','references','text','expressions','details'}
ACK_FIELDS={'id','by','target','action','qualification','replacement','note'}
CONTRIBUTION_FIELDS={'act','orientation','explanation','conclusion','acknowledgements','history_summary'}
ACTIONS={'received','understood','accept','reject','qualify','clarify','propose-revision','adopt-for-discussion','withhold-judgment','withdraw'}
STANCES={'accept','reject','mixed','undetermined'}

class StructuralProfileError(ValueError):pass
def demand(condition,reason):
    if not condition:raise StructuralProfileError('SAP-1: '+reason)

def check_contribution(obj,*,speaker,act_id,ack_id,prior_acts,claims):
    """Narrow authoring envelope; real UCL check() must still run afterward."""
    demand(type(obj) is dict and set(obj)==CONTRIBUTION_FIELDS,
           'contribution fields must match exact six-key template')
    a=obj['act']
    demand(type(a) is dict and set(a)==ACT_FIELDS,'act fields must match exact seven-key template')
    demand(a['id']==act_id,'act.id must equal '+act_id)
    demand(a['speaker']==speaker,'act.speaker must equal '+speaker)
    demand(a['kind']=='response','act.kind must equal response')
    demand(type(a['references']) is list and
           all(type(x) is str and x in prior_acts for x in a['references']),
           'act.references must contain only earlier retained act IDs')
    demand(type(a['text']) is str and bool(a['text'].strip()),'act.text must be nonempty')
    demand(type(a['expressions']) is list and
           all(type(x) is str for x in a['expressions']),
           'act.expressions must be a list of original UCL expressions')
    dt=a['details']
    demand(type(dt) is dict and set(dt)=={'responds_to','stance'},
           'response details must contain responds_to and stance only')
    demand(dt['responds_to'] in prior_acts,'responds_to must refer to an existing act')
    demand(dt['stance'] in STANCES,'stance must be one of accept/reject/mixed/undetermined')
    demand(obj['orientation']=='L','this response profile uses UCL orientation L')
    demand(type(obj['explanation']) is str and type(obj['conclusion']) is str,
           'explanation and conclusion must be UCL expression strings')
    demand(type(obj['history_summary']) is str and bool(obj['history_summary'].strip()),
           'history_summary must be nonempty')
    acks=obj['acknowledgements']
    demand(type(acks) is list and len(acks)==1,'exactly one scoped ACK is required')
    ack=acks[0]
    demand(type(ack) is dict and set(ack)==ACK_FIELDS,'ACK must match exact seven-key template')
    demand(ack['id']==ack_id,'ACK id must equal '+ack_id)
    demand(ack['by']==act_id,'ACK by must equal new act id')
    target=ack['target']
    demand(type(target) is dict and set(target)=={'claim','path'},
           'ACK target must contain claim and path only')
    demand(type(target['claim']) is str and target['claim'] in claims,
           'ACK claim must be an existing immutable claim binding')
    demand(type(target['path']) is list and len(target['path'])<=32 and
           all(type(i) is int and i>=0 for i in target['path']),
           'ACK path must be an array of nonnegative INTEGER indices')
    demand(ack['action'] in ACTIONS,'ACK action must be an existing acknowledgement')
    demand(ack['action']=='qualify' or ack['qualification'] is None,
           'qualification is allowed only for qualify')
    demand(ack['action']=='propose-revision' or ack['replacement'] is None,
           'replacement is allowed only for propose-revision')
    demand(type(ack['note']) is str,'ACK note must be a string')
    return obj

def authoring_rules(*,act_id,ack_id,speaker,prior_act):
    return (
      PROFILE+' AUTHORING CONTRACT. No new core glyphs, no change to language truth. '
      'Create a JSON object with receipt, intent, authored. authored MUST contain '
      'exactly act, orientation, explanation, conclusion, acknowledgements, '
      'history_summary. act MUST contain exactly id,kind,speaker,references,'
      'text,expressions,details. act.id='+act_id+'; act.speaker='+speaker+
      '; act.kind=response. details has exactly responds_to and stance. '
      'responds_to must name an existing prior act (example '+prior_act+
      '), stance one of accept/reject/mixed/undetermined. orientation MUST be "L". '
      'explanation MUST be a proposition, not a standalone epistemic ? expression. '
      'conclusion MUST be a proposition or a sourced epistemic report. '
      'acknowledgements MUST contain exactly one object with '
      'id,by,target,action,qualification,replacement,note. '
      'ACK id='+ack_id+'; ACK by='+act_id+
      '. ACK target must be {"claim":"theory","path":[0]} (P) or path [1] (B); '
      'indices are INTEGERS, not digit strings. '
      'Valid formula examples: ~[P][A], ![~[P][A]], '
      '&[~[P][A]][~[B][A]], |[~[P][A]][~[B][A]]. '
      'No bare AND, OR, parentheses, undefined operators or free-floating ?. '
      'ANY correctly typed UCL expression is allowed, including new well-defined '
      'concept symbols. If you wish to propose an undefined glyph/operator, '
      'describe it as an EXPLICIT NON-NORMATIVE PROPOSAL in your act.text/note; '
      'do not slip it into executable UCL syntax. Proposed innovations are '
      'preserved for research but NOT valid until independently specified and '
      'adopted through an explicit versioning process. '
      'Your authored semantics will not be rewritten or repaired by the host.'
    )
