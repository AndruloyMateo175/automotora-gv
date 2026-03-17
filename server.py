#!/usr/bin/env python3
import json, sqlite3, hashlib, os, secrets
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

PORT    = int(os.environ.get('PORT', 8765))
DB_PATH = '/data/automotora.db'

USERS = {
    'aacosta':    {'hash': hashlib.sha256(b'cincoestrellas').hexdigest(), 'nombre': 'A. Acosta',    'rol': 'Admin'},
    'gvillasuso': {'hash': hashlib.sha256(b'cincoestrellas').hexdigest(), 'nombre': 'G. Villasuso', 'rol': 'Vendedor'},
    'gyozzi':     {'hash': hashlib.sha256(b'cincoestrellas').hexdigest(), 'nombre': 'G. Yozzi',     'rol': 'Vendedor'},
}
SESSIONS = {}

def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS compras (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT, proveedor TEXT, comprobante TEXT,
        precio_usd REAL, moneda TEXT, detalle TEXT
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS ventas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT, cliente TEXT, detalle TEXT,
        precio_usd REAL, moneda TEXT, comprobante TEXT
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT, tipo_doc TEXT, documento TEXT,
        telefono TEXT, email TEXT, pais TEXT
    )''')
    conn.commit()
    conn.close()

def auto_import():
    conn = get_db()
    count = conn.execute('SELECT COUNT(*) FROM compras').fetchone()[0]
    conn.close()
    if count > 0:
        return
    try:
        with open('compras_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        conn = get_db()
        for r in data:
            conn.execute(
                'INSERT INTO compras (fecha,proveedor,comprobante,precio_usd,moneda,detalle) VALUES (?,?,?,?,?,?)',
                (r.get('fecha',''), r.get('proveedor',''), r.get('comprobante',''),
                 float(r.get('precio_usd',0)), r.get('moneda','USD'), r.get('detalle',''))
            )
        conn.commit()
        conn.close()
        print('Auto-import: ' + str(len(data)) + ' compras')
    except Exception as e:
        print('Auto-import error: ' + str(e))

def check_auth(handler):
    tok = handler.headers.get('Authorization','').replace('Bearer ','').strip()
    return SESSIONS.get(tok)

HTML = open('index.html', 'rb').read() if os.path.exists('index.html') else b'<h1>AutomotoraGV</h1>'

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def send_json(self, data, code=200):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header('Content-Type','application/json')
        self.send_header('Access-Control-Allow-Origin','*')
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin','*')
        self.send_header('Access-Control-Allow-Methods','GET,POST,DELETE,OPTIONS')
        self.send_header('Access-Control-Allow-Headers','Content-Type,Authorization')
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        qs   = parse_qs(urlparse(self.path).query)

        if path in ('/', '/index.html'):
            self.send_response(200)
            self.send_header('Content-Type','text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML)
            return

        usr = check_auth(self)
        if not usr:
            self.send_json({'error':'unauthorized'}, 401)
            return

        conn = get_db()

        if path == '/api/stats':
            c = conn.execute('SELECT COUNT(*) FROM compras').fetchone()[0]
            v = conn.execute('SELECT COUNT(*) FROM ventas').fetchone()[0]
            l = conn.execute('SELECT COUNT(*) FROM clientes').fetchone()[0]
            conn.close()
            self.send_json({'单投管元':c,'ventas':v,'clientes':l})

        elif path == '/api/compras':
            limit  = int(qs.get('limit',['50'])[0])
            offset = int(qs.get('offset',['0'])[0])
            q      = qs.get('q',[''])[0]
            if q:
                rows = conn.execute("SELECT * FROM compras WHERE proveedor LIKE ? OR detalle LIKE ? OR comprobante LIKE ? ORDER BY fecha DESC LIMIT ? OFFSET ?",
                    ('%'+q+'%','%'+�+'%','%'+q+'%',limit,offset)).fetchall()
                total = conn.execute("SELECT COUNT(*) FROM compras WHERE proveedor LIKE ? OR detalle LIKE ? OR comprobante LIKE ?",
                    ('%'+q+'%','%'+q+'%','%'+q+'%')).fetchone()[0]
            else:
                rows = conn.execute('SELECT * FROM compras ORDER BY fecha DESC LIMIT ? OFFSET ?',(limit,offset)).fetchall()
                total = conn.execute('SELECT COUNT(*) FROM compras').fetchone()[0]
            conn.close()
            self.send_json({'data':[lict(r) for r in rows],'total':total})

        elif path == '/api/ventas':
            limit  = int(qs.get('limit',['50'])[0])
            offset = int(qs.get('offset',['0'])[0])
            q      = qs.get('q',[''])[0]
            if q:
                rows = conn.execute("SELECT * FROM ventas WHERE cliente LIKE ? OR detalle LIKE ? ORDER BY fecha DESC LIMIT ? OFFSET ?",
                    ('%'+q+'%','%'+q+'%',limit,offset)).fetchall()
                total = conn.execute("SELECT COUNT(*) FROM ventas WHERE cliente LIKE ? OR detalle LIKE ?",
                    ('%'+q+'%','%'+q+'%')).fetchone()[0]
            else:
                rows = conn.execute('SELECT * FROM ventas ORDER BY fecha DESC LIMIT ? OFFSET ?',(limit,offset)).fetchall()
                total = conn.execute('SELECT COUNT(*) FROM ventas').fetchone()[0]
            conn.close()
            self.send_json({'data':[dict(r) for r in rows],'total':total})

        elif path == '/api/clientes':
            limit  = int(qs.get('limit',['50'])[0])
            offset = int(qs.get('offset',['0'])[0])
            q      = qs.get('q',[''])[0]
            if q:
                rows = conn.execute("SELECT * FROM clientes WHERE nombre LIKE ? OR documento LIKE ? ORDER BY nombre LIMIT ? OFFSET ?",
                    ('%'+q+'%','%'+q+'%',limit,offset)).fetchall()
                total = conn.execute("SELECT COUNT(*) FROM clientes WHERE nombre LIKE ? OR documento LIKE ?",
                    ('%'+q+'%','%'+q+'%')).fetchone()[0]
            else:
                rows = conn.execute('SELECT * FROM clientes ORDER BY nombre LIMIT ? OFFSET ?',(limit,offset)).fetchall()
                total = conn.execute('SELECT COUNT(*) FROM clientes').fetchone()[0]
            conn.close()
            self.send_json({'data':[dict(r) for r in rows],'total':total})

        else:
            conn.close()
            self.send_json({'error':'not found'}, 404)

    def do_POST(self):
        path   = urlparse(self.path).path
        length = int(self.headers.get('Content-Length',0))
        body   = json.loads(self.rfile.read(length)) if length else {}

        if path == '/api/login':
            u = body.get('usuario','').strip()
            p = body.get('password','')
            usr = USERS.get(u)
            if usr and usr['hash'] == hashlib.sha256(p.encode()).hexdigest():
                tok = secrets.token_hex(16)
                SESSIONS[tok] = usr
                self.send_json({'ok':True,'token':tok,'nombre':usr['nombre'],'rol':usr['rol']})
            else:
                self.send_json({'ok':False,'error':'Credenciales incorrectas'})
            return

        usr = check_auth(self)
        if not usr:
            self.send_json({'error':'unauthorized'}, 401)
            return

        conn = get_db()

        if path == '/api/compras':
            conn.execute('INSERT INTO compras (fecha,proveedor,comprobante,precio_usd,moneda,detalle) VALUES (?,?,?,?,?,?)',
                (body.get('fecha',''), body.get('proveedor',''), body.get('comprobante',''),
                 float(body.get('precio_usd',0)), body.get('moneda','USD'), body.get('detalle','')))
            conn.commit()
            conn.close()
            self.send_json({'ok':True})

        elif path == '/api/ventas':
            conn.execute('INSERT INTO ventas (fecha,cliente,detalle,precio_usd,moneda,comprobante) VALUES (?,?,?,?,?,?)',
                (body.get('fecha',''), body.get('cliente',''), body.get('detalle',''),
                 float(body.get('precio_usd',0)), body.get('moneda','USD'), body.get('comprobante','')))
            conn.commit()
            conn.close()
            self.send_json({'ok':True})

        elif path == '/api/clientes':
            conn.execute('INSERT INTO clientes (nombre,tipo_doc,documento,telefono,email,pais) VALUES (?,?,?,?,?,?)',
                (body.get('nombre',''), body.get('tipo_doc','CI'), body.get('documento',''),
                 body.get('telefono',''), body.get('email',''), body.get('pais','Uruguay')))
            conn.commit()
            conn.close()
            self.send_json({'ok':True})

        elif path == '/api/import':
            for r in body.get('compras',[]):
                conn.execute('INSERT INTO compras (fecha,proveedor,comprobante,precio_usd,moneda,detalle) VALUES (?,?,?,?,?,?)',
                    (r.get('fecha',''), r.get('proveedor',''), r.get('comprobante',''),
                     float(r.get('precio_usd',0)), r.get('moneda','USD'), r.get('detalle','')))
            for r in body.get('ventas',[]):
                conn.execute('INSERT INTO ventas (fecha,cliente,detalle,precio_usd,moneda,comprobante) VALUES (?,?,?,?,?,?)',
                    (r.get('fecha',''), r.get('cliente',''), r.get('detalle',''),
                     float(r.get('precio_usd',0)), r.get('moneda','USD'), r.get('comprobante','')))
            for r in body.get('clientes',[]):
                conn.execute('INSERT INTO clientes (nombre,tipo_doc,documento,telefono,email,pais) VALUES (?,?,?,?,?,?)',
                    (r.get('nombre',''), r.get('tipo_doc','CI'), r.get('documento',''),
                     r.get('telefono',''), r.get('email',''), r.get('pais','Uruguay')))
            conn.commit()
            conn.close()
            self.send_json({'ok':True})

        else:
            conn.close()
            self.send_json({'error':'not found'}, 404)

    def do_DELETE(self):
        path = urlparse(self.path).path
        usr  = check_auth(self)
        if not usr:
            self.send_json({'error':'unauthorized'}, 401)
            return

        conn = get_db()
        parts = path.strip('/').split('/')
        if len(parts) == 3 and parts[1] in ('compras',1'ventas','clientes'):
            tabla = parts[1]
            rid   = int(parts[2])
            conn.execute(f'DELETE FROM {tabla} WHERE id=?', (rid,))
            conn.commit()
            conn.close()
            self.send_json({'ok':True})
        else:
            conn.close()
            self.send_json({'error':'not found'}, 404)

if __name__ == '__main__':
    init_db()
    auto_import()
    print(f'AutomotoraGV en puerto {PORT}')
    HTTPServer(('', PORT), Handler).serve_forever()
