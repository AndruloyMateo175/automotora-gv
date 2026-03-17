#!/usr/bin/env python3
"""
AutomotoraGV - Sistema de Gestion de Vehiculos
"""
import json
import sqlite3
import hashlib
import os
import secrets
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

PORT = int(os.environ.get('PORT', 8765))
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
    c.execute('''CREATE TABLE IF NOT EXISTS ventas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT, cliente TEXT, marca TEXT, modelo TEXT,
        chasis TEXT, motor TEXT, precio_usd REAL, precio_uyu REAL,
        documento TEXT, tipo_doc TEXT, pais TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS compras (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT, proveedor TEXT, marca TEXT, modelo TEXT,
        chasis TEXT, motor TEXT, precio_usd REAL, precio_uyu REAL, moneda TEXT, detalle TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT, documento TEXT UNIQUE, tipo_doc TEXT, pais TEXT
    )''')
    conn.commit()
    conn.close()

def check_session(handler):
    auth = handler.headers.get('Authorization', '')
    if auth.startswith('Bearer '):
        return SESSIONS.get(auth[7:])
    return None

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AutomotoraGV</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#0a0a0f;--sidebar:#111118;--card:#16161f;--border:#2a2a3a;
  --accent:#c9a84c;--accent2:#e8c87a;--text:#e8e8f0;--muted:#6b6b80;
  --red:#e05555;--green:#4caf7d;
}
body{background:var(--bg);color:var(--text);font-family:'Segoe UI',system-ui,sans-serif;min-height:100vh;display:flex}
#login-screen{display:flex;align-items:center;justify-content:center;width:100%;min-height:100vh}
.login-box{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:48px 40px;width:360px;text-align:center}
.login-logo{font-size:28px;font-weight:800;letter-spacing:4px;color:var(--accent);margin-bottom:8px}
.login-sub{color:var(--muted);font-size:13px;margin-bottom:32px}
.login-box input{width:100%;background:#0d0d16;border:1px solid var(--border);border-radius:8px;padding:12px 14px;color:var(--text);font-size:14px;margin-bottom:12px;outline:none}
.login-box input:focus{border-color:var(--accent)}
.btn{width:100%;background:var(--accent);color:#000;font-weight:700;font-size:14px;padding:13px;border:none;border-radius:8px;cursor:pointer;letter-spacing:1px}
.btn:hover{background:var(--accent2)}
.login-err{color:var(--red);font-size:13px;margin-top:8px;min-height:20px}
#app{display:none;width:100%;min-height:100vh}
.sidebar{position:fixed;left:0;top:0;bottom:0;width:220px;background:var(--sidebar);border-right:1px solid var(--border);display:flex;flex-direction:column;z-index:100}
.sidebar-logo{padding:24px 20px 16px;border-bottom:1px solid var(--border)}
.brand{font-size:18px;font-weight:800;letter-spacing:3px;color:var(--accent)}
.user-label{font-size:12px;color:var(--muted);margin-top:4px}
.nav{flex:1;padding:16px 0}
.nav-item{display:flex;align-items:center;gap:12px;padding:12px 20px;cursor:pointer;color:var(--muted);font-size:14px;font-weight:500;border-left:3px solid transparent;transition:.15s}
.nav-item:hover{color:var(--text);background:rgba(255,255,255,.04)}
.nav-item.active{color:var(--accent);border-left-color:var(--accent);background:rgba(201,168,76,.06)}
.nav-icon{font-size:16px;width:22px;text-align:center}
.sidebar-footer{padding:16px 20px;border-top:1px solid var(--border)}
.logout-btn{width:100%;background:transparent;border:1px solid var(--border);color:var(--muted);padding:9px;border-radius:7px;cursor:pointer;font-size:13px}
.logout-btn:hover{border-color:var(--red);color:var(--red)}
.main{margin-left:220px;padding:32px;flex:1}
.page{display:none}.page.active{display:block}
.page-header{display:flex;align-items:center;margin-bottom:28px}
.page-title{font-size:22px;font-weight:700}
.badge{background:var(--accent);color:#000;font-size:11px;font-weight:700;padding:3px 8px;border-radius:20px;margin-left:10px}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:16px;margin-bottom:28px}
.stat-card{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:20px}
.stat-label{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:8px}
.stat-value{font-size:28px;font-weight:800;color:var(--accent)}
.toolbar{display:flex;gap:12px;margin-bottom:20px}
.search-box{flex:1;background:var(--card);border:1px solid var(--border);border-radius:8px;padding:10px 14px;color:var(--text);font-size:14px;outline:none}
.search-box:focus{border-color:var(--accent)}
.table-wrap{background:var(--card);border:1px solid var(--border);border-radius:12px;overflow:hidden}
table{width:100%;border-collapse:collapse;font-size:13px}
th{background:#0d0d18;color:var(--muted);font-weight:600;font-size:11px;text-transform:uppercase;letter-spacing:.8px;padding:12px 14px;text-align:left;border-bottom:1px solid var(--border)}
td{padding:12px 14px;border-bottom:1px solid rgba(42,42,58,.5);color:var(--text)}
tr:last-child td{border-bottom:none}
tr:hover td{background:rgba(255,255,255,.02)}
.mono{font-family:'Courier New',monospace;font-size:12px;color:var(--accent2)}
.price{font-weight:600;color:var(--green)}
.pagination{display:flex;align-items:center;justify-content:space-between;padding:14px 16px;border-top:1px solid var(--border);font-size:13px;color:var(--muted)}
.page-btns{display:flex;gap:6px}
.page-btn{background:var(--card);border:1px solid var(--border);color:var(--text);padding:6px 12px;border-radius:6px;cursor:pointer;font-size:12px}
.page-btn:hover{border-color:var(--accent);color:var(--accent)}
.page-btn.active-pg{background:var(--accent);color:#000;border-color:var(--accent);font-weight:700}
.page-btn:disabled{opacity:.3;cursor:default}
.hamburger{display:none;position:fixed;top:14px;left:14px;z-index:200;background:var(--accent);border:none;border-radius:8px;padding:8px 10px;cursor:pointer;font-size:18px;color:#000}
.overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,.6);z-index:99}
.empty{text-align:center;padding:60px;color:var(--muted);font-size:15px}
@media(max-width:768px){
  .hamburger{display:block}
  .sidebar{transform:translateX(-100%);transition:transform .25s}
  .sidebar.open{transform:translateX(0)}
  .overlay.open{display:block}
  .main{margin-left:0;padding:16px;padding-top:60px}
  .stats{grid-template-columns:1fr 1fr}
  .table-wrap{overflow-x:auto}
  table{min-width:600px}
}
</style>
</head>
<body>
<div id="login-screen">
  <div class="login-box">
    <div class="login-logo">BMW GV</div>
    <div class="login-sub">Sistema de Gestion</div>
    <input type="text" id="inp-user" placeholder="Usuario" autocomplete="username">
    <input type="password" id="inp-pass" placeholder="Contrasena" autocomplete="current-password">
    <button class="btn" onclick="doLogin()">INGRESAR</button>
    <div class="login-err" id="login-err"></div>
  </div>
</div>
<button class="hamburger" onclick="toggleSidebar()">&#9776;</button>
<div class="overlay" id="overlay" onclick="toggleSidebar()"></div>
<div id="app">
  <div class="sidebar" id="sidebar">
    <div class="sidebar-logo">
      <div class="brand">BMW GV</div>
      <div class="user-label" id="user-label"></div>
    </div>
    <nav class="nav">
      <div class="nav-item active" onclick="showPage('dashboard')" id="nav-dashboard"><span class="nav-icon">&#9632;</span>Dashboard</div>
      <div class="nav-item" onclick="showPage('vendidos')" id="nav-vendidos"><span class="nav-icon">&#8593;</span>Vendidos</div>
      <div class="nav-item" onclick="showPage('comprados')" id="nav-comprados"><span class="nav-icon">&#8595;</span>Comprados</div>
      <div class="nav-item" onclick="showPage('clientes')" id="nav-clientes"><span class="nav-icon">&#9786;</span>Clientes</div>
      <div class="nav-item" onclick="showPage('stock')" id="nav-stock"><span class="nav-icon">&#9632;</span>Stock</div>
      <div class="nav-item" onclick="showPage('facturacion')" id="nav-facturacion"><span class="nav-icon">&#36;</span>Facturacion</div>
    </nav>
    <div class="sidebar-footer">
      <button class="logout-btn" onclick="doLogout()">Cerrar sesion</button>
    </div>
  </div>
  <div class="main">
    <div class="page active" id="page-dashboard">
      <div class="page-header"><span class="page-title">Dashboard</span></div>
      <div class="stats">
        <div class="stat-card"><div class="stat-label">Vendidos</div><div class="stat-value" id="stat-vendidos">-</div></div>
        <div class="stat-card"><div class="stat-label">Comprados</div><div class="stat-value" id="stat-comprados">-</div></div>
        <div class="stat-card"><div class="stat-label">Clientes</div><div class="stat-value" id="stat-clientes">-</div></div>
        <div class="stat-card"><div class="stat-label">Stock</div><div class="stat-value" id="stat-stock">0</div></div>
      </div>
    </div>
    <div class="page" id="page-vendidos">
      <div class="page-header"><span class="page-title">Vendidos <span class="badge" id="badge-vendidos">0</span></span></div>
      <div class="toolbar"><input class="search-box" id="search-vendidos" placeholder="Buscar marca, modelo, chasis, motor, cliente..." oninput="filterV()"></div>
      <div class="table-wrap">
        <table><thead><tr><th>Fecha</th><th>Cliente</th><th>Marca / Modelo</th><th>Chasis</th><th>Motor</th><th>Precio USD</th></tr></thead>
        <tbody id="tbody-vendidos"></tbody></table>
        <div class="pagination" id="pag-vendidos"></div>
      </div>
    </div>
    <div class="page" id="page-comprados">
      <div class="page-header"><span class="page-title">Comprados <span class="badge" id="badge-comprados">0</span></span></div>
      <div class="toolbar"><input class="search-box" id="search-comprados" placeholder="Buscar proveedor, marca, modelo, chasis, motor..." oninput="filterC()"></div>
      <div class="table-wrap">
        <table><thead><tr><th>Fecha</th><th>Proveedor</th><th>Marca / Modelo</th><th>Chasis</th><th>Motor</th><th>Precio USD</th></tr></thead>
        <tbody id="tbody-comprados"></tbody></table>
        <div class="pagination" id="pag-comprados"></div>
      </div>
    </div>
    <div class="page" id="page-clientes">
      <div class="page-header"><span class="page-title">Clientes <span class="badge" id="badge-clientes">0</span></span></div>
      <div class="toolbar"><input class="search-box" id="search-clientes" placeholder="Buscar nombre, documento..." oninput="filterL()"></div>
      <div class="table-wrap">
        <table><thead><tr><th>Nombre</th><th>Documento</th><th>Tipo Doc</th><th>Pais</th></tr></thead>
        <tbody id="tbody-clientes"></tbody></table>
        <div class="pagination" id="pag-clientes"></div>
      </div>
    </div>
    <div class="page" id="page-stock">
      <div class="page-header"><span class="page-title">Stock</span></div>
      <div class="empty">Sin datos de stock cargados</div>
    </div>
    <div class="page" id="page-facturacion">
      <div class="page-header"><span class="page-title">Facturacion</span></div>
      <div class="empty">Sin datos de facturacion cargados</div>
    </div>
  </div>
</div>
<script>
const PS=50;
let TOK=localStorage.getItem('gv_tok')||'';
let allV=[],allC=[],allL=[];
let fV=[],fC=[],fL=[];
let pV=1,pC=1,pL=1;

async function api(path,opts){
  try{
    const r=await fetch(path,{...opts,headers:{'Authorization':'Bearer '+TOK,'Content-Type':'application/json',...((opts&&opts.headers)||{})}});
    if(r.status===401){doLogout();return null;}
    return await r.json();
  }catch(e){return null;}
}

async function doLogin(){
  const u=document.getElementById('inp-user').value.trim();
  const p=document.getElementById('inp-pass').value;
  const err=document.getElementById('login-err');
  err.textContent='';
  const r=await fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({usuario:u,password:p})});
  const d=await r.json();
  if(d.ok){
    TOK=d.token;
    localStorage.setItem('gv_tok',TOK);
    document.getElementById('user-label').textContent=d.nombre;
    launchApp();
  }else{err.textContent='Usuario o contrasena incorrectos';}
}

function doLogout(){
  TOK='';localStorage.removeItem('gv_tok');
  document.getElementById('app').style.display='none';
  document.getElementById('login-screen').style.display='flex';
}

function launchApp(){
  document.getElementById('login-screen').style.display='none';
  document.getElementById('app').style.display='flex';
  loadStats();loadV();loadC();loadL();
}

async function loadStats(){
  const d=await api('/api/stats');
  if(!d)return;
  document.getElementById('stat-vendidos').textContent=d.vendidos;
  document.getElementById('stat-comprados').textContent=d.comprados;
  document.getElementById('stat-clientes').textContent=d.clientes;
}

async function loadV(){
  const d=await api('/api/ventas?limit=5000');
  if(!d)return;
  allV=d.data||[];fV=allV;pV=1;
  document.getElementById('badge-vendidos').textContent=allV.length;
  renderV();
}
async function loadC(){
  const d=await api('/api/compras?limit=5000');
  if(!d)return;
  allC=d.data||[];fC=allC;pC=1;
  document.getElementById('badge-comprados').textContent=allC.length;
  renderC();
}
async function loadL(){
  const d=await api('/api/clientes?limit=5000');
  if(!d)return;
  allL=d.data||[];fL=allL;pL=1;
  document.getElementById('badge-clientes').textContent=allL.length;
  renderL();
}

function filterV(){const q=document.getElementById('search-vendidos').value.toLowerCase();fV=q?allV.filter(r=>['marca','modelo','chasis','motor','cliente'].some(k=>(r[k]||'').toLowerCase().includes(q))):allV;pV=1;renderV();}
function filterC(){const q=document.getElementById('search-comprados').value.toLowerCase();fC=q?allC.filter(r=>['marca','modelo','chasis','motor','proveedor'].some(k=>(r[k]||'').toLowerCase().includes(q))):allC;pC=1;renderC();}
function filterL(){const q=document.getElementById('search-clientes').value.toLowerCase();fL=q?allL.filter(r=>['nombre','documento'].some(k=>(r[k]||'').toLowerCase().includes(q))):allL;pL=1;renderL();}

function pg(arr,p){const tot=arr.length,pages=Math.max(1,Math.ceil(tot/PS)),cur=Math.min(p,pages);return{rows:arr.slice((cur-1)*PS,cur*PS),page:cur,pages,tot};}

function pagHTML(p,pages,tot,fn){
  if(pages<=1)return '<span>'+tot+' registros</span>';
  let b='<button class="page-btn" onclick="'+fn+'('+(p-1)+')" '+(p>1?'':'disabled')+'>&#8592;</button>';
  const lo=Math.max(1,p-2),hi=Math.min(pages,p+2);
  if(lo>1)b+='<button class="page-btn" onclick="'+fn+'(1)">1</button>'+(lo>2?'<span style="padding:0 4px">...</span>':'');
  for(let i=lo;i<=hi;i++)b+='<button class="page-btn'+(i===p?' active-pg':'')+'" onclick="'+fn+'('+i+')">'+i+'</button>';
  if(hi<pages)b+=(hi<pages-1?'<span style="padding:0 4px">...</span>':'')+'<button class="page-btn" onclick="'+fn+'('+pages+')">'+pages+'</button>';
  b+='<button class="page-btn" onclick="'+fn+'('+(p+1)+')" '+(p<pages?'':'disabled')+'>&#8594;</button>';
  return '<span>'+tot+' registros</span><div class="page-btns">'+b+'</div>';
}

function fmtD(s){return s?(s+'').substring(0,10):'-';}
function fmtU(v){return(v||v===0)?'$'+Number(v).toLocaleString('en-US',{maximumFractionDigits:0}):'-';}

function renderV(){
  const {rows,page,pages,tot}=pg(fV,pV);pV=page;
  const tb=document.getElementById('tbody-vendidos');
  tb.innerHTML=rows.length?rows.map(r=>'<tr><td>'+fmtD(r.fecha)+'</td><td>'+(r.cliente||'-')+'</td><td>'+(r.marca||'-')+' '+(r.modelo||'')+'</td><td class="mono">'+(r.chasis||'-')+'</td><td class="mono">'+(r.motor||'-')+'</td><td class="price">'+fmtU(r.precio_usd)+'</td></tr>').join(''):'<tr><td colspan="6" style="text-align:center;padding:40px;color:var(--muted)">Sin registros</td></tr>';
  document.getElementById('pag-vendidos').innerHTML=pagHTML(page,pages,tot,'goV');
}
function renderC(){
  const {rows,page,pages,tot}=pg(fC,pC);pC=page;
  const tb=document.getElementById('tbody-comprados');
  tb.innerHTML=rows.length?rows.map(r=>'<tr><td>'+fmtD(r.fecha)+'</td><td>'+(r.proveedor||'-')+'</td><td>'+(r.marca||'-')+' '+(r.modelo||'')+'</td><td class="mono">'+(r.chasis||'-')+'</td><td class="mono">'+(r.motor||'-')+'</td><td class="price">'+fmtU(r.precio_usd)+'</td></tr>').join(''):'<tr><td colspan="6" style="text-align:center;padding:40px;color:var(--muted)">Sin registros</td></tr>';
  document.getElementById('pag-comprados').innerHTML=pagHTML(page,pages,tot,'goC');
}
function renderL(){
  const {rows,page,pages,tot}=pg(fL,pL);pL=page;
  const tb=document.getElementById('tbody-clientes');
  tb.innerHTML=rows.length?rows.map(r=>'<tr><td>'+(r.nombre||'-')+'</td><td class="mono">'+(r.documento||'-')+'</td><td>'+(r.tipo_doc||'-')+'</td><td>'+(r.pais||'-')+'</td></tr>').join(''):'<tr><td colspan="4" style="text-align:center;padding:40px;color:var(--muted)">Sin registros</td></tr>';
  document.getElementById('pag-clientes').innerHTML=pagHTML(page,pages,tot,'goL');
}

function goV(p){pV=p;renderV();scrollTo(0,0);}
function goC(p){pC=p;renderC();scrollTo(0,0);}
function goL(p){pL=p;renderL();scrollTo(0,0);}

function showPage(name){
  document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n=>n.classList.remove('active'));
  document.getElementById('page-'+name).classList.add('active');
  document.getElementById('nav-'+name).classList.add('active');
  if(window.innerWidth<=768)toggleSidebar();
}
function toggleSidebar(){
  document.getElementById('sidebar').classList.toggle('open');
  document.getElementById('overlay').classList.toggle('open');
}
document.getElementById('inp-pass').addEventListener('keydown',e=>{if(e.key==='Enter')doLogin();});
if(TOK){api('/api/stats').then(d=>{if(d){const u=localStorage.getItem('gv_tok');document.getElementById('user-label').textContent='';launchApp();}else doLogout();});}
</script>
</body>
</html>"""

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): pass

    def send_json(self, data, code=200):
        body = json.dumps(data).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

    def send_html(self):
        body = HTML.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Authorization, Content-Type')
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)
        if path in ('/', '/index.html'):
            self.send_html(); return
        user = check_session(self)
        if not user:
            self.send_json({'error': 'unauthorized'}, 401); return
        if path == '/api/stats':
            conn = get_db()
            v = conn.execute('SELECT COUNT(*) FROM ventas').fetchone()[0]
            c = conn.execute('SELECT COUNT(*) FROM compras').fetchone()[0]
            l = conn.execute('SELECT COUNT(*) FROM clientes').fetchone()[0]
            conn.close()
            self.send_json({'vendidos': v, 'comprados': c, 'clientes': l}); return
        if path == '/api/ventas':
            lim = int(qs.get('limit', ['5000'])[0])
            off = int(qs.get('offset', ['0'])[0])
            conn = get_db()
            rows = conn.execute('SELECT * FROM ventas ORDER BY fecha DESC, id DESC LIMIT ? OFFSET ?', (lim, off)).fetchall()
            tot = conn.execute('SELECT COUNT(*) FROM ventas').fetchone()[0]
            conn.close()
            self.send_json({'data': [dict(r) for r in rows], 'total': tot}); return
        if path == '/api/compras':
            lim = int(qs.get('limit', ['5000'])[0])
            off = int(qs.get('offset', ['0'])[0])
            conn = get_db()
            rows = conn.execute('SELECT * FROM compras ORDER BY fecha DESC, id DESC LIMIT ? OFFSET ?', (lim, off)).fetchall()
            tot = conn.execute('SELECT COUNT(*) FROM compras').fetchone()[0]
            conn.close()
            self.send_json({'data': [dict(r) for r in rows], 'total': tot}); return
        if path == '/api/clientes':
            lim = int(qs.get('limit', ['5000'])[0])
            off = int(qs.get('offset', ['0'])[0])
            conn = get_db()
            rows = conn.execute('SELECT * FROM clientes ORDER BY nombre LIMIT ? OFFSET ?', (lim, off)).fetchall()
            tot = conn.execute('SELECT COUNT(*) FROM clientes').fetchone()[0]
            conn.close()
            self.send_json({'data': [dict(r) for r in rows], 'total': tot}); return
        self.send_response(404); self.end_headers()

    def do_POST(self):
        path = urlparse(self.path).path
        length = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(length)) if length else {}
        if path == '/api/login':
            u = body.get('usuario', '').strip()
            p = body.get('password', '')
            usr = USERS.get(u)
            if usr and usr['hash'] == hashlib.sha256(p.encode()).hexdigest():
                tok = secrets.token_hex(32)
                SESSIONS[tok] = {'usuario': u, 'nombre': usr['nombre']}
                self.send_json({'ok': True, 'token': tok, 'nombre': usr['nombre']}); return
            self.send_json({'ok': False}); return
        user = check_session(self)
        if not user:
            self.send_json({'error': 'unauthorized'}, 401); return
        if path == '/api/import':
            conn = get_db()
            c = conn.cursor()
            for r in body.get('ventas', []):
                c.execute('INSERT INTO ventas (fecha,cliente,marca,modelo,chasis,motor,precio_usd,precio_uyu,documento,tipo_doc,pais) VALUES (?,?,?,?,?,?,?,?,?,?,?)',
                    (r.get('fecha'),r.get('cliente'),r.get('marca'),r.get('modelo'),r.get('chasis'),r.get('motor'),r.get('precio_usd'),r.get('precio_uyu'),r.get('documento'),r.get('tipo_doc'),r.get('pais')))
            for r in body.get('compras', []):
                c.execute('INSERT INTO compras (fecha,proveedor,marca,modelo,chasis,motor,precio_usd,precio_uyu) VALUES (?,?,?,?,?,?,?,?)',
                    (r.get('fecha'),r.get('proveedor'),r.get('marca'),r.get('modelo'),r.get('chasis'),r.get('motor'),r.get('precio_usd'),r.get('precio_uyu')))
            for r in body.get('clientes', []):
                try:
                    c.execute('INSERT OR IGNORE INTO clientes (nombre,documento,tipo_doc,pais) VALUES (?,?,?,?)',
                        (r.get('nombre'),r.get('documento'),r.get('tipo_doc'),r.get('pais')))
                except: pass
            conn.commit(); conn.close()
            self.send_json({'ok': True}); return
        if path=='/api/clear':
            conn=get_db();conn.execute('DELETE FROM ventas');conn.execute('DELETE FROM compras');conn.execute('DELETE FROM clientes');conn.commit();conn.close();self.send_json({'ok':True});return
        self.send_response(404); self.end_headers()


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

if __name__ == '__main__':
    init_db()
    print(f'AutomotoraGV en puerto {PORT}')
    HTTPServer(('0.0.0.0', PORT), Handler).serve_forever()
