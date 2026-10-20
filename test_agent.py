"""Real SDK request serialisation with mocked HTTP; no real API key or network."""
import json,unittest
from unittest.mock import patch
import httpx
from google import genai
from google.genai import types
from agent import ask
from operations import NGOTools,load_state
class ClientLifetimeTests(unittest.TestCase):
    def exercise(self,tool_call=False):
        original=genai.Client;requests=[];transports=[]
        def respond(request):
            payload=json.loads(request.content);requests.append(payload)
            if tool_call and len(requests)==1:
                part={'functionCall':{'name':'reporting_queue','args':{}}}
            else:part={'text':'Hello. I can help with programme reporting.'}
            return httpx.Response(200,json={'candidates':[{'content':{'role':'model','parts':[part]},'finishReason':'STOP'}]})
        def factory(**kwargs):
            # Deliberately retain no Client reference outside the production code.
            transport=httpx.MockTransport(respond)
            client=original(api_key='test-key-not-real',http_options=types.HttpOptions(client_args={'transport':transport,'trust_env':False},async_client_args={'trust_env':False}))
            transports.append(client._api_client._httpx_client)
            return client
        with patch('google.genai.Client',side_effect=factory):
            result=ask(NGOTools(load_state()),'reporting priorities' if tool_call else 'Hello','test-key-not-real',True)
        self.assertEqual(result['mode'],'Live AI');self.assertTrue(result['text'].startswith('Hello'))
        self.assertEqual(len(requests),2 if tool_call else 1)
        self.assertTrue(all(h.is_closed for h in transports))
        if tool_call:self.assertEqual(result['trace'][0]['tool'],'reporting_queue')
    def test_greeting_client_stays_open(self):self.exercise()
    def test_tool_roundtrip_client_stays_open(self):self.exercise(True)
if __name__=='__main__':unittest.main()
