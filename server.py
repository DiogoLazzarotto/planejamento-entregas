"""Servidor local: python server.py --port 8000 --db planner.db."""
import argparse,json,sqlite3
from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlparse
from planner import connect,initialize,create_order,create_trip,assign,change_status,snapshot
BASE=Path(__file__).resolve().parent

def handler(db):
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(BASE/'web'),**kwargs)
        def end_headers(self):
            self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('Content-Security-Policy',"default-src 'self'; style-src 'self'; script-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
            super().end_headers()
        def respond(self,status,payload):
            body=json.dumps(payload,ensure_ascii=False).encode()
            self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
        def do_GET(self):
            if urlparse(self.path).path=='/api/state':
                c=connect(db)
                try:self.respond(200,snapshot(c))
                finally:c.close()
            else:super().do_GET()
        def do_POST(self):
            routes={'/api/orders':create_order,'/api/trips':create_trip,'/api/assign':assign,'/api/status':change_status}
            action=routes.get(urlparse(self.path).path)
            if not action:return self.respond(404,{'error':'Rota inexistente'})
            if self.headers.get('Content-Type','').split(';')[0]!='application/json':return self.respond(415,{'error':'Envie application/json'})
            c=None
            try:
                length=int(self.headers.get('Content-Length','0'))
                if not 0<length<=16384:raise ValueError('Tamanho de requisição inválido')
                data=json.loads(self.rfile.read(length))
                if not isinstance(data,dict):raise ValueError('Envie um objeto JSON')
                c=connect(db);result=action(c,data);self.respond(200,{'ok':True,'id':result})
            except (ValueError,UnicodeDecodeError) as e:self.respond(400,{'error':str(e)})
            except sqlite3.Error:self.respond(500,{'error':'Não foi possível gravar. Tente novamente.'})
            finally:
                if c:c.close()
    return Handler

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--port',type=int,default=8000);ap.add_argument('--db',default=str(BASE/'planner.db'));args=ap.parse_args()
    c=connect(args.db);initialize(c);c.close()
    server=ThreadingHTTPServer(('127.0.0.1',args.port),handler(args.db))
    print(f'Planejador local: http://127.0.0.1:{args.port}',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
if __name__=='__main__':main()
