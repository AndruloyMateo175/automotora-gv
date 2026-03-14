#!/usr/bin/env python3
"""AutomotoraGV - Sistema de Gestion"""

import http.server
import sqlite3
import json
import hashlib
import hmac
import base64
import urllib.parse
import os
import time
import re

PORT = int(os.environ.get('PORT', 8765))
SECRET_KEY = os.environ.get('SECRET_KEY', 'automotora-gv-secret-2026')
DB_PATH = '/data/automotora.db' if os.path.exists('/data') else 'db/automotora.db'

print(f"AutomotoraGV iniciando en puerto {PORT}")

def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            nombre TEXT,
            rol TEXT DEFAULT 'vendedor'
        );
        CREATE TABLE IF NOT EXISTS vehiculos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            marca TEXT, modelo TEXT, anio INTEGER,
            motor TEXT, chasis TEXT, color TEXT,
            km INTEGER DEFAULT 0,
            precio_compra REAL DEFAULT 0,
            precio_venta REAL DEFAULT 0,
            proveedor TEXT,
            estado TEXT DEFAULT 'stock',
            fecha_compra TEXT, fecha_venta TEXT,
            cliente_id INTEGER, notas TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            documento TEXT, telefono TEXT,
            email TEXT, direccion TEXT, ciudad TEXT,
            notas TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehiculo_id INTEGER, cliente_id INTEGER,
            precio REAL, fecha TEXT, notas TEXT,
            FOREIGN KEY(vehiculo_id) REFERENCES vehiculos(id),
            FOREIGN KEY(cliente_id) REFERENCES clientes(id)
        );
    """)
    for user, pwd, nombre, rol in [
        ('aacosta', 'AutoGV2026!', 'A. Acosta', 'admin'),
        ('gvillasuso', 'AutoGV2026!', 'G. Villasuso', 'vendedor'),
        ('gyozzi', 'AutoGV2026!', 'G. Yozzi', 'vendedor'),
    ]:
        h = hashlib.sha256(pwd.encode()).hexdigest()
        c.execute('INSERT OR IGNORE INTO usuarios (username,password_hash,nombre,rol) VALUES (?,?,?,?)',
                  (user, h, nombre, rol))
    conn.commit()
    conn.close()

init_db()

def make_token(username):
    payload = f"{username}:{int(time.time())}"
    sig = hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return base64.b64encode(f"{payload}:{sig}".encode()).decode()

def verify_token(token):
    try:
        decoded = base64.b64decode(token.encode()).decode()
        parts = decoded.rsplit(':', 1)
        payload, sig = parts[0], parts[1]
        expected = hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
        if hmac.compare_digest(sig, expected):
            return payload.split(':')[0]
    except:
        pass
    return None

def get_user(handler):
    auth = handler.headers.get('Authorization', '')
    if auth.startswith('Bearer '):
        return verify_token(auth[7:])
    for part in handler.headers.get('Cookie', '').split(';'):
        part = part.strip()
        if part.startswith('token='):
            return verify_token(part[6:])
    return None

HTML = open('/app/index.html').read() if os.path.exists('/app/index.html') else open('index.html').read()

class RequestHandler(http.server.BaseHTTPRequestHandler):
    def send_json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)
        if path == '/':
            body = HTML.encode()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', len(body))
            self.end_headers()
            self.wfile.write(body)
            return
        user = get_user(self)
        if path == '/api/me':
            self.send_json({'username': user})
            return
        if not user:
            self.send_json({'error': 'No autorizado'}, 401)
            return
        if path == '/api/dashboard':
            conn = get_db(); c = conn.cursor()
            s = c.execute("SELECT COUNT(*) FROM vehiculos WHERE estado='stock'").fetchone()[0]
            v = c.execute("SELECT COUNT(*) FROM vehiculos WHERE estado='vendido'").fetchone()[0]
            cl = c.execute("SELECT COUNT(*) FROM clientes").fetchone()[0]
            t = c.execute("SELECT SUM(precio) FROM ventas").fetchone()[0] or 0
            conn.close()
            self.send_json({'stock': s, 'vendidos': v, 'clientes': cl, 'ventas_total': t})
            return
        if path == '/api/vehiculos':
            q = qs.get('q', [''])[0]; e = qs.get('estado', [''])[0]
            conn = get_db()
            sql = "SELECT * FROM vehiculos WHERE (marca LIKE ? OR modelo LIKE ? OR chasis LIKE ? OR motor LIKE ?)"
            p = ['%'+q+'%']*4
            if e: sql += " AND estado=?"; p.append(e)
            rows = [dict(r) for r in conn.execute(sql+' ORDER BY id DESC', p).fetchall()]
            conn.close(); self.send_json({'items': rows})
            return
        if path == '/api/clientes':
            q = qs.get('q', [''])[0]; conn = get_db()
            rows = [dict(r) for r in conn.execute(
                "SELECT * FROM clientes WHERE nombre LIKE ? OR documento LIKE ? OR telefono LIKE ? ORDER BY nombre",
                ['%'+q+'%']*3).fetchall()]
            conn.close(); self.send_json({'items': rows})
            return
        if path == '/api/ventas':
            conn = get_db()
            rows = [dict(r) for r in conn.execute("""
                SELECT v.id, v.fecha, v.precio, veh.marca, veh.modelo, c.nombre as cliente
                FROM ventas v
                LEFT JOIN vehiculos veh ON v.vehiculo_id=veh.id
                LEFT JOIN clientes c ON v.cliente_id=c.id
                ORDER BY v.fecha DESC""").fetchall()]
            conn.close(); self.send_json({'items': rows})
            return
        self.send_json({'error': 'Not found'}, 404)

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(length) or b'{}')
        path = self.path
        if path == '/api/login':
            conn = get_db()
            h = hashlib.sha256(body.get('password', '').encode()).hexdigest()
            row = conn.execute("SELECT * FROM usuarios WHERE username=? AND password_hash=?",
                               (body.get('username'), h)).fetchone()
            conn.close()
            if row:
                self.send_json({'ok': True, 'token': make_token(row['username'])})
            else:
                self.send_json({'error': 'Usuario o contrasena incorrectos'}, 401)
            return
        if path == '/api/logout':
            self.send_json({'ok': True})
            return
        user = get_user(self)
        if not user:
            self.send_json({'error': 'No autorizado'}, 401)
            return
        if path == '/api/vehiculos':
            conn = get_db()
            conn.execute("""INSERT INTO vehiculos
                (marca,modelo,anio,color,motor,chasis,km,proveedor,precio_compra,precio_venta,fecha_compra,notas,estado)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,'stock')""",
                (body.get('marca'), body.get('modelo'), body.get('anio'), body.get('color'),
                 body.get('motor'), body.get('chasis'), body.get('km'), body.get('proveedor'),
                 body.get('precio_compra'), body.get('precio_venta'), body.get('fecha_compra'), body.get('notas')))
            conn.commit(); conn.close(); self.send_json({'ok': True})
            return
        if path == '/api/clientes':
            conn = get_db()
            conn.execute("INSERT INTO clientes (nombre,documento,telefono,email,ciudad,direccion) VALUES (?,?,?,?,?,?)",
                (body.get('nombre'), body.get('documento'), body.get('telefono'),
                 body.get('email'), body.get('ciudad'), body.get('direccion')))
            conn.commit(); conn.close(); self.send_json({'ok': True})
            return
        if path == '/api/ventas':
            conn = get_db()
            conn.execute("INSERT INTO ventas (vehiculo_id,cliente_id,precio,fecha,notas) VALUES (?,?,?,?,?)",
                (body.get('vehiculo_id'), body.get('cliente_id'), body.get('precio'),
                 body.get('fecha'), body.get('notas')))
            conn.execute("UPDATE vehiculos SET estado='vendido', fecha_venta=?, cliente_id=? WHERE id=?",
                (body.get('fecha'), body.get('cliente_id'), body.get('vehiculo_id')))
            conn.commit(); conn.close(); self.send_json({'ok': True})
            return
        self.send_json({'error': 'Not found'}, 404)

    def do_PUT(self):
        length = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(length) or b'{}')
        path = self.path
        user = get_user(self)
        if not user:
            self.send_json({'error': 'No autorizado'}, 401)
            return
        m = re.match(r'/api/vehiculos/(\d+)', path)
        if m:
            conn = get_db()
            conn.execute("""UPDATE vehiculos SET marca=?,modelo=?,anio=?,color=?,motor=?,chasis=?,
                km=?,proveedor=?,precio_compra=?,precio_venta=?,fecha_compra=?,notas=? WHERE id=?""",
                (body.get('marca'), body.get('modelo'), body.get('anio'), body.get('color'),
                 body.get('motor'), body.get('chasis'), body.get('km'), body.get('proveedor'),
                 body.get('precio_compra'), body.get('precio_venta'), body.get('fecha_compra'),
                 body.get('notas'), m.group(1)))
            conn.commit(); conn.close(); self.send_json({'ok': True})
            return
        m = re.match(r'/api/clientes/(\d+)', path)
        if m:
            conn = get_db()
            conn.execute("UPDATE clientes SET nombre=?,documento=?,telefono=?,email=?,ciudad=?,direccion=? WHERE id=?",
                (body.get('nombre'), body.get('documento'), body.get('telefono'),
                 body.get('email'), body.get('ciudad'), body.get('direccion'), m.group(1)))
            conn.commit(); conn.close(); self.send_json({'ok': True})
            return
        self.send_json({'error': 'Not found'}, 404)

    def log_message(self, format, *args): pass

if __name__ == '__main__':
    server = http.server.HTTPServer(('0.0.0.0', PORT), RequestHandler)
    print(f"AutomotoraGV corriendo en puerto {PORT}")
    server.serve_forever()
