#!/usr/bin/env python3
# deploy: v5
import json, re, csv, io, sqlite3, hashlib, os, secrets
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
    conn.commit()
    conn.close()

def auto_import():
    conn = get_db()
    c_count = conn.execute('SELECT COUNT(*) FROM compras').fetchone()[0]
    v_count = conn.execute('SELECT COUNT(*) FROM ventas').fetchone()[0]
    conn.close()

    # Importar compras
    if c_count == 0:
        try:
            with open('compras_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            conn = get_db()
            for r in data:
                conn.execute(
                    'INSERT INTO compras (fecha,proveedor,comprobante,precio_usd,moneda,detalle,marca,modelo,anio,motor,chasis,color) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
                    (r.get('fecha',''), r.get('proveedor',''), r.get('comprobante',''),
                     float(r.get('precio_usd',0)), r.get('moneda','USD'), r.get('detalle',''),
                     r.get('marca',''), r.get('modelo',''), r.get('anio',''),
                     r.get('motor',''), r.get('chasis',''), r.get('color',''))
                )
            conn.commit()
            conn.close()
            print('Auto-import: ' + str(len(data)) + ' compras')
        except Exception as e:
            print('Auto-import compras error: ' + str(e))

    # Importar ventas
    if v_count == 0:
        try:
            with open('ventas_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            conn = get_db()
            for r in data:
                conn.execute(
                    'INSERT INTO ventas (fecha,cliente,detalle,precio_usd,moneda,comprobante) VALUES (?,?,?,?,?,?)',
                    (r.get('fecha',''), r.get('cliente',''), r.get('detalle',''),
                     float(r.get('precio_usd',0)), r.get('moneda','USD'), r.get('comprobante',''))
                )
            conn.commit()
            conn.close()
            print('Auto-import: ' + str(len(data)) + ' ventas')
        except Exception as e:
            print('Auto-import ventas error: ' + str(e))

def check_auth(handler):
    tok = handler.headers.get('X-Auth-Token','').strip()
    if not tok:
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
        self.send_header('Access-Control-Allow-Methods','GET,POST,PUT,DELETE,OPTIONS')
        self.send_header('Access-Control-Allow-Headers','Content-Type,Authorization,X-Auth-Token')
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
            self.send_json({'comprados':c,'vendidos':v,'clientes':l})

        elif path == '/api/compras':
            limit  = int(qs.get('limit',['50'])[0])
            offset = int(qs.get('offset',['0'])[0])
            q      = qs.get('q',[''])[0]
            if q:
                rows = conn.execute("SELECT * FROM compras WHERE proveedor LIKE ? OR detalle LIKE ? OR comprobante LIKE ? ORDER BY fecha DESC LIMIT ? OFFSET ?",
                    ('%'+q+'%','%'+q+'%','%'+q+'%',limit,offset)).fetchall()
                total = conn.execute("SELECT COUNT(*) FROM compras WHERE proveedor LIKE ? OR detalle LIKE ? OR comprobante LIKE ?",
                    ('%'+q+'%','%'+q+'%','%'+q+'%')).fetchone()[0]
            else:
                rows = conn.execute('SELECT * FROM compras ORDER BY fecha DESC LIMIT ? OFFSET ?',(limit,offset)).fetchall()
                total = conn.execute('SELECT COUNT(*) FROM compras').fetchone()[0]
            conn.close()
            self.send_json({'data':[dict(r) for r in rows],'total':total})

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

        if path == '/api/ventas/fix':
            rows = conn.execute('SELECT id,comprobante,detalle FROM ventas').fetchall()
            updated=0
            for row in rows:
                det = row['detalle'] or ''
                mot=''; ch=''; mar=''; mod=''
                if det and not det.startswith('Doc:'):
                    m=re.search(r'MOTOR[:\s]+([A-Z0-9\-/]+)',det,re.IGNORECASE)
                    if m: mot=m.group(1).strip()
                    m=re.search(r'(?:CHASIS|CASIS|CH)[:\s]+([A-Z0-9]+)',det,re.IGNORECASE)
                    if m: ch=m.group(1).strip()
                    mod=re.split(r'\s+(?:MOTOR|CHASIS|CASIS|CH)[:\s]',det,flags=re.IGNORECASE)[0].strip().rstrip(',;: ')
                    u=mod.upper()
                    if u.startswith('BMW') or u.startswith('BME'): mar='BMW'
                    elif u.startswith('MINI'): mar='MINI'
                    elif u.startswith('VOLVO'): mar='VOLVO'
                    elif u.startswith('MAZDA'): mar='MAZDA'
                    elif 'LAND ROVER' in u or 'RANGE ROVER' in u: mar='LAND ROVER'
                    elif u.startswith('FERRARI'): mar='FERRARI'
                    elif u.startswith('JEEP'): mar='JEEP'
                    elif u.startswith('JAGUAR'): mar='JAGUAR'
                    elif u.startswith('AUDI'): mar='AUDI'
                    elif u.startswith('PORSCHE'): mar='PORSCHE'
                    elif 'RAPTOR' in u or u.startswith('FORD'): mar='FORD'
                    elif u.startswith('HONDA'): mar='HONDA'
                    elif u.startswith('SUBARU'): mar='SUBARU'
                    elif 'MERCEDES' in u: mar='MERCEDES BENZ'
                    elif 'TIGUAN' in u or u.startswith('VOLKSWAGEN'): mar='VOLKSWAGEN'
                    elif 'FRONTIER' in u: mar='NISSAN'
                    elif 'TOYOTA' in u: mar='TOYOTA'
                conn.execute('UPDATE ventas SET marca=?,modelo=?,motor=?,chasis=? WHERE id=?',(mar,mod,mot,ch,row['id']))
                updated+=1
            conn.commit(); conn.close()
            self.send_json({'ok':True,'updated':updated})
        elif path == '/api/import_csv':
            import csv as _csv, io as _io, re as _re
            ventas_csv = body.get('ventas_csv','')
            compras_csv = body.get('compras_csv','')
            ventas_nuevas = 0
            compras_nuevas = 0
            PROVS = ['BMW','MINI','MAZDA','LAND ROVER','VOLVO','JEEP','FERRARI','PORSCHE','AUDI','JAGUAR','MOTOR HAUS','GRESMOL']
            # Procesar ventas
            if ventas_csv:
                rows = list(_csv.reader(_io.StringIO(ventas_csv), delimiter=';'))
                for row in rows[1:]:
                    if len(row) < 8: continue
                    tipo = row[0].strip().strip('"')
                    if tipo not in ('e-Ticket','e-Factura'): continue
                    numero = row[1].strip().strip('"')
                    comprobante = tipo + ' ' + numero
                    fecha = row[2].strip().strip('"')
                    cliente_raw = row[4].strip().strip('"') if len(row) > 4 else ''
                    cm = _re.match(r'^(.+?)\s*\([^)]+\)$', cliente_raw)
                    cliente = cm.group(1).strip() if cm else cliente_raw
                    detalle = row[5].strip().strip('"') if len(row) > 5 else ''
                    try: precio = float(row[7].strip().strip('"').replace('.','').replace(',','.'))
                    except: precio = 0
                    moneda = row[8].strip().strip('"') if len(row) > 8 else 'USD'
                    exists = conn.execute('SELECT id FROM ventas WHERE comprobante=?',(comprobante,)).fetchone()
                    if not exists:
                        conn.execute('INSERT INTO ventas (fecha,cliente,detalle,precio_usd,moneda,comprobante) VALUES (?,?,?,?,?,?)',
                            (fecha,cliente,detalle,precio,moneda,comprobante))
                        ventas_nuevas += 1
            # Procesar compras
            if compras_csv:
                rows2 = list(_csv.reader(_io.StringIO(compras_csv), delimiter=';'))
                for row in rows2[1:]:
                    if len(row) < 8: continue
                    tipo = row[0].strip().strip('"')
                    if tipo not in ('e-Ticket','e-Factura','e-Remito'): continue
                    numero = row[1].strip().strip('"')
                    comprobante = tipo + ' ' + numero
                    fecha = row[2].strip().strip('"')
                    proveedor = row[4].strip().strip('"') if len(row) > 4 else ''
                    if not any(v in proveedor.upper() for v in PROVS): continue
                    detalle = row[5].strip().strip('"') if len(row) > 5 else ''
                    try: precio = float(row[7].strip().strip('"').replace('.','').replace(',','.'))
                    except: precio = 0
                    moneda = row[8].strip().strip('"') if len(row) > 8 else 'USD'
                    exists = conn.execute('SELECT id FROM compras WHERE comprobante=?',(comprobante,)).fetchone()
                    if not exists:
                        conn.execute('INSERT INTO compras (fecha,proveedor,comprobante,precio_usd,moneda,detalle,marca,modelo,anio,motor,chasis,color) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
                            (fecha,proveedor,comprobante,precio,moneda,detalle,'','','','','',''))
                        compras_nuevas += 1
            conn.commit()
            conn.close()
            self.send_json({'ok':True,'ventas_nuevas':ventas_nuevas,'compras_nuevas':compras_nuevas})
        elif path == '/api/compras':
            conn.execute('INSERT INTO compras (fecha,proveedor,comprobante,precio_usd,moneda,detalle,marca,modelo,anio,motor,chasis,color) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
                (body.get('fecha',''), body.get('proveedor',''), body.get('comprobante',''),
                 float(body.get('precio_usd',0)), body.get('moneda','USD'), body.get('detalle',''),
                 body.get('marca',''), body.get('modelo',''), body.get('anio',''),
                 body.get('motor',''), body.get('chasis',''), body.get('color','')))
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
            # Importar bulk: {compras:[...], ventas:[...], clientes:[...]}
            for r in body.get('compras',[]):
                conn.execute('INSERT INTO compras (fecha,proveedor,comprobante,precio_usd,moneda,detalle,marca,modelo,anio,motor,chasis,color) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
                    (r.get('fecha',''), r.get('proveedor',''), r.get('comprobante',''),
                     float(r.get('precio_usd',0)), r.get('moneda','USD'), r.get('detalle',''),
                     r.get('marca',''), r.get('modelo',''), r.get('anio',''),
                     r.get('motor',''), r.get('chasis',''), r.get('color','')))
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


        elif path == '/api/clear':
            tabla = body.get('tabla','')
            if tabla in ('compras','ventas','clientes'):
                conn.execute(f'DELETE FROM {tabla}')
                conn.commit()
            conn.close()
            self.send_json({'ok':True})

        elif path == '/api/reset':
            # Borrar todas las tablas y reimportar desde JSON
            conn.execute('DELETE FROM compras')
            conn.execute('DELETE FROM ventas')
            conn.execute('DELETE FROM clientes')
            conn.commit()
            conn.close()
            auto_import()
            self.send_json({'ok':True})

        else:
            conn.close()
            self.send_json({'error':'not found'}, 404)


    def do_PUT(self):
        path = urlparse(self.path).path
        usr = check_auth(self)
        if not usr: self.send_json({'error':'unauthorized'},401); return
        length = int(self.headers.get('Content-Length',0))
        body = json.loads(self.rfile.read(length)) if length else {}
        conn = get_db()
        parts = path.strip('/').split('/')
        if len(parts)==3 and parts[1]=='ventas':
            rid = int(parts[2])
            conn.execute('UPDATE ventas SET fecha=?,cliente=?,detalle=?,precio_usd=?,moneda=?,comprobante=?,marca=?,modelo=?,motor=?,chasis=? WHERE id=?',
                (body.get('fecha',''),body.get('cliente',''),body.get('detalle',''),float(body.get('precio_usd',0)),body.get('moneda','USD'),body.get('comprobante',''),body.get('marca',''),body.get('modelo',''),body.get('motor',''),body.get('chasis',''),rid))
            conn.commit(); conn.close(); self.send_json({'ok':True})
        elif len(parts)==3 and parts[1]=='compras':
            rid = int(parts[2])
            conn.execute('UPDATE compras SET fecha=?,proveedor=?,comprobante=?,precio_usd=?,moneda=?,detalle=?,marca=?,modelo=?,anio=?,motor=?,chasis=?,color=? WHERE id=?',
                (body.get('fecha',''),body.get('proveedor',''),body.get('comprobante',''),float(body.get('precio_usd',0)),body.get('moneda','USD'),body.get('detalle',''),body.get('marca',''),body.get('modelo',''),body.get('anio',''),body.get('motor',''),body.get('chasis',''),body.get('color',''),rid))
            conn.commit(); conn.close(); self.send_json({'ok':True})
        else:
            conn.close(); self.send_json({'error':'not found'},404)

    def do_DELETE(self):
        path = urlparse(self.path).path
        usr  = check_auth(self)
        if not usr:
            self.send_json({'error':'unauthorized'}, 401)
            return

        conn = get_db()
        parts = path.strip('/').split('/')
        # /api/compras/123
        if len(parts) == 3 and parts[1] in ('compras','ventas','clientes'):
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
