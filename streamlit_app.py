"""FieldBridge Foundation AI — a fictional NGO operating workspace."""
import json,os
import pandas as pd
import streamlit as st
from operations import NGOTools,ROLES,load_state
from agent import ask,safe_error_message,log_private_diagnostic
st.set_page_config(page_title='FieldBridge Foundation AI | ONE Light Analytics',page_icon='◈',layout='wide')
st.markdown('''<style>.stApp{background:#f6f4ee;color:#122c35}.block-container{padding-top:2rem;padding-bottom:3rem}.hero{padding:34px 38px;border-radius:18px;background:linear-gradient(115deg,#0b2530,#28574e);color:white;margin-bottom:24px}.hero h1{color:white;font-size:3rem;line-height:1.1;margin:14px 0}.hero p{color:#e0e8e6;max-width:800px}.kicker{font-size:12px;letter-spacing:.15em;color:#e4bd7a}.stButton button{min-height:44px;height:auto;white-space:normal}.stButton button p,.stButton button [data-testid="stMarkdownContainer"]{white-space:normal!important;overflow:visible!important;text-overflow:clip!important;overflow-wrap:anywhere;line-height:1.45}.stButton button p{-webkit-line-clamp:unset!important}.hero h1{overflow-wrap:break-word}@media(max-width:640px){.hero{padding:24px}.hero h1{font-size:2.1rem}}[data-testid="stMetric"]{background:white;border:1px solid #d8dfd8;border-radius:12px;padding:16px}[data-testid="stMetricValue"]{color:#163e43}</style>''',unsafe_allow_html=True)
for k,v in [('fb_state',load_state()),('fb_messages',[])]:
    if k not in st.session_state:st.session_state[k]=v
with st.sidebar:
    st.subheader('FieldBridge Foundation AI');st.caption('Programme evidence → clearer decisions')
    st.link_button('ONE Light Analytics','https://onelightanalytics.com/')
    role=st.selectbox('Explore a demo role',list(ROLES),format_func=ROLES.get)
    key=os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY','')
    if not key:
        try:key=st.secrets.get('GEMINI_API_KEY','') or st.secrets.get('GOOGLE_API_KEY','')
        except Exception:key=''
    model=os.getenv('GEMINI_MODEL','gemini-3.5-flash-lite')
    try:model=st.secrets.get('GEMINI_MODEL',model)
    except Exception:pass
    mode=st.radio('Conversation mode',['Guided scenario']+(['Live AI'] if key else []))
    st.caption('Guided scenario uses deterministic answers. Live AI uses Gemini when a private API key is configured. This is not an OpenAI product.')
    if st.button('Reset demonstration'):
        for k in list(st.session_state):
            if k.startswith('fb_'):del st.session_state[k]
        st.rerun()
    st.caption('Fictional aggregate records · Fixed date: 20 October 2026. Role switching demonstrates permissions; it is not a secure login.')
if st.session_state.get('fb_context')!=(role,mode):
    st.session_state.fb_context=(role,mode);st.session_state.fb_messages=[];st.session_state.pop('fb_proposal',None);st.session_state.pop('fb_pending',None)
t=NGOTools(st.session_state.fb_state,role)
st.markdown('''<div class="hero"><div class="kicker">ONE LIGHT ANALYTICS · NGO & SOCIAL IMPACT</div><h1>Less chasing.<br>More time for the mission.</h1><p>FieldBridge Foundation AI connects programme progress, donor deadlines and the evidence your team needs to act confidently.</p><p>Ask a question. Check the records. Review the next step.</p></div>''',unsafe_allow_html=True)
st.caption('Fictional NGO · Four programmes · Education, livelihoods, community health and partner capacity · Nigeria with regional partnerships')
with st.expander('Start here · a three-minute walkthrough',expanded=False):
    st.markdown('**1.** Open AI Assistant and ask what needs attention before the next donor report.\n\n**2.** Inspect R02 and E03 in Evidence Desk: the deadline passed, but evidence still needs review.\n\n**3.** In Action Lab, prepare an E03 follow-up, review its owner and due date, then confirm. Inspect the session audit.\n\n**4.** Draft a P02 donor update. Notice that pending records stay separate and no impact claim is invented.')
board,chat,desk,lab=st.tabs(['Mission overview','AI Assistant','Evidence Desk','Action Lab'])
def table(rows):st.dataframe(pd.DataFrame(rows),hide_index=True,width='stretch')

FIELD_LABELS={
    'id':'Record reference','programme_id':'Programme reference','programme':'Programme',
    'deliverable':'Report or deliverable','donor':'Donor','due':'Due date','status':'Status',
    'owner':'Responsible person','days_to_due':'Days until due','overdue':'Overdue',
    'evidence_gaps':'Evidence to review','item':'Evidence item','location':'Location',
    'currency':'Currency','budget':'Approved budget','spent':'Recorded spending',
    'committed':'Open commitments','available':'Available budget','target':'Target',
    'verified_unique_reach':'Verified unique reach','pending_verification':'Pending verification',
    'unit':'Reporting unit','progress_pct':'Verified progress (%)','title':'Guidance',
    'text':'Detail','evidence_id':'Evidence reference','task':'Follow-up task',
    'actor':'Recorded by','action':'Action','date':'Recorded date','record':'Task details',
    'draft':'Internal draft','sources':'Source references'
}
SOURCE_LABELS={
    'reporting_queue':'Donor reporting calendar','programme_progress':'Programme delivery records',
    'evidence_gaps':'Evidence awaiting review','budget_position':'Programme budget records',
    'knowledge':'Reporting and finance guidance','donor_draft':'Sources for the donor-update draft',
    'propose_followup':'Proposed evidence follow-up','session_audit':'Confirmed session actions'
}
def readable_value(value):
    if value is None:return 'Not recorded'
    if isinstance(value,bool):return 'Yes' if value else 'No'
    if isinstance(value,list):
        return '; '.join(readable_value(item) for item in value) if value else 'None recorded'
    if isinstance(value,dict):
        return '; '.join(FIELD_LABELS.get(str(k),str(k).replace('_',' ').capitalize())+': '+readable_value(v) for k,v in value.items())
    if isinstance(value,(int,float)):return format(value,',')
    return str(value)

def readable_record(record):
    if not isinstance(record,dict):
        st.text(readable_value(record))
        return
    st.table(pd.DataFrame([
        {'Field':FIELD_LABELS.get(str(k),str(k).replace('_',' ').capitalize()),'Detail':readable_value(v)}
        for k,v in record.items()
    ]))

def show_evidence(trace):
    if not trace:
        st.caption('No programme records were retrieved for this response.')
        return
    st.caption('These are the demonstration records used for this answer. References match the Evidence Desk.')
    for entry in trace:
        st.markdown('**'+SOURCE_LABELS.get(entry.get('tool',''),'Supporting records')+'**')
        result=entry.get('result',{})
        if not isinstance(result,dict):
            st.text(readable_value(result))
            continue
        if result.get('error'):
            st.info(str(result['error']))
            continue
        records=result.get('records')
        if isinstance(records,list):
            if not records:st.caption('No matching records.')
            for record in records:
                readable_record(record)
        else:
            readable_record({k:v for k,v in result.items() if k!='note'})
        if result.get('note'):st.caption(str(result['note']))

with board:
    queue=t.reporting_queue()['records'];gaps=t.evidence_gaps()['records']
    cols=st.columns(3)
    for col,(label,value) in zip(cols,[('Active programmes',4),('Overdue reports',sum(r['overdue'] for r in queue)),('Evidence items to review',len(gaps))]):col.metric(label,value)
    st.subheader('Delivery progress, with evidence kept in view')
    for p in t.programme_progress()['records']:
        with st.container(border=True):
            a,b=st.columns([3,1]);a.markdown(f"**{p['programme']} · {p['id']}**");a.caption(p['location']+' · '+p['unit']);b.metric('Verified / target',f"{p['verified_unique_reach']} / {p['target']}");st.progress(min(p['progress_pct']/100,1));st.caption(f"{p['progress_pct']}% of target verified · {p['pending_verification']} pending verification, excluded from verified reach")
    st.info('Programme outputs are not demonstrated impact. Reach is not added across programmes because units differ and participants may overlap.')
    st.subheader('Next reporting commitments');table(queue)
    if role in {'director','finance'}:
        st.subheader('Funding visibility');table(t.budget_position()['records']);st.caption(t.budget_position()['note'])
with chat:
    left,right=st.columns([1.8,1])
    with left:
        st.subheader('Ask FieldBridge Foundation AI')
        for m in st.session_state.fb_messages:
            with st.chat_message(m['role']):
                st.markdown(m['content'])
                if m.get('trace'):
                    with st.expander('Sources used for this answer'):show_evidence(m['trace'])
        message=st.chat_input('What needs attention before the next donor report?')
        if st.session_state.get('fb_pending'):message=st.session_state.pop('fb_pending')
        if message:
            history=st.session_state.fb_messages.copy();st.session_state.fb_messages.append({'role':'user','content':message})
            with st.chat_message('user'):st.markdown(message)
            with st.chat_message('assistant'):
                try:
                    with st.spinner('Checking the programme records…'):response=ask(t,message,key,mode=='Live AI',history,model=model)
                    st.markdown(response['text']);st.caption(response['mode'])
                    with st.expander('Sources used for this answer'):show_evidence(response['trace'])
                    st.session_state.fb_messages.append({'role':'assistant','content':response['text'],'trace':response['trace']})
                except PermissionError as e:st.info(str(e))
                except Exception as error:
                    log_private_diagnostic(error,key)
                    st.error(safe_error_message(error))
    with right:
        st.markdown('#### Try an operating question')
        prompts=[
            ('Reporting priorities','What needs attention before the next donor report?'),
            ('Programme progress','Show verified programme progress and pending records.'),
            ('Draft a donor update','Draft a donor update for P02.'),
            ('Reporting guidance','Explain the reporting policy.'),
        ]
        if role in {'director','finance'}:
            prompts.append(('Available budget','Show budget availability after commitments.'))
        for i,(label,prompt) in enumerate(prompts):
            with st.container(border=True):
                st.caption(prompt)
                if st.button(label,key=f'prompt{i}',width='stretch'):
                    st.session_state.fb_pending=prompt
                    st.rerun()
        st.caption('Answers should connect to programme IDs and evidence. Review all drafts before use. This public demo has no beneficiary records or real donor data.')
with desk:
    st.subheader('Trace each answer back to the evidence')
    choices=['Programme progress','Reporting calendar','Evidence gaps','Operating guidance']+(['Budget records'] if role in {'director','finance'} else [])
    choice=st.selectbox('Choose a record collection',choices)
    method={'Programme progress':'programme_progress','Reporting calendar':'reporting_queue','Evidence gaps':'evidence_gaps','Operating guidance':'knowledge','Budget records':'budget_position'}[choice]
    records=getattr(t,method)()['records'];table(records);st.download_button('Download this evidence table',pd.DataFrame(records).to_csv(index=False),'fieldbridge-evidence.csv','text/csv')
    st.subheader('Prepare a donor-update draft')
    pid=st.selectbox('Programme',[p['id'] for p in t.state['programmes']],format_func=lambda p:p+' · '+t.programme(p)['programme'])
    draft=t.donor_draft(pid);st.text_area('Internal draft · not submitted',draft['draft'],height=240);st.download_button('Download internal draft',draft['draft'],f'FieldBridge-{pid}-draft.txt','text/plain')
with lab:
    st.subheader('Turn a reporting gap into an accountable next step')
    st.caption('Prepare → review → confirm. Changes stay in your browser session; no email, donor submission or external task is created.')
    if role in {'director','programme'}:
        available=[e for e in t.evidence_gaps()['records'] if not any(x['evidence_id']==e['id'] for x in t.state['tasks'])]
        if available:
            eid=st.selectbox('Evidence item requiring follow-up',[e['id'] for e in available],format_func=lambda i:next(e['id']+' · '+e['item'] for e in available if e['id']==i))
            if st.button('Prepare follow-up proposal'):st.session_state.fb_proposal=t.propose_followup(eid)
        else:st.success('Each open evidence item has a session follow-up.')
        proposal=st.session_state.get('fb_proposal')
        if proposal:
            with st.container(border=True):
                st.markdown('**Review proposed task**');readable_record(proposal)
                if proposal['due']<t.state['as_of']:st.warning('The original evidence deadline has passed. This task preserves that deadline; the team must agree a recovery date.')
                with st.form('confirm_task'):
                    confirm=st.checkbox('I have reviewed this simulated task and its owner.');submit=st.form_submit_button('Confirm session follow-up')
                if submit:
                    try:
                        task=t.confirm_followup(proposal,confirm);st.session_state.pop('fb_proposal',None);st.success(task['id']+' recorded in this session only.');st.rerun()
                    except (ValueError,PermissionError) as e:st.error(str(e))
    else:st.info('Finance can inspect funding; programme leadership approves evidence follow-ups.')
    st.markdown('#### Session task register');table(t.state['tasks'])
    with st.expander('Review confirmed session actions'):show_evidence([{'tool':'session_audit','result':{'records':t.state['audit']}}])
    st.download_button('Download session audit',json.dumps(t.state['audit'],indent=2),'fieldbridge-session-audit.json','application/json')
st.divider();st.caption('FieldBridge Foundation and all donors, budgets, programmes and records are fictional. This is a demonstration of workflow support, not a client case study or a production grant-management platform. No funding, beneficiary eligibility or safeguarding decisions are automated.')
