#!/usr/bin/env python3
# AutomotoraGV - Server v7 (rebuild integral)
import json, re, sqlite3, hashlib, os, secrets
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

PORT    = int(os.environ.get('PORT', 8765))
DB_PATH = '/data/automotora.db'

USERS = {
    'aacosta':    {'hash': hashlib.sha256(b'cincoestrellas').hexdigest(), 'nombre': 'A. Acosta'},
    'gvillasuso': {'hash': hashlib.sha256(b'cincoestrellas').hexdigest(), 'nombre': 'G. Villasuso'},
    'gyozzi':     {'hash': hashlib.sha256(b'cincoestrellas').hexdigest(), 'nombre': 'G. Yozzi'},
}
SESSIONS = {}

# ── DB ────────────────────────────────────────────────────────────────
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
        precio_usd REAL, moneda TEXT, detalle TEXT,
        marca TEXT, modelo TEXT, anio TEXT, motor TEXT, chasis TEXT, color TEXT
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS ventas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT, cliente TEXT, detalle TEXT,
        precio_usd REAL, moneda TEXT, comprobante TEXT,
        marca TEXT, modelo TEXT, motor TEXT, chasis TEXT
    )''')
    for _col in ['marca','modelo','motor','chasis']:
        try: conn.execute(f'ALTER TABLE ventas ADD COLUMN {_col} TEXT DEFAULT ""')
        except: pass
    conn.execute('''CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT, tipo_doc TEXT, documento TEXT,
        telefono TEXT, email TEXT, pais TEXT
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS inventario_stock (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        marca TEXT, modelo TEXT, chasis TEXT, motor TEXT,
        matricula TEXT, padron TEXT, precio REAL,
        tipo TEXT DEFAULT '0km',
        anio TEXT, color TEXT,
        compra_id INTEGER,
        fecha_ingreso TEXT,
        vendido INTEGER DEFAULT 0
    )''')
    conn.commit()
    conn.close()

def auto_import():
    """Import from JSON data files if DB is empty."""
    conn = get_db()
    if conn.execute('SELECT COUNT(*) FROM compras').fetchone()[0] == 0:
        for fn in ['compras_data.json','compras_data_v2.json']:
            if os.path.exists(fn):
                data = json.load(open(fn, encoding='utf-8'))
                for r in data:
                    conn.execute(
                        'INSERT INTO compras (fecha,proveedor,comprobante,precio_usd,moneda,detalle,marca,modelo,anio,motor,chasis,color) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
                        (r.get('fecha',''), r.get('proveedor',''), r.get('comprobante',''),
                         r.get('precio_usd',0), r.get('moneda','USD'), r.get('detalle',''),
                         r.get('marca',''), r.get('modelo',''), r.get('anio',''),
                         r.get('motor',''), r.get('chasis',''), r.get('color','')))
                break
    if conn.execute('SELECT COUNT(*) FROM ventas').fetchone()[0] == 0:
        for fn in ['ventas_data.json','ventas_data_v2.json']:
            if os.path.exists(fn):
                data = json.load(open(fn, encoding='utf-8'))
                for r in data:
                    conn.execute(
                        'INSERT INTO ventas (fecha,cliente,detalle,precio_usd,moneda,comprobante,marca,modelo,motor,chasis) VALUES (?,?,?,?,?,?,?,?,?,?)',
                        (r.get('fecha',''), r.get('cliente',''), r.get('detalle',''),
                         r.get('precio_usd',0), r.get('moneda','USD'), r.get('comprobante',''),
                         r.get('marca',''), r.get('modelo',''), r.get('motor',''), r.get('chasis','')))
                break
    conn.commit()
    conn.close()

# ── Auth ──────────────────────────────────────────────────────────────
def check_auth(handler):
    c = handler.headers.get('Cookie','')
    for part in c.split(';'):
        part = part.strip()
        if part.startswith('session='):
            sid = part.split('=',1)[1]
            return SESSIONS.get(sid)
    return None

HTML = open('index.html', 'rb').read() if os.path.exists('index.html') else b'<h1>AutomotoraGV</h1>'

# ── Handler ───────────────────────────────────────────────────────────
class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def send_json(self, data, code=200):
        body = json.dumps(data, ensure_ascii=False, default=str).encode()
        self.send_response(code)
        self.send_header('Content-Type','application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin','*')
        self.send_header('Access-Control-Allow-Methods','GET,POST,PUT,DELETE,OPTIONS')
        self.send_header('Access-Control-Allow-Headers','Content-Type')
        self.end_headers()

    # ── GET ────────────────────────────────────────────────────────
    def do_GET(self):
        path = urlparse(self.path).path
        qs   = parse_qs(urlparse(self.path).query)

        if path == '/' or path == '/index.html':
            self.send_response(200)
            self.send_header('Content-Type','text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(HTML)))
            self.end_headers()
            self.wfile.write(HTML)
            return

        # Serve static files (logo, etc.)
        if path == '/logo.png' and os.path.exists('logo.png'):
            data = open('logo.png', 'rb').read()
            self.send_response(200)
            self.send_header('Content-Type','image/png')
            self.send_header('Content-Length', str(len(data)))
            self.send_header('Cache-Control','public, max-age=86400')
            self.end_headers()
            self.wfile.write(data)
            return

        if path == '/api/me':
            usr = check_auth(self)
            if usr:
                self.send_json({'ok': True, 'user': usr})
            else:
                self.send_json({'ok': False}, 401)
            return

        # Protected API
        usr = check_auth(self)
        if not usr:
            self.send_json({'error':'unauthorized'}, 401)
            return

        conn = get_db()

        if path == '/api/compras':
            rows = conn.execute('SELECT * FROM compras ORDER BY id DESC').fetchall()
            self.send_json([dict(r) for r in rows])

        elif path == '/api/ventas':
            rows = conn.execute('SELECT * FROM ventas ORDER BY id DESC').fetchall()
            self.send_json([dict(r) for r in rows])

        elif path == '/api/clientes':
            rows = conn.execute('SELECT * FROM clientes ORDER BY nombre').fetchall()
            self.send_json([dict(r) for r in rows])

        elif path == '/api/stock':
            vendido = qs.get('vendido',['0'])[0]
            rows = conn.execute('SELECT * FROM inventario_stock WHERE vendido=? ORDER BY id DESC',
                                (int(vendido),)).fetchall()
            self.send_json([dict(r) for r in rows])

        elif path.startswith('/api/compras/'):
            rid = int(path.split('/')[-1])
            row = conn.execute('SELECT * FROM compras WHERE id=?', (rid,)).fetchone()
            self.send_json(dict(row) if row else {'error':'not found'})

        elif path.startswith('/api/ventas/'):
            rid = int(path.split('/')[-1])
            row = conn.execute('SELECT * FROM ventas WHERE id=?', (rid,)).fetchone()
            self.send_json(dict(row) if row else {'error':'not found'})

        elif path.startswith('/api/clientes/'):
            rid = int(path.split('/')[-1])
            row = conn.execute('SELECT * FROM clientes WHERE id=?', (rid,)).fetchone()
            self.send_json(dict(row) if row else {'error':'not found'})

        elif path.startswith('/api/stock/'):
            rid = int(path.split('/')[-1])
            row = conn.execute('SELECT * FROM inventario_stock WHERE id=?', (rid,)).fetchone()
            self.send_json(dict(row) if row else {'error':'not found'})

        else:
            self.send_json({'error':'not found'}, 404)

        conn.close()

    # ── POST ───────────────────────────────────────────────────────
    def do_POST(self):
        path = urlparse(self.path).path
        length = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(length)) if length else {}

        # Login
        if path == '/api/login':
            u = body.get('user','').lower().strip()
            p = body.get('pass','')
            h = hashlib.sha256(p.encode()).hexdigest()
            if u in USERS and USERS[u]['hash'] == h:
                sid = secrets.token_hex(16)
                SESSIONS[sid] = USERS[u]['nombre']
                self.send_response(200)
                self.send_header('Content-Type','application/json')
                self.send_header('Set-Cookie', f'session={sid}; Path=/; HttpOnly; SameSite=Lax')
                body_out = json.dumps({'ok': True, 'nombre': USERS[u]['nombre']}).encode()
                self.send_header('Content-Length', str(len(body_out)))
                self.end_headers()
                self.wfile.write(body_out)
            else:
                self.send_json({'ok': False, 'error': 'Credenciales incorrectas'}, 401)
            return

        if path == '/api/logout':
            c = self.headers.get('Cookie','')
            for part in c.split(';'):
                part = part.strip()
                if part.startswith('session='):
                    sid = part.split('=',1)[1]
                    SESSIONS.pop(sid, None)
            self.send_response(200)
            self.send_header('Content-Type','application/json')
            self.send_header('Set-Cookie','session=; Path=/; Max-Age=0')
            body_out = json.dumps({'ok': True}).encode()
            self.send_header('Content-Length', str(len(body_out)))
            self.end_headers()
            self.wfile.write(body_out)
            return

        # Protected
        usr = check_auth(self)
        if not usr:
            self.send_json({'error':'unauthorized'}, 401)
            return

        conn = get_db()

        if path == '/api/compras':
            cur = conn.execute(
                '''INSERT INTO compras (fecha,proveedor,comprobante,precio_usd,moneda,detalle,marca,modelo,anio,motor,chasis,color)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',
                (body.get('fecha',''), body.get('proveedor',''), body.get('comprobante',''),
                 body.get('precio_usd',0), body.get('moneda','USD'), body.get('detalle',''),
                 body.get('marca',''), body.get('modelo',''), body.get('anio',''),
                 body.get('motor',''), body.get('chasis',''), body.get('color','')))
            conn.commit()
            new_id = cur.lastrowid
            conn.close()
            self.send_json({'ok': True, 'id': new_id})

        elif path == '/api/ventas':
            cur = conn.execute(
                '''INSERT INTO ventas (fecha,cliente,detalle,precio_usd,moneda,comprobante,marca,modelo,motor,chasis)
                   VALUES (?,?,?,?,?,?,?,?,?,?)''',
                (body.get('fecha',''), body.get('cliente',''), body.get('detalle',''),
                 body.get('precio_usd',0), body.get('moneda','USD'), body.get('comprobante',''),
                 body.get('marca',''), body.get('modelo',''), body.get('motor',''), body.get('chasis','')))
            conn.commit()
            new_id = cur.lastrowid
            conn.close()
            self.send_json({'ok': True, 'id': new_id})

        elif path == '/api/clientes':
            cur = conn.execute(
                '''INSERT INTO clientes (nombre,tipo_doc,documento,telefono,email,pais)
                   VALUES (?,?,?,?,?,?)''',
                (body.get('nombre',''), body.get('tipo_doc',''), body.get('documento',''),
                 body.get('telefono',''), body.get('email',''), body.get('pais','Uruguay')))
            conn.commit()
            new_id = cur.lastrowid
            conn.close()
            self.send_json({'ok': True, 'id': new_id})

        elif path == '/api/stock':
            cur = conn.execute(
                '''INSERT INTO inventario_stock (marca,modelo,chasis,motor,matricula,padron,precio,tipo,anio,color,compra_id,fecha_ingreso)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,date('now'))''',
                (body.get('marca',''), body.get('modelo',''), body.get('chasis',''),
                 body.get('motor',''), body.get('matricula',''), body.get('padron',''),
                 body.get('precio',0), body.get('tipo','Usado'),
                 body.get('anio',''), body.get('color',''), body.get('compra_id')))
            conn.commit()
            new_id = cur.lastrowid
            conn.close()
            self.send_json({'ok': True, 'id': new_id})

        elif path.startswith('/api/stock/from-compra/'):
            # Add 0km vehicle to stock from a purchase
            compra_id = int(path.split('/')[-1])
            row = conn.execute('SELECT * FROM compras WHERE id=?', (compra_id,)).fetchone()
            if not row:
                conn.close()
                self.send_json({'error': 'Compra no encontrada'}, 404)
                return
            # Check if already in stock
            existing = conn.execute('SELECT id FROM inventario_stock WHERE compra_id=?', (compra_id,)).fetchone()
            if existing:
                conn.close()
                self.send_json({'error': 'Este vehiculo ya esta en stock', 'stock_id': existing['id']}, 409)
                return
            r = dict(row)
            cur = conn.execute(
                '''INSERT INTO inventario_stock (marca,modelo,chasis,motor,matricula,padron,precio,tipo,anio,color,compra_id,fecha_ingreso)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,date('now'))''',
                (r.get('marca',''), r.get('modelo',''), r.get('chasis',''),
                 r.get('motor',''), '', '', r.get('precio_usd',0), '0km',
                 r.get('anio',''), r.get('color',''), compra_id))
            conn.commit()
            new_id = cur.lastrowid
            conn.close()
            self.send_json({'ok': True, 'id': new_id})

        elif path == '/api/ventas/fix':
            # Bulk fix: parse vehicle details from detalle field
            rows = conn.execute('SELECT id, detalle FROM ventas WHERE (marca IS NULL OR marca="") AND detalle!=""').fetchall()
            n = 0
            for row in rows:
                det = row['detalle']
                marca = re.search(r'MARCA:(\w+)', det)
                modelo = re.search(r'MODELO:(.+?)(?:AÑO:|MOTOR:|CHASIS:|COLOR:|$)', det)
                motor = re.search(r'MOTOR:(\S+)', det)
                chasis = re.search(r'CHASIS:(\S+)', det)
                if marca or modelo or motor or chasis:
                    conn.execute('UPDATE ventas SET marca=?, modelo=?, motor=?, chasis=? WHERE id=?',
                        (marca.group(1) if marca else '',
                         modelo.group(1).strip() if modelo else '',
                         motor.group(1) if motor else '',
                         chasis.group(1) if chasis else '',
                         row['id']))
                    n += 1
            conn.commit()
            conn.close()
            self.send_json({'ok': True, 'fixed': n})

        else:
            conn.close()
            self.send_json({'error':'not found'}, 404)

    # ── PUT ────────────────────────────────────────────────────────
    def do_PUT(self):
        path = urlparse(self.path).path
        usr  = check_auth(self)
        if not usr:
            self.send_json({'error':'unauthorized'}, 401)
            return

        length = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(length)) if length else {}
        conn = get_db()
        parts = path.strip('/').split('/')

        if len(parts) == 3 and parts[0] == 'api':
            tabla = parts[1]
            rid   = int(parts[2])

            if tabla == 'compras':
                conn.execute(
                    '''UPDATE compras SET fecha=?,proveedor=?,comprobante=?,precio_usd=?,moneda=?,detalle=?,
                       marca=?,modelo=?,anio=?,motor=?,chasis=?,color=? WHERE id=?''',
                    (body.get('fecha',''), body.get('proveedor',''), body.get('comprobante',''),
                     body.get('precio_usd',0), body.get('moneda','USD'), body.get('detalle',''),
                     body.get('marca',''), body.get('modelo',''), body.get('anio',''),
                     body.get('motor',''), body.get('chasis',''), body.get('color',''), rid))

            elif tabla == 'ventas':
                conn.execute(
                    '''UPDATE ventas SET fecha=?,cliente=?,detalle=?,precio_usd=?,moneda=?,comprobante=?,
                       marca=?,modelo=?,motor=?,chasis=? WHERE id=?''',
                    (body.get('fecha',''), body.get('cliente',''), body.get('detalle',''),
                     body.get('precio_usd',0), body.get('moneda','USD'), body.get('comprobante',''),
                     body.get('marca',''), body.get('modelo',''), body.get('motor',''),
                     body.get('chasis',''), rid))

            elif tabla == 'clientes':
                conn.execute(
                    '''UPDATE clientes SET nombre=?,tipo_doc=?,documento=?,telefono=?,email=?,pais=? WHERE id=?''',
                    (body.get('nombre',''), body.get('tipo_doc',''), body.get('documento',''),
                     body.get('telefono',''), body.get('email',''), body.get('pais',''), rid))

            elif tabla == 'stock':
                conn.execute(
                    '''UPDATE inventario_stock SET marca=?,modelo=?,chasis=?,motor=?,matricula=?,padron=?,
                       precio=?,tipo=?,anio=?,color=?,vendido=? WHERE id=?''',
                    (body.get('marca',''), body.get('modelo',''), body.get('chasis',''),
                     body.get('motor',''), body.get('matricula',''), body.get('padron',''),
                     body.get('precio',0), body.get('tipo',''), body.get('anio',''),
                     body.get('color',''), body.get('vendido',0), rid))

            else:
                conn.close()
                self.send_json({'error':'not found'}, 404)
                return

            conn.commit()
            conn.close()
            self.send_json({'ok': True})
        else:
            conn.close()
            self.send_json({'error':'not found'}, 404)

    # ── DELETE ─────────────────────────────────────────────────────
    def do_DELETE(self):
        path = urlparse(self.path).path
        usr  = check_auth(self)
        if not usr:
            self.send_json({'error':'unauthorized'}, 401)
            return

        conn = get_db()
        parts = path.strip('/').split('/')
        if len(parts) == 3 and parts[1] in ('compras','ventas','clientes','stock'):
            tabla = 'inventario_stock' if parts[1] == 'stock' else parts[1]
            rid   = int(parts[2])
            conn.execute(f'DELETE FROM {tabla} WHERE id=?', (rid,))
            conn.commit()
            conn.close()
            self.send_json({'ok': True})
        else:
            conn.close()
            self.send_json({'error':'not found'}, 404)

# ── Main ──────────────────────────────────────────────────────────────
if __name__ == '__main__':
    init_db()
    auto_import()
    print(f'AutomotoraGV en puerto {PORT}')
    HTTPServer(('', PORT), Handler).serve_forever()
