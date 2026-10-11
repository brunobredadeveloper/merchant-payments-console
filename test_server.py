import unittest,tempfile,concurrent.futures,json,threading,urllib.request,urllib.error
from http.server import ThreadingHTTPServer
from server import Store,Conflict,handler
class PaymentsTests(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.path=self.tmp.name+'/db';self.store=Store(self.path)
 def tearDown(self):self.tmp.cleanup()
 def test_replay_survives_restart(self):
  p,_=self.store.create('key',2590,'approve');q,fresh=Store(self.path).create('key',2590,'approve');self.assertEqual(p,q);self.assertFalse(fresh)
 def test_changed_payload_conflicts(self):
  self.store.create('k',10,'approve')
  with self.assertRaises(Conflict):self.store.create('k',11,'approve')
 def test_concurrent_retries_one_payment(self):
  with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:r=list(pool.map(lambda _:self.store.create('k',10,'approve'),range(16)))
  self.assertEqual(len(self.store.list()),1);self.assertEqual(sum(f for _,f in r),1)
 def test_invalid_amounts(self):
  for amount in [True,0,-1,1.1,'10',100000001]:
   with self.assertRaises(ValueError):self.store.create('k',amount,'approve')
 def test_refund_idempotent(self):
  p,_=self.store.create('k',10,'approve');self.assertEqual(self.store.refund(p['id']),self.store.refund(p['id']))
 def test_decline_cannot_refund(self):
  p,_=self.store.create('k',10,'decline')
  with self.assertRaises(Conflict):self.store.refund(p['id'])
 def test_duplicate_event_and_payload_conflict(self):
  p,_=self.store.create('k',10,'approve');self.assertFalse(self.store.event('e',p['id'],'approved')['duplicate']);self.assertTrue(self.store.event('e',p['id'],'approved')['duplicate'])
  with self.assertRaises(Conflict):self.store.event('e',p['id'],'declined')
 def test_late_event_preserves_refund(self):
  p,_=self.store.create('k',10,'approve');self.store.refund(p['id']);self.store.event('late',p['id'],'approved');self.assertEqual(self.store.find('k')['status'],'refunded')
 def test_lost_response_already_committed(self):
  p,_=self.store.create('k',10,'lost_response');self.assertEqual(self.store.find('k')['status'],'approved')
 def test_http_timeout_then_reconcile(self):
  s=ThreadingHTTPServer(('127.0.0.1',0),handler(self.store));t=threading.Thread(target=s.serve_forever,daemon=True);t.start()
  try:
   base='http://127.0.0.1:%s'%s.server_port
   body=json.dumps({'idempotencyKey':'lost','amountInCents':123,'scenario':'lost_response'}).encode()
   with self.assertRaises(TimeoutError):urllib.request.urlopen(urllib.request.Request(base+'/api/payments',body,{'Content-Type':'application/json'}),timeout=0.2)
   with urllib.request.urlopen(base+'/api/payments/by-key/lost') as response:self.assertEqual(json.load(response)['status'],'approved')
   self.assertEqual(len(self.store.list()),1)
  finally:s.shutdown();s.server_close();t.join()
 def test_http_validation_and_replay(self):
  s=ThreadingHTTPServer(('127.0.0.1',0),handler(self.store));t=threading.Thread(target=s.serve_forever,daemon=True);t.start()
  try:
   url='http://127.0.0.1:%s/api/payments'%s.server_port
   def post(body):return urllib.request.urlopen(urllib.request.Request(url,json.dumps(body).encode(),{'Content-Type':'application/json'}))
   body={'idempotencyKey':'http','amountInCents':100,'scenario':'approve'}
   with post(body) as a:self.assertEqual(a.status,201);pid=json.load(a)['id']
   with post(body) as b:self.assertEqual(b.status,200);self.assertEqual(json.load(b)['id'],pid)
   with self.assertRaises(urllib.error.HTTPError) as e:post(dict(body,amountInCents=200))
   self.assertEqual(e.exception.code,409)
  finally:s.shutdown();s.server_close();t.join()
if __name__=='__main__':unittest.main()
