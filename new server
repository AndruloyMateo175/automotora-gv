#!/usr/bin/env python3
"""AutomotoraGV - Sistema de Gestion de Vehiculos"""
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
    c = conn.cursor()
    c.execute(
        'CREATE TABLE IF NOT EXISTS ventas ('
        'id INTEGER PRIMARY KEY AUTOINCREMENT,'
        'fecha TEXT, cliente TEXT, marca TEXT, modelo TEXT,'
        'chasis TEXT, motor TEXT, precio_usd REAL, precio_uyu REAL,'
        'documento TEXT, tipo_doc TEXT, pais TEXT, detalle TEXT)'
    )
    c.execute(
        'CREATE TABLE IF NOT EXISTS compras ('
        'id INTEGER PRIMARY KEY AUTOINCREMENT,'
        'fecha TEXT, proveedor TEXT, comprobante TEXT,'
        'marca TEXT, modelo TEXT, chasis TEXT, motor TEXT,'
        'precio_usd REAL, precio_uyu REAL, moneda TEXT, detalle TEXT)'
    )
    c.execute(
        'CREATE TABLE IF NOT EXISTS clientes ('
        'id INTEGER PRIMARY KEY AUTOINCREMENT,'
        'nombre TEXT UNIQUE, documento TEXT, tipo_doc TEXT,'
        'pais TEXT, email TEXT, telefono TEXT, rut TEXT)'
    )
    conn.commit()
    conn.close()

def check_session(token):
    return SESSIONS.get(token)

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def send_json(self, data, code=200):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

    def send_html(self, html, code=200):
        body = html.encode() if isinstance(html, str) else html
        self.send_response(code)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def _get_token(self):
        auth = self.headers.get('Authorization', '')
        return auth.replace('Bearer ', '').strip()

    def do_GET(self):
        parsed = urlparse(self.path)
        path   = parsed.path
        qs     = parse_qs(parsed.query)

        if path == '/import-tool':
            try:
                with open('import_tool.html', 'rb') as f:
                    self.send_html(f.read())
            except Exception as e:
                self.send_json({'error': str(e)}, 404)
            return

        if path == '/' or path == '/index.html':
            try:
                with open('index.html', 'rb') as f:
                    self.send_html(f.read())
            except Exception:
                self.send_html('<h1>AutomotoraGV</h1>')
            return

        if path == '/api/stats':
            tok = self._get_token()
            if not check_session(tok):
                self.send_json({'error': 'unauthorized'}, 401)
                return
            conn = get_db()
            c = conn.cursor()
            c.execute('SELECT COUNT(*) FROM ventas')
            vendidos = c.fetchone()[0]
            c.execute('SELECT COUNT(*) FROM compras')
            comprados = c.fetchone()[0]
            c.execute('SELECT COUNT(*) FROM clientes')
            clientes_n = c.fetchone()[0]
            conn.close()
            self.send_json({'vendidos': vendidos, 'comprados': comprados, 'clientes': clientes_n})
            return

        if path == '/api/ventas':
            tok = self._get_token()
            if not check_session(tok):
                self.send_json({'error': 'unauthorized'}, 401)
                return
            page   = int(qs.get('page',  ['1'])[0])
            limit  = int(qs.get('limit', ['50'])[0])
            q      = qs.get('q', [''])[0]
            offset = (page - 1) * limit
            conn = get_db()
            c = conn.cursor()
            if q:
                like = '%' + q + '%'
                c.execute('SELECT COUNT(*) FROM ventas WHERE cliente LIKE ? OR detalle LIKE ? OR chasis LIKE ? OR motor LIKE ?', (like, like, like, like))
                total = c.fetchone()[0]
                c.execute('SELECT * FROM ventas WHERE cliente LIKE ? OR detalle LIKE ? OR chasis LIKE ? OR motor LIKE ? ORDER BY fecha DESC, id DESC LIMIT ? OFFSET ?', (like, like, like, like, limit, offset))
            else:
                c.execute('SELECT COUNT(*) FROM ventas')
                total = c.fetchone()[0]
                c.execute('SELECT * FROM ventas ORDER BY fecha DESC, id DESC LIMIT ? OFFSET ?', (limit, offset))
            rows = [dict(r) for r in c.fetchall()]
            conn.close()
            self.send_json({'data': rows, 'total': total})
            return

        if path == '/api/compras':
            tok = self._get_token()
            if not check_session(tok):
                self.send_json({'error': 'unauthorized'}, 401)
                return
            page   = int(qs.get('page',  ['1'])[0])
            limit  = int(qs.get('limit', ['50'])[0])
            q      = qs.get('q', [''])[0]
            offset = (page - 1) * limit
            conn = get_db()
            c = conn.cursor()
            if q:
                like = '%' + q + '%'
                c.execute('SELECT COUNT(*) FROM compras WHERE proveedor LIKE ? OR detalle LIKE ? OR chasis LIKE ? OR motor LIKE ?', (like, like, like, like))
                total = c.fetchone()[0]
                c.execute('SELECT * FROM compras WHERE proveedor LIKE ? OR detalle LIKE ? OR chasis LIKE ? OR motor LIKE ? ORDER BY fecha DESC, id DESC LIMIT ? OFFSET ?', (like, like, like, like, limit, offset))
            else:
                c.execute('SELECT COUNT(*) FROM compras')
                total = c.fetchone()[0]
                c.execute('SELECT * FROM compras ORDER BY fecha DESC, id DESC LIMIT ? OFFSET ?', (limit, offset))
            rows = [dict(r) for r in c.fetchall()]
            conn.close()
            self.send_json({'data': rows, 'total': total})
            return

        if path == '/api/clientes':
            tok = self._get_token()
            if not check_session(tok):
                self.send_json({'error': 'unauthorized'}, 401)
                return
            page   = int(qs.get('page',  ['1'])[0])
            limit  = int(qs.get('limit', ['50'])[0])
            q      = qs.get('q', [''])[0]
            offset = (page - 1) * limit
            conn = get_db()
            c = conn.cursor()
            if q:
                like = '%' + q + '%'
                c.execute('SELECT COUNT(*) FROM clientes WHERE nombre LIKE ? OR documento LIKE ? OR rut LIKE ?', (like, like, like))
                total = c.fetchone()[0]
                c.execute('SELECT * FROM clientes WHERE nombre LIKE ? OR documento LIKE ? OR rut LIKE ? ORDER BY nombre LIMIT ? OFFSET ?', (like, like, like, limit, offset))
            else:
                c.execute('SELECT COUNT(*) FROM clientes')
                total = c.fetchone()[0]
                c.execute('SELECT * FROM clientes ORDER BY nombre LIMIT ? OFFSET ?', (limit, offset))
            rows = [dict(r) for r in c.fetchall()]
            conn.close()
            self.send_json({'data': rows, 'total': total})
            return

        self.send_json({'error': 'not found'}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path   = parsed.path
        length = int(self.headers.get('Content-Length', 0))
        body   = json.loads(self.rfile.read(length) or b'{}')

        if path == '/api/login':
            u    = body.get('usuario', '')
            p    = body.get('password', '')
            user = USERS.get(u)
            if user and user['hash'] == hashlib.sha256(p.encode()).hexdigest():
                tok = secrets.token_hex(16)
                SESSIONS[tok] = {'usuario': u, 'nombre': user['nombre'], 'rol': user['rol']}
                self.send_json({'ok': True, 'token': tok, 'nombre': user['nombre'], 'rol': user['rol']})
            else:
                self.send_json({'ok': False, 'error': 'credenciales invalidas'}, 401)
            return

        tok = self._get_token()
        if not check_session(tok):
            self.send_json({'error': 'unauthorized'}, 401)
            return

        if path == '/api/import':
            tipo      = body.get('tipo', '')
            registros = body.get('registros', [])
            conn = get_db()
            c    = conn.cursor()
            if tipo == 'ventas':
                for r in registros:
                    c.execute(
                        'INSERT INTO ventas '
                        '(fecha,cliente,marca,modelo,chasis,motor,precio_usd,precio_uyu,documento,tipo_doc,pais,detalle) '
                        'VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
                        (r.get('fecha',''), r.get('cliente',''),
                         r.get('marca',''), r.get('modelo',''),
                         r.get('chasis',''), r.get('motor',''),
                         r.get('precio_usd', 0), r.get('precio_uyu', 0),
                         r.get('comprobante',''), r.get('tipo_doc','e-Factura'),
                         r.get('pais','UY'), r.get('detalle',''))
                    )
            elif tipo == 'compras':
                for r in registros:
                    c.execute(
                        'INSERT INTO compras '
                        '(fecha,proveedor,comprobante,marca,modelo,chasis,motor,precio_usd,precio_uyu,moneda,detalle) '
                        'VALUES (?,?,?,?,?,?,?,?,?,?,?)',
                        (r.get('fecha',''), r.get('proveedor',''),
                         r.get('comprobante',''),
                         r.get('marca',''), r.get('modelo',''),
                         r.get('chasis',''), r.get('motor',''),
                         r.get('precio_usd', 0), r.get('precio_uyu', 0),
                         r.get('moneda','USD'), r.get('detalle',''))
                    )
            elif tipo == 'clientes':
                for r in registros:
                    try:
                        c.execute(
                            'INSERT OR IGNORE INTO clientes '
                            '(nombre,documento,tipo_doc,pais,email,telefono,rut) '
                            'VALUES (?,?,?,?,?,?,?)',
                            (r.get('nombre',''), r.get('documento',''),
                             r.get('tipo_doc','CI'), r.get('pais','UY'),
                             r.get('email',''), r.get('telefono',''),
                             r.get('rut',''))
                        )
                    except Exception:
                        pass
            conn.commit()
            conn.close()
            self.send_json({'ok': True, 'insertados': len(registros)})
            return

        if path == '/api/clear':
            tipo = body.get('tipo', 'all')
            conn = get_db()
            c    = conn.cursor()
            if tipo in ('ventas', 'all'):
                c.execute('DELETE FROM ventas')
            if tipo in ('compras', 'all'):
                c.execute('DELETE FROM compras')
            if tipo in ('clientes', 'all'):
                c.execute('DELETE FROM clientes')
            conn.commit()
            conn.close()
            self.send_json({'ok': True})
            return

        self.send_json({'error': 'not found'}, 404)


if __name__ == '__main__':
    init_db()
    server = HTTPServer(('0.0.0.0', PORT), Handler)
    print(f'AutomotoraGV corriendo en puerto {PORT}')
    server.serve_forever()
