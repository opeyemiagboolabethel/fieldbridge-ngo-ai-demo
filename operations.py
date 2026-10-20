"""Deterministic NGO evidence and session-only, human-approved actions."""
from copy import deepcopy
from datetime import date
ROLES={'director':'Executive director','programme':'Programme & MEL lead','finance':'Finance & grants lead'}
AS_OF='2026-10-20'
def load_state():
    return {'as_of':AS_OF,'programmes':[
        {'id':'P01','programme':'Community learning','location':'Lagos','currency':'NGN','budget':48000000,'spent':29400000,'committed':8200000,'target':600,'verified_unique_reach':412,'pending_verification':48,'unit':'unique learners','owner':'Programme lead'},
        {'id':'P02','programme':'Women’s livelihoods','location':'Ogun','currency':'NGN','budget':36000000,'spent':22800000,'committed':6100000,'target':240,'verified_unique_reach':176,'pending_verification':22,'unit':'unique participants','owner':'Livelihoods lead'},
        {'id':'P03','programme':'Community health outreach','location':'Kaduna','currency':'NGN','budget':52000000,'spent':31800000,'committed':12400000,'target':1200,'verified_unique_reach':846,'pending_verification':73,'unit':'unique participants','owner':'Health programme lead'},
        {'id':'P04','programme':'Partner capacity strengthening','location':'Regional partners','currency':'USD','budget':90000,'spent':48500,'committed':18500,'target':20,'verified_unique_reach':12,'pending_verification':3,'unit':'partner organisations','owner':'Partnerships lead'}],
        'reports':[
        {'id':'R01','programme_id':'P01','deliverable':'Quarterly learning report','donor':'Learning Futures Fund (fictional)','due':'2026-10-23','status':'In preparation','owner':'MEL officer'},
        {'id':'R02','programme_id':'P02','deliverable':'Milestone evidence pack','donor':'Opportunity Fund (fictional)','due':'2026-10-19','status':'In preparation','owner':'Livelihoods lead'},
        {'id':'R03','programme_id':'P03','deliverable':'Community outreach update','donor':'Community Health Trust (fictional)','due':'2026-10-30','status':'In preparation','owner':'Health programme lead'},
        {'id':'R04','programme_id':'P04','deliverable':'Partner training summary','donor':'Regional Partnerships Fund (fictional)','due':'2026-11-06','status':'Submitted','owner':'Partnerships lead'}],
        'evidence':[
        {'id':'E01','programme_id':'P01','item':'September attendance reconciliation','status':'Pending','due':'2026-10-21','owner':'MEL officer'},
        {'id':'E02','programme_id':'P01','item':'Learning assessment summary','status':'Verified','due':'2026-10-18','owner':'Education officer'},
        {'id':'E03','programme_id':'P02','item':'Training completion reconciliation','status':'Pending','due':'2026-10-18','owner':'Livelihoods lead'},
        {'id':'E04','programme_id':'P02','item':'Outcome follow-up survey','status':'Not collected','due':'2026-11-15','owner':'MEL officer'},
        {'id':'E05','programme_id':'P03','item':'Outreach tally validation','status':'Pending','due':'2026-10-25','owner':'Health programme lead'},
        {'id':'E06','programme_id':'P04','item':'Partner workshop completion summary','status':'Verified','due':'2026-10-15','owner':'Partnerships lead'}],
        'knowledge':[
        {'id':'K01','title':'Reporting evidence standard','text':'Report verified unique programme reach separately from pending records. Do not sum across programmes: participants may overlap and partner organisations are a different unit. Reach is an output, not evidence of impact.'},
        {'id':'K02','title':'Finance interpretation','text':'Available budget = approved budget minus recorded spending minus open commitments. A commitment is not a payment. Never combine NGN and USD without an approved exchange rate and reporting basis. Spending is not a measure of programme success.'},
        {'id':'K03','title':'Donor update review','text':'Drafts require programme, MEL and grants review before external use. Missing evidence must remain visible. Do not claim donor approval, submission, outcomes or causal impact.'},
        {'id':'K04','title':'Demonstration data boundary','text':'Use only the fictional aggregate programme records provided here. No beneficiary case files, personal contacts or safeguarding incident details are included. Role switching illustrates access rules, not authentication.'}],
        'tasks':[],'audit':[]}
class NGOTools:
    def __init__(self,state,role='director'):
        if role not in ROLES:raise ValueError('Unknown demo role.')
        self.state,self.role=state,role
    def programme(self,programme_id):
        return deepcopy(next(p for p in self.state['programmes'] if p['id']==programme_id))
    def programme_progress(self):
        return {'records':[{k:v for k,v in p.items() if k not in {'budget','spent','committed'}}|{'progress_pct':round(100*p['verified_unique_reach']/p['target'],1)} for p in self.state['programmes']], 'note':self.state['knowledge'][0]['text']}
    def reporting_queue(self):
        rows=[]
        for r in self.state['reports']:
            gap=[e['id'] for e in self.state['evidence'] if e['programme_id']==r['programme_id'] and e['status']!='Verified']
            rows.append(deepcopy(r)|{'days_to_due':(date.fromisoformat(r['due'])-date.fromisoformat(self.state['as_of'])).days,'overdue':r['status']!='Submitted' and r['due']<self.state['as_of'],'evidence_gaps':gap})
        return {'records':rows,'note':'Evidence gaps are programme-level review prompts, not a donor-compliance finding.'}
    def evidence_gaps(self):
        return {'records':[deepcopy(e) for e in self.state['evidence'] if e['status']!='Verified']}
    def budget_position(self):
        if self.role not in {'director','finance'}:raise PermissionError('Financial detail requires director or finance role.')
        rows=[{k:p[k] for k in ['id','programme','currency','budget','spent','committed']}|{'available':p['budget']-p['spent']-p['committed']} for p in self.state['programmes']]
        return {'records':rows,'note':self.state['knowledge'][1]['text']}
    def knowledge(self):return {'records':deepcopy(self.state['knowledge'])}
    def donor_draft(self,programme_id):
        p=self.programme(programme_id);gaps=[e for e in self.evidence_gaps()['records'] if e['programme_id']==programme_id]
        return {'programme_id':programme_id,'draft':f"DRAFT — INTERNAL REVIEW REQUIRED\n\n{p['programme']} ({programme_id}), as of {self.state['as_of']}: verified reach is {p['verified_unique_reach']} of {p['target']} {p['unit']} ({100*p['verified_unique_reach']/p['target']:.1f}%). A further {p['pending_verification']} records remain pending verification and are excluded.\n\nEvidence requiring review: "+('; '.join(e['id']+' — '+e['item'] for e in gaps) or 'No open evidence items recorded.')+'\n\nThese are delivery outputs, not measured outcomes or attributable impact. Review the supporting records and donor requirements before external use. No report has been submitted by this application.','sources':[programme_id]+[e['id'] for e in gaps]}
    def propose_followup(self,evidence_id):
        if self.role not in {'director','programme'}:raise PermissionError('Follow-up creation requires programme lead or director.')
        e=next((e for e in self.state['evidence'] if e['id']==evidence_id),None)
        if not e or e['status']=='Verified':raise ValueError('Choose an open evidence item.')
        if any(t['evidence_id']==evidence_id for t in self.state['tasks']):raise ValueError('A follow-up already exists for this item.')
        return {'evidence_id':e['id'],'programme_id':e['programme_id'],'task':'Review '+e['item'],'owner':e['owner'],'due':e['due']}
    def confirm_followup(self,proposal,confirmed=False):
        if not confirmed:raise ValueError('Review and confirm the proposed task first.')
        expected=self.propose_followup(proposal['evidence_id'])
        if proposal!=expected:raise ValueError('Proposal changed. Prepare a new proposal.')
        task={'id':f"T{len(self.state['tasks'])+1:03d}",**expected,'status':'Open'}
        self.state['tasks'].append(task);self.state['audit'].append({'action':'followup_created','actor':self.role,'date':self.state['as_of'],'record':deepcopy(task)})
        return task

def scenario_answer(t,message):
    q=message.lower();trace=[]
    def run(name,*args):
        result=getattr(t,name)(*args);trace.append({'tool':name,'result':result});return result
    if any(w in q for w in ['budget','spend','finance','commitment']):
        r=run('budget_position');text='### Budget position\n'+'\n'.join(f"- **{p['id']}**: {p['currency']} {p['available']:,} available after recorded spending and commitments." for p in r['records'])+'\n\n'+r['note']
    elif any(w in q for w in ['draft','donor update']):
        pid=next((p['id'] for p in t.state['programmes'] if p['id'].lower() in q),'P01');r=run('donor_draft',pid);text=r['draft']
    elif any(w in q for w in ['reach','progress','impact']):
        r=run('programme_progress');text='### Programme progress\n'+'\n'.join(f"- **{p['id']} · {p['programme']}**: {p['verified_unique_reach']}/{p['target']} {p['unit']} verified ({p['progress_pct']}%); {p['pending_verification']} pending." for p in r['records'])+'\n\n'+r['note']
    elif any(w in q for w in ['policy','rule','knowledge']):
        r=run('knowledge');text='\n\n'.join('**'+p['id']+' · '+p['title']+'**\n'+p['text'] for p in r['records'])
    elif any(w in q for w in ['report','deadline','priority','brief','evidence','follow']):
        r=run('reporting_queue');e=run('evidence_gaps');open_reports=[p for p in r['records'] if p['status']!='Submitted'];text='### Reporting priorities\n'+'\n'.join(f"- **{p['id']} / {p['programme_id']}**: {p['deliverable']}, due {p['due']}"+(' — overdue' if p['overdue'] else '')+f". Owner: {p['owner']}. Open evidence: {', '.join(p['evidence_gaps']) or 'none recorded'}." for p in sorted(open_reports,key=lambda p:p['due']))+f"\n\n{len(e['records'])} open programme evidence items. Prepare and confirm a follow-up in Action Lab; no email or report is sent."
    else:text='Scenario mode supports reporting priorities, programme progress, evidence gaps, budget position, policy and donor-update drafts. For open-ended conversation, configure Live AI. Try “What needs attention before the next donor report?”'
    return {'text':text,'trace':trace,'mode':'Guided scenario'}
