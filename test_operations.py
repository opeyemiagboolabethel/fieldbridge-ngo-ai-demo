import unittest
from copy import deepcopy
from operations import NGOTools,load_state,scenario_answer
class NGOTests(unittest.TestCase):
    def setUp(self):self.t=NGOTools(load_state())
    def test_budgets(self):
        rows=self.t.budget_position()['records'];self.assertEqual([r['available'] for r in rows],[10400000,7100000,7800000,23000]);self.assertEqual(rows[-1]['currency'],'USD')
    def test_reach(self):
        p=self.t.programme_progress()['records'][1];self.assertEqual(p['progress_pct'],73.3);self.assertEqual(p['verified_unique_reach'],176);self.assertEqual(p['pending_verification'],22);self.assertNotIn('budget',p)
    def test_deadlines(self):
        rows=self.t.reporting_queue()['records'];self.assertEqual(sum(r['overdue'] for r in rows),1);self.assertEqual(rows[1]['days_to_due'],-1);self.assertFalse(rows[3]['overdue'])
    def test_no_write_without_confirmation(self):
        p=self.t.propose_followup('E03');self.assertEqual(self.t.state['tasks'],[])
        with self.assertRaises(ValueError):self.t.confirm_followup(p)
        self.assertEqual(self.t.state['audit'],[])
    def test_confirm_and_duplicate(self):
        p=self.t.propose_followup('E03');task=self.t.confirm_followup(p,True);self.assertEqual(task['id'],'T001');self.assertEqual(len(self.t.state['audit']),1)
        with self.assertRaises(ValueError):self.t.confirm_followup(p,True)
    def test_permissions(self):
        with self.assertRaises(PermissionError):NGOTools(load_state(),'programme').budget_position()
        with self.assertRaises(PermissionError):NGOTools(load_state(),'finance').propose_followup('E03')
    def test_tamper_and_closed(self):
        p=self.t.propose_followup('E03');p['owner']='Other person'
        with self.assertRaises(ValueError):self.t.confirm_followup(p,True)
        with self.assertRaises(ValueError):self.t.propose_followup('E02')
        self.assertEqual(self.t.state['tasks'],[])
    def test_draft_and_scenarios(self):
        text=self.t.donor_draft('P02')['draft'];self.assertIn('176 of 240',text);self.assertIn('22 records remain pending',text)
        for q in ['report priorities','programme progress','budget availability','draft P02 update','policy','unrecognised']:
            self.assertTrue(scenario_answer(self.t,q)['text'])
    def test_session_isolation(self):
        other=load_state();self.t.confirm_followup(self.t.propose_followup('E03'),True);self.assertEqual(other['tasks'],[])
if __name__=='__main__':unittest.main()
