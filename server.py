"""Local fictional payment service. Python 3.11+, standard library only."""
import json, sqlite3, uuid, time, os
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

class Conflict(Exception): pass
class Store:
 def __init__(self, path):
  self.path=path
  with self.db() as db:
   db.executescript("""CREATE TABLE IF NOT EXISTS payments (id TEXT PRIMARY KEY, request_key TEXT UNIQUE NOT NULL, amount INTEGER NOT NULL, scenario TEXT NOT NULL, status TEXT NOT NULL, created TEXT DEFAULT CURRENT_TIMESTAMP);
   CREATE TABLE IF NOT EXISTS events (id TEXT PRIMARY KEY, payment_id TEXT NOT NULL, kind TEXT NOT NULL, created TEXT DEFAULT CURRENT_TIMESTAMP);""")
 def db(self):
  db=sqlite3.connect(self.path, timeout=10); db.row_factory=sqlite3.Row; return db
 def create(self, key, amount, scenario):
  if not isinstance(key,str) or not key.strip() or len(key)>128: raise ValueError('Invalid idempotency key')
  if type(amount)!=int or not 0<amount<=100000000: raise ValueError('Amount must be positive integer cents, max 100000000')
  if scenario not in ('approve','decline','lost_response'): raise ValueError('Invalid scenario')
  with self.db() as db:
   db.execute('BEGIN IMMEDIATE')
   old=db.execute('SELECT * FROM payments WHERE request_key=?',(key,)).fetchone()
   if old:
    if old['amount']!=amount or old['scenario']!=scenario: raise Conflict('Key already used with different payload')
    return dict(old),False
   pid=str(uuid.uuid4());status='declined' if scenario=='decline' else 'approved'
   db.execute('INSERT INTO payments(id,request_key,amount,scenario,status) VALUES(?,?,?,?,?)',(pid,key,amount,scenario,status))
   db.execute('INSERT INTO events(id,payment_id,kind) VALUES(?,?,?)',(str(uuid.uuid4()),pid,status))
   return dict(db.execute('SELECT * FROM payments WHERE id=?',(pid,)).fetchone()),True
 def list(self):
  with self.db() as db:return [dict(x) for x in db.execute('SELECT * FROM payments ORDER BY created DESC,rowid DESC')]
 def find(self,key):
  with self.db() as db:
   row=db.execute('SELECT * FROM payments WHERE request_key=?',(key,)).fetchone();return dict(row) if row else None
 def refund(self,pid):
  with self.db() as db:
   db.execute('BEGIN IMMEDIATE'); row=db.execute('SELECT * FROM payments WHERE id=?',(pid,)).fetchone()
   if not row:raise KeyError(pid)
   if row['status']=='declined':raise Conflict('Declined payment cannot be refunded')
   if row['status']=='approved':
    db.execute("UPDATE payments SET status='refunded' WHERE id=?",(pid,))
    db.execute('INSERT INTO events(id,payment_id,kind) VALUES(?,?,?)',(str(uuid.uuid4()),pid,'refunded'))
   return dict(db.execute('SELECT * FROM payments WHERE id=?',(pid,)).fetchone())
 def event(self,eid,pid,kind):
  if not isinstance(eid,str) or not eid.strip() or len(eid)>128:raise ValueError('Invalid event id')
  if kind not in ('approved','declined'):raise ValueError('Invalid event kind')
  with self.db() as db:
   db.execute('BEGIN IMMEDIATE')
   previous=db.execute('SELECT * FROM events WHERE id=?',(eid,)).fetchone()
   if previous:
    if previous['payment_id']!=pid or previous['kind']!=kind:raise Conflict('Event id reused with different payload')
    return {'duplicate':True}
   p=db.execute('SELECT * FROM payments WHERE id=?',(pid,)).fetchone()
   if not p:raise KeyError(pid)
   # Simulator events corroborate persisted state; they cannot resurrect refunds.
   expected='declined' if p['scenario']=='decline' else 'approved'
   if kind!=expected:raise Conflict('Event contradicts payment outcome')
   db.execute('INSERT INTO events(id,payment_id,kind) VALUES(?,?,?)',(eid,pid,kind))
   return {'duplicate':False}

def handler(store):
 class Handler(BaseHTTPRequestHandler):
  def send(self,status,data):
   payload=json.dumps(data).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(payload)));self.end_headers();self.wfile.write(payload)
  def do_GET(self):
   path=urlparse(self.path).path
   if path=='/':
    data=Path(__file__).with_name('dashboard.html').read_bytes();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.end_headers();self.wfile.write(data)
   elif path=='/health':self.send(200,{'status':'ok','mode':'simulation'})
   elif path=='/api/payments':self.send(200,store.list())
   elif path.startswith('/api/payments/by-key/'):
    p=store.find(path.rsplit('/',1)[1]);self.send(200 if p else 404,p or {'error':'Not found'})
   else:self.send(404,{'error':'Not found'})
  def do_POST(self):
   try:
    length=int(self.headers.get('Content-Length','0'))
    if not 0<length<=16384:raise ValueError('Invalid body size')
    body=json.loads(self.rfile.read(length));path=urlparse(self.path).path
    if path=='/api/payments':
     p,fresh=store.create(body.get('idempotencyKey'),body.get('amountInCents'),body.get('scenario','approve'))
     # Commit happened before this delayed response, demonstrating uncertain client outcome.
     if fresh and p['scenario']=='lost_response':time.sleep(5)
     self.send(201 if fresh else 200,p)
    elif path.startswith('/api/payments/') and path.endswith('/refund'):self.send(200,store.refund(path.split('/')[3]))
    elif path=='/api/events':self.send(200,store.event(body.get('eventId'),body.get('paymentId'),body.get('kind')))
    else:self.send(404,{'error':'Not found'})
   except Conflict as e:self.send(409,{'error':str(e)})
   except KeyError:self.send(404,{'error':'Not found'})
   except (ValueError,TypeError,AttributeError) as e:self.send(400,{'error':str(e)})
   except (BrokenPipeError,ConnectionResetError):pass
 return Handler

if __name__=='__main__':
 server=ThreadingHTTPServer((os.getenv('HOST','127.0.0.1'),int(os.getenv('PORT','8080'))),handler(Store(os.getenv('PAYMENTS_DB','payments.sqlite3'))))
 print('Simulation console on http://%s:%s'%server.server_address,flush=True);server.serve_forever()
