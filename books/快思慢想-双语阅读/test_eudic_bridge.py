"""Checks routing without contacting any real Eudic account."""
import unittest
from unittest.mock import patch
import eudic_server as bridge

class BridgeTests(unittest.TestCase):
    def setUp(self):
        p=patch.object(bridge.credential_store,'save');p.start();self.addCleanup(p.stop)
        p=patch.object(bridge.credential_store,'forget');p.start();self.addCleanup(p.stop)
        bridge.AUTH='';bridge.TARGET=None;bridge.CATEGORIES=[]
    def test_no_auth_no_write(self):
        with patch.object(bridge,'remote') as api:
            with self.assertRaises(bridge.APIError):bridge.dispatch('/api/collect',{'word':'thinking'})
            api.assert_not_called()
    def test_explicit_target_and_no_secret_in_response(self):
        with patch.object(bridge,'remote',return_value={'data':[{'id':'123456789012345678','name':'Reading'}]}) as api:
            result=bridge.dispatch('/api/connect',{'token':'NIS test-only'})
            self.assertNotIn('token',result)
            api.assert_called_once_with('GET','category?language=en',auth='NIS test-only')
        with patch.object(bridge,'remote') as api:
            with self.assertRaises(bridge.APIError):bridge.dispatch('/api/collect',{'word':'thinking'})
            api.assert_not_called()
        bridge.dispatch('/api/target',{'id':'123456789012345678'})
        with patch.object(bridge,'remote',return_value={'message':'ok'}) as api:
            bridge.dispatch('/api/collect',{'word':'thinking'})
            api.assert_called_once_with('POST','words',{'language':'en','category_id':'123456789012345678','words':['thinking']})
        bridge.dispatch('/api/disconnect',{})
        self.assertEqual(bridge.AUTH,'');self.assertIsNone(bridge.TARGET)
    def test_existing_named_book_reused(self):
        bridge.AUTH='NIS test-only'
        with patch.object(bridge,'remote',return_value={'data':[{'id':'42','name':'Reading'}]}) as api:
            result=bridge.dispatch('/api/create',{'name':'Reading'})
            self.assertEqual(result['target']['id'],'42')
            self.assertEqual(api.call_count,1)
            self.assertEqual(api.call_args.args[0],'GET')
    def test_reject_sentence_and_unknown_target(self):
        bridge.AUTH='NIS test-only';bridge.TARGET={'id':'42','name':'Reading'}
        with patch.object(bridge,'remote') as api:
            for word in ['<script>x</script>','中文','a sentence.','a'*81]:
                with self.assertRaises(bridge.APIError):bridge.dispatch('/api/collect',{'word':word})
            with self.assertRaises(bridge.APIError):bridge.dispatch('/api/target',{'id':'not-listed'})
            api.assert_not_called()

if __name__=='__main__':unittest.main()
