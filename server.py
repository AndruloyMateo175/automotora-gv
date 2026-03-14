#!/usr/bin/env python3
"""
AutomotoraGV - Sistema de Gestion
"""

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

def get_user_from_request(handler):
    # Check Authorization header (Bearer token from localStorage)
    auth = handler.headers.get('Authorization', '')
    if auth.startswith('Bearer '):
        return verify_token(auth[7:])
    # Fallback: cookie
    cookie = handler.headers.get('Cookie', '')
    for part in cookie.split(';'):
        part = part.strip()
        if part.startswith('token='):
            return verify_token(part[6:])
    return None

HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AutomotoraGV</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',sans-serif;background:#0f172a;color:#e2e8f0;min-height:100vh}
.navbar{background:#1e293b;padding:12px 24px;display:flex;align-items:center;gap:16px;border-bottom:1px solid #334155;position:sticky;top:0;z-index:100}
.navbar h1{font-size:1.2rem;color:#38bdf8;font-weight:700}
.nav-links{display:flex;gap:8px;margin-left:auto}
.nav-links a{color:#94a3b8;text-decoration:none;padding:6px 12px;border-radius:6px;font-size:.9rem;transition:.2s}
.nav-links a:hover,.nav-links a.active{background:#334155;color:#e2e8f0}
.main{padding:24px;max-width:1400px;margin:0 auto}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;margin-bottom:24px}
.card{background:#1e293b;border:1px solid #334155;border-radius:12px;padding:20px;text-align:center}
.card .num{font-size:2rem;font-weight:700;color:#38bdf8}
.card .label{color:#94a3b8;font-size:.9rem;margin-top:4px}
table{width:100%;border-collapse:collapse;background:#1e293b;border-radius:12px;overflow:hidden}
th{background:#334155;padding:12px 16px;text-align:left;font-size:.85rem;color:#94a3b8;font-weight:600}
td{padding:10px 16px;border-bottom:1px solid #0f172a;font-size:.9rem}
tr:hover td{background:#334155}
.badge{display:inline-block;padding:2px 8px;border-radius:20px;font-size:.75rem;font-weight:600}
.badge-green{background:#064e3b;color:#34d399}
.badge-blue{background:#1e3a5f;color:#60a5fa}
.btn{padding:8px 16px;border:none;border-radius:8px;cursor:pointer;font-size:.9rem;font-weight:600;transition:.2s}
.btn-primary{background:#0ea5e9;color:#fff}
.btn-primary:hover{background:#0284c7}
.btn-sm{padding:4px 10px;font-size:.8rem}
.search-bar{display:flex;gap:8px;margin-bottom:16px;flex-wrap:wrap}
.search-bar input,.search-bar select{background:#1e293b;border:1px solid #334155;color:#e2e8f0;padding:8px 12px;border-radius:8px;font-size:.9rem;flex:1}
.modal{display:none;position:fixed;inset:0;background:rgba(0,0,0,.7);z-index:200;align-items:center;justify-content:center}
.modal.open{display:flex}
.modal-box{background:#1e293b;border:1px solid #334155;border-radius:16px;padding:24px;width:90%;max-width:520px;max-height:90vh;overflow-y:auto}
.modal-box h3{margin-bottom:16px;color:#38bdf8}
.form-group{margin-bottom:12px}
.form-group label{display:block;font-size:.85rem;color:#94a3b8;margin-bottom:4px}
.form-group input,.form-group select,.form-group textarea{width:100%;background:#0f172a;border:1px solid #334155;color:#e2e8f0;padding:8px 12px;border-radius:8px;font-size:.9rem}
.form-row{display:grid;grid-template-columns:1fr 1fr;gap:12px}
#login-screen{display:flex;align-items:center;justify-content:center;min-height:100vh}
.login-box{background:#1e293b;border:1px solid #334155;border-radius:16px;padding:40px;width:340px}
.login-box h2{text-align:center;color:#38bdf8;margin-bottom:24px}
.section{display:none}
.section.active{display:block}
.page-title{font-size:1.4rem;font-weight:700;margin-bottom:20px;color:#f1f5f9}
</style>
</head>
<body>
<div id="login-screen">
  <div class="login-box">
    <h2>AutomotoraGV</h2>
    <div class="form-group">
      <label>Usuario</label>
      <input type="text" id="login-user" placeholder="usuario">
    </div>
    <div class="form-group">
      <label>Contrasena</label>
      <input type="password" id="login-pass" onkeydown="if(event.key==='Enter')doLogin()">
    </div>
    <button class="btn btn-primary" style="width:100%;margin-top:8px" onclick="doLogin()">Ingresar</button>
    <p id="login-err" style="color:#f87171;text-align:center;margin-top:8px;font-size:.85rem"></p>
  </div>
</div>

<div id="app" style="display:none">
  <nav class="navbar">
    <h1>AutomotoraGV</h1>
    <div class="nav-links">
      <a href="#" onclick="showSection('dashboard')" id="nav-dashboard">Dashboard</a>
      <a href="#" onclick="showSection('vehiculos')" id="nav-vehiculos">Vehiculos</a>
      <a href="#" onclick="showSection('clientes')" id="nav-clientes">Clientes</a>
      <a href="#" onclick="showSection('ventas')" id="nav-ventas">Ventas</a>
      <a href="#" onclick="doLogout()" style="color:#f87171">Salir</a>
    </div>
  </nav>
  <div class="main">
    <div id="sec-dashboard" class="section">
      <p class="page-title">Dashboard</p>
      <div class="cards" id="dash-cards"></div>
    </div>
    <div id="sec-vehiculos" class="section">
      <p class="page-title">Vehiculos</p>
      <div class="search-bar">
        <input id="v-search" placeholder="Buscar marca, modelo, chasis..." oninput="loadVehiculos()">
        <select id="v-estado" onchange="loadVehiculos()">
          <option value="">Todos</option>
          <option value="stock">En stock</option>
          <option value="vendido">Vendidos</option>
        </select>
        <button class="btn btn-primary" onclick="openVehiculoModal()">+ Agregar</button>
      </div>
      <table>
        <thead><tr><th>Marca</th><th>Modelo</th><th>Anio</th><th>Chasis</th><th>Motor</th><th>KM</th><th>Precio</th><th>Estado</th><th>Proveedor</th><th></th></tr></thead>
        <tbody id="vehiculos-tbody"></tbody>
      </table>
    </div>
    <div id="sec-clientes" class="section">
      <p class="page-title">Clientes</p>
      <div class="search-bar">
        <input id="c-search" placeholder="Buscar cliente..." oninput="loadClientes()">
        <button class="btn btn-primary" onclick="openClienteModal()">+ Agregar</button>
      </div>
      <table>
        <thead><tr><th>Nombre</th><th>Documento</th><th>Telefono</th><th>Email</th><th>Ciudad</th><th></th></tr></thead>
        <tbody id="clientes-tbody"></tbody>
      </table>
    </div>
    <div id="sec-ventas" class="section">
      <p class="page-title">Ventas</p>
      <div class="search-bar">
        <button class="btn btn-primary" onclick="openVentaModal()">+ Nueva venta</button>
      </div>
      <table>
        <thead><tr><th>Fecha</th><th>Vehiculo</th><th>Cliente</th><th>Precio</th></tr></thead>
        <tbody id="ventas-tbody"></tbody>
      </table>
    </div>
  </div>
</div>

<!-- Modal vehiculo -->
<div class="modal" id="modal-vehiculo">
  <div class="modal-box">
    <h3 id="mv-title">Agregar Vehiculo</h3>
    <div class="form-row">
      <div class="form-group"><label>Marca</label><input id="mv-marca"></div>
      <div class="form-group"><label>Modelo</label><input id="mv-modelo"></div>
    </div>
    <div class="form-row">
      <div class="form-group"><label>Anio</label><input id="mv-anio" type="number"></div>
      <div class="form-group"><label>Color</label><input id="mv-color"></div>
    </div>
    <div class="form-row">
      <div class="form-group"><label>N Motor</label><input id="mv-motor"></div>
      <div class="form-group"><label>N Chasis</label><input id="mv-chasis"></div>
    </div>
    <div class="form-row">
      <div class="form-group"><label>KM</label><input id="mv-km" type="number"></div>
      <div class="form-group"><label>Proveedor</label><input id="mv-proveedor"></div>
    </div>
    <div class="form-row">
      <div class="form-group"><label>Precio Compra</label><input id="mv-pcompra" type="number"></div>
      <div class="form-group"><label>Precio Venta</label><input id="mv-pventa" type="number"></div>
    </div>
    <div class="form-group"><label>Fecha Compra</label><input id="mv-fcompra" type="date"></div>
    <div class="form-group"><label>Notas</label><textarea id="mv-notas" rows="2"></textarea></div>
    <div style="display:flex;gap:8px;justify-content:flex-end;margin-top:16px">
      <button class="btn" onclick="closeModal('modal-vehiculo')" style="background:#334155">Cancelar</button>
      <button class="btn btn-primary" onclick="saveVehiculo()">Guardar</button>
    </div>
  </div>
</div>

<!-- Modal cliente -->
<div class="modal" id="modal-cliente">
  <div class="modal-box">
    <h3>Cliente</h3>
    <div class="form-group"><label>Nombre completo</label><input id="mc-nombre"></div>
    <div class="form-row">
      <div class="form-group"><label>Documento</label><input id="mc-doc"></div>
      <div class="form-group"><label>Telefono</label><input id="mc-tel"></div>
    </div>
    <div class="form-row">
      <div class="form-group"><label>Email</label><input id="mc-email"></div>
      <div class="form-group"><label>Ciudad</label><input id="mc-ciudad"></div>
    </div>
    <div class="form-group"><label>Direccion</label><input id="mc-dir"></div>
    <div style="display:flex;gap:8px;justify-content:flex-end;margin-top:16px">
      <button class="btn" onclick="closeModal('modal-cliente')" style="background:#334155">Cancelar</button>
      <button class="btn btn-primary" onclick="saveCliente()">Guardar</button>
    </div>
  </div>
</div>

<!-- Modal venta -->
<div class="modal" id="modal-venta">
  <div class="modal-box">
    <h3>Nueva Venta</h3>
    <div class="form-group"><label>Vehiculo (en stock)</label><select id="mv2-vehiculo"></select></div>
    <div class="form-group"><label>Cliente</label><select id="mv2-cliente"></select></div>
    <div class="form-row">
      <div class="form-group"><label>Precio</label><input id="mv2-precio" type="number"></div>
      <div class="form-group"><label>Fecha</label><input id="mv2-fecha" type="date"></div>
    </div>
    <div class="form-group"><label>Notas</label><textarea id="mv2-notas" rows="2"></textarea></div>
    <div style="display:flex;gap:8px;justify-content:flex-end;margin-top:16px">
      <button class="btn" onclick="closeModal('modal-venta')" style="background:#334155">Cancelar</button>
      <button class="btn btn-primary" onclick="saveVenta()">Registrar</button>
    </div>
  </div>
</div>

<script>
let editingVehiculoId = null;
let editingClienteId = null;

// Token stored in sessionStorage to work with HTTPS proxy
function getToken() { return sessionStorage.getItem('gv_token'); }
function setToken(t) { sessionStorage.setItem('gv_token', t); }
function clearToken() { sessionStorage.removeItem('gv_token'); }

async function api(path, method='GET', body=null) {
  const opts = {method, headers:{'Content-Type':'application/json'}};
  const token = getToken();
  if (token) opts.headers['Authorization'] = 'Bearer ' + token;
  if (body) opts.body = JSON.stringify(body);
  const r = await fetch(path, opts);
  return r.json();
}

async function doLogin() {
  const username = document.getElementById('login-user').value;
  const password = document.getElementById('login-pass').value;
  const res = await api('/api/login', 'POST', {username, password});
  if (res.ok && res.token) {
    setToken(res.token);
    document.getElementById('login-screen').style.display = 'none';
    document.getElementById('app').style.display = 'block';
    showSection('dashboard');
  } else {
    document.getElementById('login-err').textContent = res.error || 'Error al ingresar';
  }
}

function doLogout() {
  clearToken();
  location.reload();
}

function showSection(name) {
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.getElementById('sec-' + name).classList.add('active');
  document.querySelectorAll('.nav-links a').forEach(a => a.classList.remove('active'));
  document.getElementById('nav-' + name)?.classList.add('active');
  if (name === 'dashboard') loadDashboard();
  if (name === 'vehiculos') loadVehiculos();
  if (name === 'clientes') loadClientes();
  if (name === 'ventas') loadVentas();
}

async function loadDashboard() {
  const d = await api('/api/dashboard');
  document.getElementById('dash-cards').innerHTML = [
    ['Vehiculos en Stock', d.stock],
    ['Vehiculos Vendidos', d.vendidos],
    ['Clientes', d.clientes],
    ['Total Ventas $', (d.ventas_total||0).toLocaleString()],
  ].map(([l,v]) => '<div class="card"><div class="num">' + v + '</div><div class="label">' + l + '</div></div>').join('');
}

async function loadVehiculos() {
  const q = document.getElementById('v-search').value;
  const estado = document.getElementById('v-estado').value;
  const data = await api('/api/vehiculos?q=' + encodeURIComponent(q) + '&estado=' + estado);
  document.getElementById('vehiculos-tbody').innerHTML = (data.items||[]).map(v =>
    '<tr><td>' + (v.marca||'') + '</td><td>' + (v.modelo||'') + '</td><td>' + (v.anio||'') + '</td><td>' + (v.chasis||'-') + '</td><td>' + (v.motor||'-') + '</td><td>' + (v.km||0).toLocaleString() + '</td><td>$' + (v.precio_venta||0).toLocaleString() + '</td>' +
    '<td><span class="badge ' + (v.estado==='stock'?'badge-green':'badge-blue') + '">' + v.estado + '</span></td>' +
    '<td>' + (v.proveedor||'-') + '</td>' +
    '<td><button class="btn btn-primary btn-sm" onclick=\'editVehiculo(' + JSON.stringify(v) + ')\'>Editar</button></td></tr>'
  ).join('') || '<tr><td colspan="10" style="text-align:center;color:#64748b;padding:24px">Sin registros</td></tr>';
}

async function loadClientes() {
  const q = document.getElementById('c-search').value;
  const data = await api('/api/clientes?q=' + encodeURIComponent(q));
  document.getElementById('clientes-tbody').innerHTML = (data.items||[]).map(c =>
    '<tr><td>' + c.nombre + '</td><td><span class="badge badge-blue">' + (c.documento||'-') + '</span></td>' +
    '<td>' + (c.telefono ? '<a href="tel:' + c.telefono + '" style="color:#34d399">' + c.telefono + '</a>' : '-') + '</td>' +
    '<td>' + (c.email||'-') + '</td><td>' + (c.ciudad||'-') + '</td>' +
    '<td><button class="btn btn-primary btn-sm" onclick=\'editCliente(' + JSON.stringify(c) + ')\'>Editar</button></td></tr>'
  ).join('') || '<tr><td colspan="6" style="text-align:center;color:#64748b;padding:24px">Sin registros</td></tr>';
}

async function loadVentas() {
  const data = await api('/api/ventas');
  document.getElementById('ventas-tbody').innerHTML = (data.items||[]).map(v =>
    '<tr><td>' + (v.fecha||'') + '</td><td>' + (v.marca||'') + ' ' + (v.modelo||'') + '</td><td>' + (v.cliente||'') + '</td><td>$' + (v.precio||0).toLocaleString() + '</td></tr>'
  ).join('') || '<tr><td colspan="4" style="text-align:center;color:#64748b;padding:24px">Sin ventas</td></tr>';
}

function openVehiculoModal() {
  editingVehiculoId = null;
  document.getElementById('mv-title').textContent = 'Agregar Vehiculo';
  ['marca','modelo','anio','color','motor','chasis','km','proveedor','pcompra','pventa','fcompra','notas'].forEach(f => {
    const el = document.getElementById('mv-' + f); if (el) el.value = '';
  });
  document.getElementById('modal-vehiculo').classList.add('open');
}

function editVehiculo(v) {
  editingVehiculoId = v.id;
  document.getElementById('mv-title').textContent = 'Editar Vehiculo';
  document.getElementById('mv-marca').value = v.marca||'';
  document.getElementById('mv-modelo').value = v.modelo||'';
  document.getElementById('mv-anio').value = v.anio||'';
  document.getElementById('mv-color').value = v.color||'';
  document.getElementById('mv-motor').value = v.motor||'';
  document.getElementById('mv-chasis').value = v.chasis||'';
  document.getElementById('mv-km').value = v.km||0;
  document.getElementById('mv-proveedor').value = v.proveedor||'';
  document.getElementById('mv-pcompra').value = v.precio_compra||0;
  document.getElementById('mv-pventa').value = v.precio_venta||0;
  document.getElementById('mv-fcompra').value = v.fecha_compra||'';
  document.getElementById('mv-notas').value = v.notas||'';
  document.getElementById('modal-vehiculo').classList.add('open');
}

async function saveVehiculo() {
  const body = {
    marca: document.getElementById('mv-marca').value,
    modelo: document.getElementById('mv-modelo').value,
    anio: document.getElementById('mv-anio').value,
    color: document.getElementById('mv-color').value,
    motor: document.getElementById('mv-motor').value,
    chasis: document.getElementById('mv-chasis').value,
    km: document.getElementById('mv-km').value,
    proveedor: document.getElementById('mv-proveedor').value,
    precio_compra: document.getElementById('mv-pcompra').value,
    precio_venta: document.getElementById('mv-pventa').value,
    fecha_compra: document.getElementById('mv-fcompra').value,
    notas: document.getElementById('mv-notas').value,
  };
  if (editingVehiculoId) {
    await api('/api/vehiculos/' + editingVehiculoId, 'PUT', body);
  } else {
    await api('/api/vehiculos', 'POST', body);
  }
  closeModal('modal-vehiculo');
  loadVehiculos();
}

function openClienteModal() {
  editingClienteId = null;
  ['nombre','doc','tel','email','ciudad','dir'].forEach(f => document.getElementById('mc-'+f).value='');
  document.getElementById('modal-cliente').classList.add('open');
}

function editCliente(c) {
  editingClienteId = c.id;
  document.getElementById('mc-nombre').value = c.nombre||'';
  document.getElementById('mc-doc').value = c.documento||'';
  document.getElementById('mc-tel').value = c.telefono||'';
  document.getElementById('mc-email').value = c.email||'';
  document.getElementById('mc-ciudad').value = c.ciudad||'';
  document.getElementById('mc-dir').value = c.direccion||'';
  document.getElementById('modal-cliente').classList.add('open');
}

async function saveCliente() {
  const body = {
    nombre: document.getElementById('mc-nombre').value,
    documento: document.getElementById('mc-doc').value,
    telefono: document.getElementById('mc-tel').value,
    email: document.getElementById('mc-email').value,
    ciudad: document.getElementById('mc-ciudad').value,
    direccion: document.getElementById('mc-dir').value,
  };
  if (editingClienteId) {
    await api('/api/clientes/' + editingClienteId, 'PUT', body);
  } else {
    await api('/api/clientes', 'POST', body);
  }
  closeModal('modal-cliente');
  loadClientes();
}

async function openVentaModal() {
  const [vs, cs] = await Promise.all([api('/api/vehiculos?estado=stock&q='), api('/api/clientes?q=')]);
  document.getElementById('mv2-vehiculo').innerHTML = (vs.items||[]).map(v =>
    '<option value="' + v.id + '">' + v.marca + ' ' + v.modelo + ' (' + v.anio + ')</option>'
  ).join('');
  document.getElementById('mv2-cliente').innerHTML = (cs.items||[]).map(c =>
    '<option value="' + c.id + '">' + c.nombre + '</option>'
  ).join('');
  document.getElementById('mv2-precio').value = '';
  document.getElementById('mv2-fecha').value = new Date().toISOString().split('T')[0];
  document.getElementById('mv2-notas').value = '';
  document.getElementById('modal-venta').classList.add('open');
}

async function saveVenta() {
  await api('/api/ventas', 'POST', {
    vehiculo_id: document.getElementById('mv2-vehiculo').value,
    cliente_id: document.getElementById('mv2-cliente').value,
    precio: document.getElementById('mv2-precio').value,
    fecha: document.getElementById('mv2-fecha').value,
    notas: document.getElementById('mv2-notas').value,
  });
  closeModal('modal-venta');
  loadVentas();
}

function closeModal(id) { document.getElementById(id).classList.remove('open'); }

// Check existing session
(async () => {
  const token = getToken();
  if (token) {
    const res = await api('/api/me');
    if (res.username) {
      document.getElementById('login-screen').style.display = 'none';
      document.getElementById('app').style.display = 'block';
      showSection('dashboard');
    } else {
      clearToken();
    }
  }
})();
</script>
</body>
</html>"""

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

        user = get_user_from_request(self)

        if path == '/api/me':
            self.send_json({'username': user})
            return

        if not user:
            self.send_json({'error': 'No autorizado'}, 401)
            return

        if path == '/api/dashboard':
            conn = get_db()
            c = conn.cursor()
            stock = c.execute("SELECT COUNT(*) FROM vehiculos WHERE estado='stock'").fetchone()[0]
            vendidos = c.execute("SELECT COUNT(*) FROM vehiculos WHERE estado='vendido'").fetchone()[0]
            clientes = c.execute("SELECT COUNT(*) FROM clientes").fetchone()[0]
            total = c.execute("SELECT SUM(precio) FROM ventas").fetchone()[0] or 0
            conn.close()
            self.send_json({'stock': stock, 'vendidos': vendidos, 'clientes': clientes, 'ventas_total': total})
            return

        if path == '/api/vehiculos':
            q = qs.get('q', [''])[0]
            estado = qs.get('estado', [''])[0]
            conn = get_db()
            sql = "SELECT * FROM vehiculos WHERE (marca LIKE ? OR modelo LIKE ? OR chasis LIKE ? OR motor LIKE ?)"
            params = ['%'+q+'%']*4
            if estado:
                sql += " AND estado=?"
                params.append(estado)
            sql += " ORDER BY id DESC"
            rows = [dict(r) for r in conn.execute(sql, params).fetchall()]
            conn.close()
            self.send_json({'items': rows})
            return

        if path == '/api/clientes':
            q = qs.get('q', [''])[0]
            conn = get_db()
            rows = [dict(r) for r in conn.execute(
                "SELECT * FROM clientes WHERE nombre LIKE ? OR documento LIKE ? OR telefono LIKE ? ORDER BY nombre",
                ['%'+q+'%']*3).fetchall()]
            conn.close()
            self.send_json({'items': rows})
            return

        if path == '/api/ventas':
            conn = get_db()
            rows = [dict(r) for r in conn.execute("""
                SELECT v.id, v.fecha, v.precio,
                       veh.marca, veh.modelo, c.nombre as cliente
                FROM ventas v
                LEFT JOIN vehiculos veh ON v.vehiculo_id=veh.id
                LEFT JOIN clientes c ON v.cliente_id=c.id
                ORDER BY v.fecha DESC
            """).fetchall()]
            conn.close()
            self.send_json({'items': rows})
            return

        self.send_json({'error': 'Not found'}, 404)

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(length) or b'{}')
        path = self.path

        if path == '/api/login':
            conn = get_db()
            h = hashlib.sha256(body.get('password','').encode()).hexdigest()
            row = conn.execute("SELECT * FROM usuarios WHERE username=? AND password_hash=?",
                               (body.get('username'), h)).fetchone()
            conn.close()
            if row:
                token = make_token(row['username'])
                # Return token in JSON so JS can store it (works with HTTPS proxy)
                self.send_json({'ok': True, 'token': token})
            else:
                self.send_json({'error': 'Usuario o contrasena incorrectos'}, 401)
            return

        if path == '/api/logout':
            self.send_json({'ok': True})
            return

        user = get_user_from_request(self)
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
            conn.commit(); conn.close()
            self.send_json({'ok': True})
            return

        if path == '/api/clientes':
            conn = get_db()
            conn.execute("INSERT INTO clientes (nombre,documento,telefono,email,ciudad,direccion) VALUES (?,?,?,?,?,?)",
                (body.get('nombre'), body.get('documento'), body.get('telefono'),
                 body.get('email'), body.get('ciudad'), body.get('direccion')))
            conn.commit(); conn.close()
            self.send_json({'ok': True})
            return

        if path == '/api/ventas':
            conn = get_db()
            conn.execute("INSERT INTO ventas (vehiculo_id,cliente_id,precio,fecha,notas) VALUES (?,?,?,?,?)",
                (body.get('vehiculo_id'), body.get('cliente_id'), body.get('precio'),
                 body.get('fecha'), body.get('notas')))
            conn.execute("UPDATE vehiculos SET estado='vendido', fecha_venta=?, cliente_id=? WHERE id=?",
                (body.get('fecha'), body.get('cliente_id'), body.get('vehiculo_id')))
            conn.commit(); conn.close()
            self.send_json({'ok': True})
            return

        self.send_json({'error': 'Not found'}, 404)

    def do_PUT(self):
        length = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(length) or b'{}')
        path = self.path
        user = get_user_from_request(self)
        if not user:
            self.send_json({'error': 'No autorizado'}, 401)
            return

        m = re.match(r'/api/vehiculos/(\d+)', path)
        if m:
            vid = m.group(1)
            conn = get_db()
            conn.execute("""UPDATE vehiculos SET marca=?,modelo=?,anio=?,color=?,motor=?,chasis=?,
                km=?,proveedor=?,precio_compra=?,precio_venta=?,fecha_compra=?,notas=? WHERE id=?""",
                (body.get('marca'), body.get('modelo'), body.get('anio'), body.get('color'),
                 body.get('motor'), body.get('chasis'), body.get('km'), body.get('proveedor'),
                 body.get('precio_compra'), body.get('precio_venta'), body.get('fecha_compra'),
                 body.get('notas'), vid))
            conn.commit(); conn.close()
            self.send_json({'ok': True})
            return

        m = re.match(r'/api/clientes/(\d+)', path)
        if m:
            cid = m.group(1)
            conn = get_db()
            conn.execute("UPDATE clientes SET nombre=?,documento=?,telefono=?,email=?,ciudad=?,direccion=? WHERE id=?",
                (body.get('nombre'), body.get('documento'), body.get('telefono'),
                 body.get('email'), body.get('ciudad'), body.get('direccion'), cid))
            conn.commit(); conn.close()
            self.send_json({'ok': True})
            return

        self.send_json({'error': 'Not found'}, 404)

    def log_message(self, format, *args): pass

if __name__ == '__main__':
    try:
        server = http.server.HTTPServer(('0.0.0.0', PORT), RequestHandler)
        print(f"AutomotoraGV corriendo en puerto {PORT}")
        server.serve_forever()
    except Exception as e:
        print(f"Error: {e}")
