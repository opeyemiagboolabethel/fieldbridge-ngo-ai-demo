# FieldBridge Foundation AI
ONE Light Analytics' NGO and social-impact demonstration. FieldBridge and all records/donors are fictional. No client results are implied.

## Experience
- Conversational programme and reporting assistant with tool evidence.
- Verified reach and pending records kept separate; no cross-programme reach total or fabricated impact.
- Donor deadlines, programme evidence gaps and sourced internal update drafts.
- Spending, commitments and availability; NGN/USD kept separate.
- Human-reviewed follow-up proposals, session-only confirmation and audit export.
- Director, programme/MEL and finance views. Demo role selector is not authentication.

## Run
Python 3.11+:
```
pip install -r requirements.txt
streamlit run streamlit_app.py
```
Guided scenario mode needs no key and is explicitly deterministic, not a language model. For live AI, configure GEMINI_API_KEY or GOOGLE_API_KEY privately in Streamlit Secrets. Never commit keys. Default GEMINI_MODEL is gemini-flash-latest; set an available model for your account if needed. API quotas/charges depend on your provider plan. The interface is conversational; this is not OpenAI ChatGPT.

## Independent deployment
Create the separate GitHub repository `fieldbridge-ngo-ai-demo` with a README, then publish these files there. In Streamlit Community Cloud choose that repository, `main`, and `streamlit_app.py`. Suggested app subdomain `fieldbridge-ngo-ai-demo`, subject to availability. Configure secrets for this app independently. Verify the live URL before adding the website's launch button.

## Walkthrough
1. Ask: What needs attention before the next donor report?
2. Inspect R02 and E03; compare the fixed date 20 October 2026.
3. Prepare E03 follow-up in Action Lab; confirm and inspect the audit.
4. Draft P02 donor update. Pending 22 are excluded from verified 176/240.
5. Switch to Finance and inspect availability without combining currencies.

## Verification
`python -m unittest -v test_operations.py`
`python -m unittest -v test_ui.py` (requires Streamlit)
No external model call is required for these tests. Live AI requires a configured key and separate acceptance test.

## Production boundary
No real uploads, messaging, submissions, personal data, access control or persistent task integration. Production requires authenticated roles, data controls, durable storage, organisational approvals and agreed donor reporting rules. This demo uses aggregate records only. No eligibility, safeguarding or funding decisions.

## Training use
A short workshop can teach staff to ask a focused question, verify IDs and denominators, recognise missing evidence, review a draft and approve an accountable next step. Training outreach and commercial offers are planned separately.
