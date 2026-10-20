import unittest
from streamlit.testing.v1 import AppTest
class UITests(unittest.TestCase):
    def test_render_and_roles(self):
        at=AppTest.from_file('streamlit_app.py').run(timeout=30);self.assertEqual(len(at.exception),0)
        at.sidebar.selectbox[0].select('programme').run();self.assertEqual(len(at.exception),0)
        at.sidebar.selectbox[0].select('finance').run();self.assertEqual(len(at.exception),0)
    def test_chat(self):
        at=AppTest.from_file('streamlit_app.py').run(timeout=30);at.chat_input[0].set_value('report priorities').run();self.assertEqual(len(at.exception),0);self.assertEqual(len(at.chat_message),2)
if __name__=='__main__':unittest.main()
