#!/usr/bin/env python3
"""
AutomotoraGV - Sistema de gestión vehicular
Servidor para Railway con volumen persistente en /data
"""

import http.server
import sqlite3
import json
import hashlib
import hmac
import base64
import datetime
import urllib.parse
import os
import sys
import time
import re
import secrets
import mimetypes

# ── CONFIGURACIÓN ────────────────────────────────────────
PORT = int(os.environ.get('PORT', 8080))
DB_PATH = '/data/automotora.db'
SECRET_KEY = os.environ.get('SECRET_KEY', 'automotora_gv_2026_secret_key')
TOKEN_EXPIRY_HOURS = 72

# ── JWT SIMPLE ───────────────────────────────────────────
def b64url_encode(data):
    if isinstance(data, str):
        data = data.encode()
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode()

def b64url_decode(s):
    s += '=' * (4 - len(s) % 4)
    return base64.urlsafe_b64decode(s)

def create_jwt(payload):
    header = b64url_encode(json.dumps({'alg': 'HS256', 'typ': 'JWT'}))
    payload['exp'] = (datetime.datetime.utcnow() + datetime.timedelta(hours=TOKEN_EXPIRY_HOURS)).isoformat()
    body = b64url_encode(json.dumps(payload))
    sig_input = f'{header}.{body}'.encode()
    sig = hmac.new(SECRET_KEY.encode(), sig_input, hashlib.sha256).digest()
    return f'{header}.{body}.{b64url_encode(sig)}'

def verify_jwt(token):
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        sig_input = f'{parts[0]}.{parts[1]}'.encode()
        expected = hmac.new(SECRET_KEY.encode(), sig_input, hashlib.sha256).digest()
        actual = b64url_decode(parts[2])
        if not hmac.compare_digest(expected, actual):
            return None
        payload = json.loads(b64url_decode(parts[1]))
        if datetime.datetime.fromisoformat(payload['exp']) < datetime.datetime.utcnow():
            return None
        return payload
    except Exception:
        return None

# ── PASSWORD HASHING ─────────────────────────────────────
def hash_password(pw):
    salt = secrets.token_hex(16)
    h = hashlib.sha256((salt + pw).encode()).hexdigest()
    return f'{salt}:{h}'

def check_password(pw, stored):
    if ':' not in stored:
        # Legacy: plain sha256 (from v7 migration)
        return hashlib.sha256(pw.encode()).hexdigest() == stored
    salt, h = stored.split(':', 1)
    return hashlib.sha256((salt + pw).encode()).hexdigest() == h

# ── BASE DE DATOS ────────────────────────────────────────
def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    # Usuarios
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        nombre TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        rol TEXT DEFAULT 'admin',
        activo INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    # Compras
    c.execute('''CREATE TABLE IF NOT EXISTS compras (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT,
        proveedor TEXT,
        comprobante TEXT,
        marca TEXT,
        modelo TEXT,
        anio TEXT,
        motor TEXT,
        chasis TEXT,
        color TEXT,
        precio_usd REAL DEFAULT 0,
        moneda TEXT DEFAULT 'USD',
        detalle TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    # Ventas
    c.execute('''CREATE TABLE IF NOT EXISTS ventas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT,
        cliente TEXT,
        comprobante TEXT,
        marca TEXT,
        modelo TEXT,
        chasis TEXT,
        motor TEXT,
        precio_usd REAL DEFAULT 0,
        moneda TEXT DEFAULT 'USD',
        detalle TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    # Clientes
    c.execute('''CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        tipo_doc TEXT DEFAULT 'RUT',
        documento TEXT,
        telefono TEXT,
        email TEXT,
        pais TEXT DEFAULT 'Uruguay',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    # Stock
    c.execute('''CREATE TABLE IF NOT EXISTS stock (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT DEFAULT 'Usado',
        marca TEXT,
        modelo TEXT,
        anio TEXT,
        chasis TEXT,
        motor TEXT,
        color TEXT,
        matricula TEXT,
        padron TEXT,
        precio REAL DEFAULT 0,
        precio_venta REAL DEFAULT 0,
        vendido INTEGER DEFAULT 0,
        fecha_ingreso TEXT,
        estado TEXT DEFAULT 'Stock',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    conn.commit()

    # Migración: agregar fecha_ingreso si no existe
    try:
        c.execute("ALTER TABLE stock ADD COLUMN fecha_ingreso TEXT")
        conn.commit()
    except:
        pass  # Ya existe

    # Migración: agregar estado si no existe
    try:
        c.execute("ALTER TABLE stock ADD COLUMN estado TEXT DEFAULT 'Stock'")
        c.execute("UPDATE stock SET estado = 'Stock' WHERE estado IS NULL")
        conn.commit()
    except:
        pass

    # Rellenar fecha_ingreso para registros existentes que no la tienen
    # 0km: buscar la fecha de la compra por chasis
    c.execute("""UPDATE stock SET fecha_ingreso = (
        SELECT compras.fecha FROM compras WHERE compras.chasis = stock.chasis AND compras.chasis != '' LIMIT 1
    ) WHERE fecha_ingreso IS NULL AND tipo = '0km' AND chasis IS NOT NULL AND chasis != ''""")
    # Usados y cualquier restante: usar created_at o fecha de hoy
    c.execute("""UPDATE stock SET fecha_ingreso = COALESCE(
        substr(created_at, 1, 10), date('now')
    ) WHERE fecha_ingreso IS NULL""")
    conn.commit()

    # Crear usuarios por defecto si no existen
    usuarios_default = [
        ('aacosta',    'A. Acosta',    'cincoestrellas', 'admin'),
        ('gvillasuso', 'G. Villasuso', 'cincoestrellas', 'admin'),
        ('gyozzi',     'G. Yozzi',     'cincoestrellas', 'vendedor'),
    ]
    for username, nombre, pw, rol in usuarios_default:
        try:
            c.execute("INSERT INTO usuarios (username,nombre,password_hash,rol) VALUES (?,?,?,?)",
                     (username, nombre, hash_password(pw), rol))
        except sqlite3.IntegrityError:
            pass

    conn.commit()
    conn.close()
    print(f"✓ Base de datos inicializada: {DB_PATH}")

# ── HELPERS ──────────────────────────────────────────────
def read_body(handler):
    length = int(handler.headers.get('Content-Length', 0))
    if length == 0:
        return {}
    raw = handler.rfile.read(length)
    try:
        return json.loads(raw)
    except Exception:
        return {}

def json_response(handler, data, status=200):
    body = json.dumps(data, ensure_ascii=False, default=str).encode('utf-8')
    handler.send_response(status)
    handler.send_header('Content-Type', 'application/json')
    handler.send_header('Content-Length', str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)

def get_user_from_token(handler):
    auth = handler.headers.get('Authorization', '')
    if not auth.startswith('Bearer '):
        return None
    token = auth[7:]
    payload = verify_jwt(token)
    if not payload:
        return None
    return payload

# ── HTTP HANDLER ─────────────────────────────────────────
class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Silenciar logs

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type,Authorization')

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    # ── GET ──
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)

        # Serve static files
        if path == '/' or path == '/index.html':
            self._serve_file('index.html', 'text/html')
            return
        if path == '/logo.png':
            self._serve_file('logo.png', 'image/png')
            return
        if path.startswith('/static/'):
            fname = path[8:]
            mime = mimetypes.guess_type(fname)[0] or 'application/octet-stream'
            self._serve_file(fname, mime)
            return

        # API endpoints requiring auth
        user = get_user_from_token(self)

        if path == '/api/me':
            if not user:
                json_response(self, {'error': 'unauthorized'}, 401)
                return
            # Fetch fresh user data from DB
            conn = get_db()
            row = conn.execute("SELECT * FROM usuarios WHERE id=? AND activo=1", (user['id'],)).fetchone()
            conn.close()
            if not row:
                json_response(self, {'error': 'unauthorized'}, 401)
                return
            json_response(self, {
                'ok': True,
                'id': row['id'],
                'username': row['username'],
                'nombre': row['nombre'],
                'user': row['username'],
                'rol': row['rol']
            })
            return

        if path == '/api/stats':
            if not user:
                json_response(self, {'error': 'unauthorized'}, 401)
                return
            conn = get_db()
            compras = conn.execute("SELECT COUNT(*) FROM compras").fetchone()[0]
            ventas = conn.execute("SELECT COUNT(*) FROM ventas").fetchone()[0]
            clientes = conn.execute("SELECT COUNT(*) FROM clientes").fetchone()[0]
            stock = conn.execute("SELECT COUNT(*) FROM stock WHERE vendido=0").fetchone()[0]
            conn.close()
            json_response(self, {'compras': compras, 'ventas': ventas, 'clientes': clientes, 'stock': stock})
            return

        if not user:
            json_response(self, {'error': 'unauthorized'}, 401)
            return

        # COMPRAS
        if path == '/api/compras':
            self._get_compras(qs)
            return
        m = re.match(r'^/api/compras/(\d+)$', path)
        if m:
            self._get_one('compras', int(m.group(1)))
            return

        # VENTAS
        if path == '/api/ventas':
            self._get_ventas(qs)
            return
        m = re.match(r'^/api/ventas/(\d+)$', path)
        if m:
            self._get_one('ventas', int(m.group(1)))
            return

        # CLIENTES
        if path == '/api/clientes':
            self._get_clientes(qs)
            return
        m = re.match(r'^/api/clientes/(\d+)$', path)
        if m:
            self._get_one('clientes', int(m.group(1)))
            return

        # STOCK
        if path == '/api/stock':
            self._get_stock(qs)
            return
        m = re.match(r'^/api/stock/(\d+)$', path)
        if m:
            self._get_one('stock', int(m.group(1)))
            return

        self.send_error(404)

    # ── POST ──
    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == '/api/login':
            self._login()
            return

        user = get_user_from_token(self)
        if not user:
            json_response(self, {'error': 'unauthorized'}, 401)
            return

        if path == '/api/change-password':
            self._change_password(user)
            return

        if path == '/api/compras':
            self._post_compra()
            return
        if path == '/api/ventas':
            self._post_venta()
            return
        if path == '/api/clientes':
            self._post_cliente()
            return
        if path == '/api/stock':
            self._post_stock()
            return

        m = re.match(r'^/api/stock/from-compra/(\d+)$', path)
        if m:
            self._stock_from_compra(int(m.group(1)))
            return

        self.send_error(404)

    # ── PUT ──
    def do_PUT(self):
        user = get_user_from_token(self)
        if not user:
            json_response(self, {'error': 'unauthorized'}, 401)
            return

        path = urllib.parse.urlparse(self.path).path

        m = re.match(r'^/api/compras/(\d+)$', path)
        if m:
            self._put_compra(int(m.group(1)))
            return
        m = re.match(r'^/api/ventas/(\d+)$', path)
        if m:
            self._put_venta(int(m.group(1)))
            return
        m = re.match(r'^/api/clientes/(\d+)$', path)
        if m:
            self._put_cliente(int(m.group(1)))
            return
        m = re.match(r'^/api/stock/(\d+)$', path)
        if m:
            self._put_stock(int(m.group(1)))
            return

        self.send_error(404)

    # ── DELETE ──
    def do_DELETE(self):
        user = get_user_from_token(self)
        if not user:
            json_response(self, {'error': 'unauthorized'}, 401)
            return

        path = urllib.parse.urlparse(self.path).path

        for table in ['compras', 'ventas', 'clientes', 'stock']:
            m = re.match(rf'^/api/{table}/(\d+)$', path)
            if m:
                conn = get_db()
                conn.execute(f"DELETE FROM {table} WHERE id=?", (int(m.group(1)),))
                conn.commit()
                conn.close()
                json_response(self, {'ok': True})
                return

        self.send_error(404)

    # ── SERVE FILES ──
    def _serve_file(self, filename, content_type):
        base = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(base, filename)
        if not os.path.exists(filepath):
            self.send_error(404)
            return
        with open(filepath, 'rb') as f:
            data = f.read()
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(data)))
        self._cors()
        self.end_headers()
        self.wfile.write(data)

    # ── LOGIN ──
    def _login(self):
        body = read_body(self)
        username = (body.get('username') or body.get('user') or '').lower().strip()
        password = body.get('password') or body.get('pass') or ''

        conn = get_db()
        row = conn.execute("SELECT * FROM usuarios WHERE username=? AND activo=1", (username,)).fetchone()
        conn.close()

        if not row or not check_password(password, row['password_hash']):
            json_response(self, {'error': 'Credenciales incorrectas'}, 401)
            return

        token = create_jwt({
            'id': row['id'],
            'username': row['username'],
            'nombre': row['nombre'],
            'rol': row['rol']
        })
        json_response(self, {'token': token, 'nombre': row['nombre'], 'ok': True})

    # ── CHANGE PASSWORD ──
    def _change_password(self, user):
        body = read_body(self)
        current = body.get('current_password', '')
        new_pw = body.get('new_password', '')

        if not current or not new_pw:
            json_response(self, {'error': 'Faltan campos'}, 400)
            return

        if len(new_pw) < 4:
            json_response(self, {'error': 'Mínimo 4 caracteres'}, 400)
            return

        conn = get_db()
        row = conn.execute("SELECT * FROM usuarios WHERE id=?", (user['id'],)).fetchone()
        if not row or not check_password(current, row['password_hash']):
            conn.close()
            json_response(self, {'error': 'Contraseña actual incorrecta'}, 401)
            return

        conn.execute("UPDATE usuarios SET password_hash=? WHERE id=?",
                     (hash_password(new_pw), user['id']))
        conn.commit()
        conn.close()
        json_response(self, {'ok': True})

    # ── GET HELPERS ──
    def _get_one(self, table, rid):
        conn = get_db()
        row = conn.execute(f"SELECT * FROM {table} WHERE id=?", (rid,)).fetchone()
        conn.close()
        if row:
            json_response(self, dict(row))
        else:
            json_response(self, {'error': 'No encontrado'}, 404)

    def _get_compras(self, qs):
        conn = get_db()
        limit = int(qs.get('limit', ['500'])[0])
        rows = [dict(r) for r in conn.execute(
            "SELECT * FROM compras ORDER BY fecha DESC, id DESC LIMIT ?", (limit,)).fetchall()]
        conn.close()
        json_response(self, rows)

    def _get_ventas(self, qs):
        conn = get_db()
        limit = int(qs.get('limit', ['500'])[0])
        rows = [dict(r) for r in conn.execute(
            "SELECT * FROM ventas ORDER BY fecha DESC, id DESC LIMIT ?", (limit,)).fetchall()]
        conn.close()
        json_response(self, rows)

    def _get_clientes(self, qs):
        conn = get_db()
        limit = int(qs.get('limit', ['500'])[0])
        rows = [dict(r) for r in conn.execute(
            "SELECT * FROM clientes ORDER BY nombre ASC LIMIT ?", (limit,)).fetchall()]
        conn.close()
        json_response(self, rows)

    def _get_stock(self, qs):
        vendido = int(qs.get('vendido', ['0'])[0])
        conn = get_db()
        rows = [dict(r) for r in conn.execute(
            "SELECT * FROM stock WHERE vendido=? ORDER BY id DESC", (vendido,)).fetchall()]
        conn.close()
        json_response(self, rows)

    # ── POST HELPERS ──
    def _post_compra(self):
        v = read_body(self)
        conn = get_db()
        c = conn.cursor()
        c.execute("""INSERT INTO compras (fecha,proveedor,comprobante,marca,modelo,anio,motor,chasis,color,precio_usd,moneda,detalle)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (v.get('fecha'), v.get('proveedor'), v.get('comprobante'),
             v.get('marca'), v.get('modelo'), v.get('anio'),
             v.get('motor'), v.get('chasis'), v.get('color'),
             v.get('precio_usd', 0), v.get('moneda', 'USD'), v.get('detalle')))
        conn.commit()
        row = dict(conn.execute("SELECT * FROM compras WHERE id=?", (c.lastrowid,)).fetchone())
        conn.close()
        json_response(self, row, 201)

    def _post_venta(self):
        v = read_body(self)
        conn = get_db()
        c = conn.cursor()
        c.execute("""INSERT INTO ventas (fecha,cliente,comprobante,marca,modelo,chasis,motor,precio_usd,moneda,detalle)
            VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (v.get('fecha'), v.get('cliente'), v.get('comprobante'),
             v.get('marca'), v.get('modelo'), v.get('chasis'),
             v.get('motor'), v.get('precio_usd', 0), v.get('moneda', 'USD'), v.get('detalle')))
        conn.commit()
        row = dict(conn.execute("SELECT * FROM ventas WHERE id=?", (c.lastrowid,)).fetchone())
        conn.close()
        json_response(self, row, 201)

    def _post_cliente(self):
        v = read_body(self)
        conn = get_db()
        c = conn.cursor()
        c.execute("""INSERT INTO clientes (nombre,tipo_doc,documento,telefono,email,pais)
            VALUES (?,?,?,?,?,?)""",
            (v.get('nombre'), v.get('tipo_doc', 'RUT'), v.get('documento'),
             v.get('telefono'), v.get('email'), v.get('pais', 'Uruguay')))
        conn.commit()
        row = dict(conn.execute("SELECT * FROM clientes WHERE id=?", (c.lastrowid,)).fetchone())
        conn.close()
        json_response(self, row, 201)

    def _post_stock(self):
        v = read_body(self)
        conn = get_db()
        c = conn.cursor()
        fecha_ing = v.get('fecha_ingreso') or datetime.date.today().isoformat()
        c.execute("""INSERT INTO stock (tipo,marca,modelo,anio,chasis,motor,color,matricula,padron,precio,precio_venta,vendido,fecha_ingreso,estado)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (v.get('tipo', 'Usado'), v.get('marca'), v.get('modelo'), v.get('anio'),
             v.get('chasis'), v.get('motor'), v.get('color'),
             v.get('matricula'), v.get('padron'),
             v.get('precio', 0), v.get('precio_venta', 0), v.get('vendido', 0), fecha_ing,
             v.get('estado', 'Stock')))
        conn.commit()
        row = dict(conn.execute("SELECT * FROM stock WHERE id=?", (c.lastrowid,)).fetchone())
        conn.close()
        json_response(self, row, 201)

    def _stock_from_compra(self, compra_id):
        conn = get_db()
        compra = conn.execute("SELECT * FROM compras WHERE id=?", (compra_id,)).fetchone()
        if not compra:
            conn.close()
            json_response(self, {'error': 'Compra no encontrada'}, 404)
            return
        # Check if already in stock by chasis
        if compra['chasis']:
            existing = conn.execute("SELECT id FROM stock WHERE chasis=?", (compra['chasis'],)).fetchone()
            if existing:
                conn.close()
                json_response(self, {'error': 'Este vehículo ya está en stock'}, 400)
                return
        c = conn.cursor()
        c.execute("""INSERT INTO stock (tipo,marca,modelo,anio,chasis,motor,color,precio,vendido,fecha_ingreso)
            VALUES (?,?,?,?,?,?,?,?,0,?)""",
            ('0km', compra['marca'], compra['modelo'], compra['anio'],
             compra['chasis'], compra['motor'], compra['color'], compra['precio_usd'],
             compra['fecha']))
        conn.commit()
        conn.close()
        json_response(self, {'ok': True, 'id': c.lastrowid}, 201)

    # ── PUT HELPERS ──
    def _put_compra(self, cid):
        v = read_body(self)
        conn = get_db()
        conn.execute("""UPDATE compras SET fecha=?,proveedor=?,comprobante=?,marca=?,modelo=?,anio=?,
            motor=?,chasis=?,color=?,precio_usd=?,moneda=?,detalle=? WHERE id=?""",
            (v.get('fecha'), v.get('proveedor'), v.get('comprobante'),
             v.get('marca'), v.get('modelo'), v.get('anio'),
             v.get('motor'), v.get('chasis'), v.get('color'),
             v.get('precio_usd', 0), v.get('moneda', 'USD'), v.get('detalle'), cid))
        conn.commit()
        row = dict(conn.execute("SELECT * FROM compras WHERE id=?", (cid,)).fetchone())
        conn.close()
        json_response(self, row)

    def _put_venta(self, vid):
        v = read_body(self)
        conn = get_db()
        conn.execute("""UPDATE ventas SET fecha=?,cliente=?,comprobante=?,marca=?,modelo=?,
            chasis=?,motor=?,precio_usd=?,moneda=?,detalle=? WHERE id=?""",
            (v.get('fecha'), v.get('cliente'), v.get('comprobante'),
             v.get('marca'), v.get('modelo'), v.get('chasis'),
             v.get('motor'), v.get('precio_usd', 0), v.get('moneda', 'USD'), v.get('detalle'), vid))
        conn.commit()
        row = dict(conn.execute("SELECT * FROM ventas WHERE id=?", (vid,)).fetchone())
        conn.close()
        json_response(self, row)

    def _put_cliente(self, cid):
        v = read_body(self)
        conn = get_db()
        conn.execute("""UPDATE clientes SET nombre=?,tipo_doc=?,documento=?,telefono=?,email=?,pais=? WHERE id=?""",
            (v.get('nombre'), v.get('tipo_doc', 'RUT'), v.get('documento'),
             v.get('telefono'), v.get('email'), v.get('pais', 'Uruguay'), cid))
        conn.commit()
        row = dict(conn.execute("SELECT * FROM clientes WHERE id=?", (cid,)).fetchone())
        conn.close()
        json_response(self, row)

    def _put_stock(self, sid):
        v = read_body(self)
        conn = get_db()
        conn.execute("""UPDATE stock SET tipo=?,marca=?,modelo=?,anio=?,chasis=?,motor=?,color=?,
            matricula=?,padron=?,precio=?,precio_venta=?,vendido=?,estado=? WHERE id=?""",
            (v.get('tipo', 'Usado'), v.get('marca'), v.get('modelo'), v.get('anio'),
             v.get('chasis'), v.get('motor'), v.get('color'),
             v.get('matricula'), v.get('padron'),
             v.get('precio', 0), v.get('precio_venta', 0), v.get('vendido', 0),
             v.get('estado', 'Stock'), sid))
        conn.commit()
        row = dict(conn.execute("SELECT * FROM stock WHERE id=?", (sid,)).fetchone())
        conn.close()
        json_response(self, row)


# ── MAIN ─────────────────────────────────────────────────
if __name__ == '__main__':
    init_db()
    server = http.server.HTTPServer(('0.0.0.0', PORT), Handler)
    print(f"AutomotoraGV en puerto {PORT}")
    server.serve_forever()
