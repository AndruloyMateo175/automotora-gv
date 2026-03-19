#!/usr/bin/env python3
"""
BMW Punta del Este - Servidor Local
Ejecutar: python3 server.py
Acceder:  http://localhost:8765
"""

import http.server
import sqlite3
import json
import hashlib
import hmac
import base64
import datetime
import threading
import urllib.parse
import os
import sys
import time
import re
import secrets
import struct

# ── HTML INCRUSTADO ──────────────────────────────────────
HTML_CONTENT = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>BMW Punta del Este</title>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=Instrument+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
:root {
  --bg: #0f0f0f; --bg2: #161616; --bg3: #1e1e1e; --bg4: #252525;
  --bd: #2a2a2a; --bd2: #333;
  --tx: #f0ede8; --tx2: #9a9690; --tx3: #5a5752;
  --acc: #c8a96e; --acc2: #e8c98e; --accl: rgba(200,169,110,.12);
  --gn: #4ade80; --gnl: rgba(74,222,128,.1);
  --rd: #f87171; --rdl: rgba(248,113,113,.1);
  --bl: #60a5fa; --bll: rgba(96,165,250,.1);
  --fn: 'Instrument Sans',sans-serif; --fh: 'Syne',sans-serif; --mo: 'JetBrains Mono',monospace;
  --r: 10px; --rl: 14px;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{font-family:var(--fn);background:var(--bg);color:var(--tx);font-size:14px;line-height:1.5;min-height:100vh}

/* ── LOGIN ── */
#login-screen{display:flex;align-items:center;justify-content:center;min-height:100vh;background:var(--bg)}
.login-box{background:var(--bg2);border:1px solid var(--bd);border-radius:20px;padding:48px 40px;width:380px;max-width:96vw}
.login-logo{font-family:var(--fh);font-size:11px;text-transform:uppercase;letter-spacing:3px;color:var(--tx3);margin-bottom:6px}
.login-title{font-family:var(--fh);font-size:28px;font-weight:800;color:var(--acc);margin-bottom:4px}
.login-sub{font-size:12px;color:var(--tx3);margin-bottom:36px}
.lf-group{display:flex;flex-direction:column;gap:5px;margin-bottom:16px}
.lf-group label{font-size:11.5px;font-weight:600;color:var(--tx3);font-family:var(--fh);text-transform:uppercase;letter-spacing:.5px}
.lf-group input{font-family:var(--fn);font-size:14px;padding:10px 13px;border:1px solid var(--bd);border-radius:var(--r);background:var(--bg3);color:var(--tx);outline:none;transition:border-color .15s}
.lf-group input:focus{border-color:var(--acc)}
.login-btn{width:100%;font-family:var(--fh);font-size:14px;font-weight:700;padding:12px;border-radius:var(--r);border:none;cursor:pointer;background:var(--acc);color:#0f0f0f;margin-top:8px;transition:background .15s}
.login-btn:hover{background:var(--acc2)}
.login-err{color:var(--rd);font-size:12.5px;margin-top:10px;text-align:center;min-height:18px}

/* ── APP ── */
#app{display:none}
.sb{position:fixed;left:0;top:0;bottom:0;width:230px;background:var(--bg2);border-right:1px solid var(--bd);display:flex;flex-direction:column;z-index:100}
.sb-top{padding:24px 20px 20px;border-bottom:1px solid var(--bd)}
.sb-logo{font-size:10px;font-family:var(--fh);text-transform:uppercase;letter-spacing:2px;color:var(--tx3);margin-bottom:2px}
.sb-brand{font-family:var(--fh);font-size:20px;font-weight:800;color:var(--acc);line-height:1}
.sb-user{display:flex;align-items:center;gap:8px;margin-top:12px}
.sb-avatar{width:30px;height:30px;border-radius:50%;background:var(--accl);display:flex;align-items:center;justify-content:center;font-family:var(--fh);font-size:12px;font-weight:800;color:var(--acc);border:1px solid rgba(200,169,110,.2);flex-shrink:0}
.sb-uname{font-size:12px;font-weight:600;color:var(--tx2)}
.sb-rol{font-size:10px;color:var(--tx3)}
.nav{flex:1;padding:14px 10px;overflow-y:auto}
.nl{font-size:10px;font-family:var(--fh);text-transform:uppercase;letter-spacing:1.5px;color:var(--tx3);padding:0 10px;margin:16px 0 5px}
.nl:first-child{margin-top:2px}
.ni{display:flex;align-items:center;gap:9px;padding:8px 11px;border-radius:8px;cursor:pointer;color:var(--tx2);font-size:13px;font-weight:500;border:none;background:none;width:100%;text-align:left;transition:all .15s;position:relative}
.ni svg{opacity:.6;flex-shrink:0;transition:opacity .15s}
.ni:hover{background:var(--bg3);color:var(--tx)}
.ni:hover svg{opacity:1}
.ni.active{background:var(--accl);color:var(--acc2)}
.ni.active svg{opacity:1;color:var(--acc)}
.ni .badge-cnt{margin-left:auto;background:var(--bg4);color:var(--tx3);font-size:10px;font-family:var(--mo);padding:1px 6px;border-radius:20px}
.ni.active .badge-cnt{background:rgba(200,169,110,.2);color:var(--acc)}
.ni .badge-alert{margin-left:auto;background:var(--rdl);color:var(--rd);font-size:10px;font-family:var(--mo);padding:1px 6px;border-radius:20px;font-weight:700}
.sb-bot{padding:12px 20px;border-top:1px solid var(--bd)}
.sb-logout{font-family:var(--fn);font-size:12px;color:var(--tx3);cursor:pointer;display:flex;align-items:center;gap:6px;transition:color .15s;background:none;border:none;padding:4px 0}
.sb-logout:hover{color:var(--rd)}

.main{margin-left:230px;min-height:100vh}
.topbar{background:var(--bg2);border-bottom:1px solid var(--bd);padding:0 24px;height:54px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:50}
.topbar-title{font-family:var(--fh);font-size:16px;font-weight:700}
.topbar-sub{font-size:12px;color:var(--tx3);margin-left:10px}
.content{padding:22px 24px}

/* ── MENU PRINCIPAL ── */
.menu-hero{display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:calc(100vh - 54px);padding:40px 24px}
.menu-greeting{font-family:var(--fh);font-size:13px;color:var(--tx3);text-transform:uppercase;letter-spacing:2px;margin-bottom:4px}
.menu-title{font-family:var(--fh);font-size:30px;font-weight:800;margin-bottom:4px}
.menu-title span{color:var(--acc)}
.menu-sub{font-size:13px;color:var(--tx3);margin-bottom:44px}
.menu-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;width:100%;max-width:820px}
.mc{background:var(--bg2);border:1px solid var(--bd);border-radius:14px;padding:26px 22px;cursor:pointer;transition:all .2s;position:relative;overflow:hidden;display:flex;flex-direction:column;gap:14px}
.mc:hover{border-color:var(--acc);transform:translateY(-2px);box-shadow:0 10px 36px rgba(0,0,0,.5)}
.mc-icon{width:46px;height:46px;border-radius:10px;display:flex;align-items:center;justify-content:center}
.mc-label{font-size:10px;font-family:var(--fh);text-transform:uppercase;letter-spacing:1.5px;color:var(--tx3)}
.mc-name{font-family:var(--fh);font-size:18px;font-weight:800;color:var(--tx);line-height:1.1}
.mc-desc{font-size:12px;color:var(--tx3);line-height:1.5}
.mc-arrow{position:absolute;bottom:18px;right:18px;opacity:0;transition:all .2s}
.mc:hover .mc-arrow{opacity:1;transform:translateX(3px)}

/* ── TOOLBAR + TABLE ── */
.tb{display:flex;gap:8px;margin-bottom:14px;flex-wrap:wrap;align-items:center}
.sw{position:relative;flex:1;min-width:200px;max-width:340px}
.sw svg{position:absolute;left:10px;top:50%;transform:translateY(-50%);color:var(--tx3);pointer-events:none}
.sw input{width:100%;padding:8px 10px 8px 32px;font-size:13px;font-family:var(--fn);border:1px solid var(--bd);border-radius:var(--r);background:var(--bg3);color:var(--tx);outline:none;transition:border-color .15s}
.sw input:focus{border-color:var(--acc)}
.sw input::placeholder{color:var(--tx3)}
select.fi,input.fi{font-family:var(--fn);font-size:13px;padding:8px 10px;border:1px solid var(--bd);border-radius:var(--r);background:var(--bg3);color:var(--tx);outline:none;cursor:pointer;transition:border-color .15s}
select.fi:focus,input.fi:focus{border-color:var(--acc)}
.btn{font-family:var(--fn);font-size:13px;font-weight:500;padding:8px 16px;border-radius:var(--r);border:1px solid var(--bd);cursor:pointer;background:var(--bg3);color:var(--tx2);transition:all .15s;white-space:nowrap}
.btn:hover{border-color:var(--bd2);color:var(--tx);background:var(--bg4)}
.btn.pr{background:var(--acc);color:#0f0f0f;border-color:var(--acc);font-weight:600}
.btn.pr:hover{background:var(--acc2);border-color:var(--acc2)}
.btn.sm{font-size:11px;padding:4px 10px}
.btn.danger{border-color:var(--rdl);color:var(--rd)}
.btn.danger:hover{background:var(--rdl);border-color:var(--rd)}

.tc{background:var(--bg2);border:1px solid var(--bd);border-radius:var(--rl);overflow:hidden}
.tsc{overflow-x:auto}
table{width:100%;border-collapse:collapse;font-size:13px}
th{background:var(--bg3);text-align:left;font-weight:600;font-size:10.5px;color:var(--tx3);text-transform:uppercase;letter-spacing:.6px;padding:10px 14px;border-bottom:1px solid var(--bd);white-space:nowrap;cursor:pointer;font-family:var(--fh);user-select:none;transition:color .15s}
th:hover{color:var(--tx2)}
td{padding:9px 14px;border-bottom:1px solid var(--bd);color:var(--tx);vertical-align:middle}
tr:last-child td{border-bottom:none}
tr:hover td{background:rgba(255,255,255,.02)}
.mo{font-family:var(--mo);font-size:12px;color:var(--tx2)}
.pr-val{font-family:var(--mo);font-size:13px;font-weight:500;color:var(--acc2)}
.badge{display:inline-block;font-size:11px;font-weight:600;padding:2px 9px;border-radius:20px;white-space:nowrap;font-family:var(--fh);letter-spacing:.3px}

/* ── PAG ── */
.pag{display:flex;align-items:center;justify-content:space-between;padding:10px 14px;border-top:1px solid var(--bd);background:var(--bg3)}
.pi{font-size:12px;color:var(--tx3)}
.pbs{display:flex;gap:4px}
.pb{font-family:var(--mo);font-size:12px;padding:3px 9px;border-radius:6px;border:1px solid var(--bd);background:var(--bg4);cursor:pointer;color:var(--tx3);transition:all .12s}
.pb:hover{background:var(--bg3);color:var(--tx)}
.pb.ac{background:var(--acc);color:#0f0f0f;border-color:var(--acc);font-weight:700}

/* ── MODAL ── */
.ov{display:none;position:fixed;inset:0;background:rgba(0,0,0,.7);z-index:200;align-items:center;justify-content:center;backdrop-filter:blur(4px)}
.ov.op{display:flex}
.mo-box{background:var(--bg2);border:1px solid var(--bd2);border-radius:var(--rl);width:560px;max-width:96vw;max-height:90vh;overflow-y:auto;box-shadow:0 8px 40px rgba(0,0,0,.6);animation:slideUp .2s ease}
.mo-box.wide{width:720px}
@keyframes slideUp{from{transform:translateY(16px);opacity:0}to{transform:translateY(0);opacity:1}}
.mh{padding:18px 22px 14px;border-bottom:1px solid var(--bd);display:flex;align-items:center;justify-content:space-between}
.mh h2{font-family:var(--fh);font-size:16px;font-weight:700}
.mc-close{background:none;border:none;cursor:pointer;color:var(--tx3);font-size:20px;line-height:1;padding:4px 6px;border-radius:6px;transition:all .12s}
.mc-close:hover{background:var(--bg3);color:var(--tx)}
.mb{padding:18px 22px}
.mf{padding:12px 22px;border-top:1px solid var(--bd);display:flex;justify-content:flex-end;gap:8px;background:var(--bg3);border-radius:0 0 var(--rl) var(--rl)}
.fg{display:grid;grid-template-columns:1fr 1fr;gap:11px}
.fi-g{display:flex;flex-direction:column;gap:4px}
.fi-g.full{grid-column:1/-1}
.fi-g.span3{grid-column:1/-1}
.fi-g label{font-size:11px;font-weight:600;color:var(--tx3);font-family:var(--fh);text-transform:uppercase;letter-spacing:.5px}
.fi-g input,.fi-g select,.fi-g textarea{font-family:var(--fn);font-size:13px;padding:8px 11px;border:1px solid var(--bd);border-radius:var(--r);background:var(--bg3);color:var(--tx);outline:none;transition:border-color .15s}
.fi-g input:focus,.fi-g select:focus,.fi-g textarea:focus{border-color:var(--acc)}
.fi-g textarea{resize:vertical;min-height:70px}
.fi-g input::placeholder{color:var(--tx3)}

/* ── DETAIL ROWS ── */
.dr{display:flex;gap:12px;padding:7px 0;border-bottom:1px solid var(--bd);font-size:13px}
.dr:last-child{border-bottom:none}
.dl{color:var(--tx3);width:120px;flex-shrink:0;font-size:11px;font-family:var(--fh);text-transform:uppercase;letter-spacing:.4px;padding-top:1px}
.dv{color:var(--tx);word-break:break-all;flex:1}

/* ── BRAND CHIPS ── */
.brand-bar{display:flex;flex-wrap:wrap;gap:7px;margin-bottom:14px}
.bchip{display:flex;align-items:center;gap:7px;padding:6px 13px;border-radius:9px;border:1px solid var(--bd);background:var(--bg2);cursor:pointer;transition:all .15s;user-select:none;font-family:var(--fh);font-size:12px;font-weight:700}
.bchip:hover{border-color:var(--bd2);background:var(--bg3)}
.bchip.all{background:var(--bg3)}
.bchip.all.active{background:var(--acc);border-color:var(--acc);color:#0f0f0f}
.bchip-cnt{font-family:var(--mo);font-size:11px;opacity:.7}

/* ── LOADING / EMPTY ── */
.loading{text-align:center;padding:48px;color:var(--tx3);font-size:13px}
.loading-spin{display:inline-block;width:20px;height:20px;border:2px solid var(--bd2);border-top-color:var(--acc);border-radius:50%;animation:spin .7s linear infinite;margin-bottom:10px}
@keyframes spin{to{transform:rotate(360deg)}}
.empty{text-align:center;padding:48px;color:var(--tx3);font-size:13px}
.empty-icon{font-size:32px;margin-bottom:8px}

/* ── NEGOCIOS ── */
.neg-card{background:var(--bg2);border:1px solid var(--bd);border-radius:var(--rl);padding:18px 20px;margin-bottom:10px;transition:border-color .15s;cursor:pointer}
.neg-card:hover{border-color:var(--bd2)}
.neg-card-header{display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:10px}
.neg-cliente{font-family:var(--fh);font-size:15px;font-weight:700}
.neg-vehiculo{font-size:12px;color:var(--tx3);margin-top:2px}
.neg-metas{display:flex;gap:10px;flex-wrap:wrap}
.neg-meta{font-size:11.5px;color:var(--tx2)}
.neg-cuotas-bar{margin-top:12px}
.neg-cuotas-label{display:flex;justify-content:space-between;font-size:11px;color:var(--tx3);margin-bottom:5px}
.neg-cuotas-track{background:var(--bg4);border-radius:4px;height:4px;overflow:hidden}
.neg-cuotas-fill{height:100%;border-radius:4px;background:var(--gn);transition:width .4s}

/* ── STOCK ── */
.stock-low{color:var(--rd) !important}
.stock-ok{color:var(--gn) !important}

/* ── FACTURACIÓN ── */
.fac-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:24px}
.fac-card{background:var(--bg2);border:1px solid var(--bd);border-radius:var(--rl);padding:22px 24px;position:relative;overflow:hidden}
.fac-card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px}
.fac-card.v::before{background:var(--bl)}
.fac-card.c::before{background:var(--acc)}
.fac-card.s::before{background:var(--gn)}
.fc-label{font-size:11px;font-family:var(--fh);text-transform:uppercase;letter-spacing:1px;color:var(--tx3);margin-bottom:10px}
.fc-val{font-family:var(--mo);font-size:26px;font-weight:700;line-height:1;margin-bottom:4px}
.fc-sub{font-size:12px;color:var(--tx3)}

/* ── CUOTAS ── */
.cuota-row{display:flex;align-items:center;justify-content:space-between;padding:9px 0;border-bottom:1px solid var(--bd);gap:12px}
.cuota-row:last-child{border-bottom:none}
.cuota-num{font-family:var(--mo);font-size:11px;color:var(--tx3);width:40px;flex-shrink:0}
.cuota-fecha{font-family:var(--mo);font-size:12px;color:var(--tx2);flex:1}
.cuota-monto{font-family:var(--mo);font-size:13px;font-weight:600;color:var(--acc2)}
.cuota-pagada{color:var(--gn);font-size:11px;font-family:var(--fh);font-weight:700}
.cuota-vencida{color:var(--rd);font-size:11px;font-family:var(--fh);font-weight:700}

/* ── TOAST ── */
.toast{position:fixed;bottom:24px;right:24px;background:var(--bg3);border:1px solid var(--bd2);border-radius:10px;padding:12px 18px;font-size:13px;color:var(--tx);z-index:999;transform:translateY(20px);opacity:0;transition:all .25s;box-shadow:0 4px 20px rgba(0,0,0,.4)}
.toast.show{transform:translateY(0);opacity:1}
.toast.ok{border-left:3px solid var(--gn)}
.toast.err{border-left:3px solid var(--rd)}

/* ── SYNC BUTTON ── */
.sync-btn{display:flex;align-items:center;gap:6px;font-family:var(--fn);font-size:12px;font-weight:500;padding:6px 14px;border-radius:8px;border:1px solid var(--bd);cursor:pointer;background:var(--bg3);color:var(--tx2);transition:all .15s}
.sync-btn:hover{border-color:var(--acc);color:var(--acc)}
.sync-btn.syncing svg{animation:spin .7s linear infinite}

/* ── PAGE ── */
.page{display:none}
.page.active{display:block}

/* ── SCROLLBAR ── */
::-webkit-scrollbar{width:5px;height:5px}
::-webkit-scrollbar-track{background:var(--bg)}
::-webkit-scrollbar-thumb{background:var(--bd2);border-radius:3px}

/* ── SYNC MODAL ── */
.sync-log-line{font-family:var(--mo);font-size:12px;padding:4px 0;border-bottom:1px solid var(--bd);color:var(--tx2)}
.sync-log-line.ok{color:var(--gn)}
.sync-log-line.err{color:var(--rd)}
.sync-progress{background:var(--bg4);border-radius:6px;height:8px;overflow:hidden;margin:10px 0}
.sync-progress-fill{height:100%;background:var(--acc);border-radius:6px;transition:width .3s;width:0%}
</style>
</head>
<body>

<!-- ── LOGIN ── -->
<div id="login-screen">
  <div class="login-box">
    <div class="login-logo">Mofidec S.A.</div>
    <div class="login-title">BMW Punta del Este</div>
    <div class="login-sub">Sistema de gestión · Iniciá sesión</div>
    <div class="lf-group">
      <label>Usuario</label>
      <input id="l-user" placeholder="gonzalo / andres / guillermo" autocomplete="username" onkeydown="if(event.key==='Enter')doLogin()">
    </div>
    <div class="lf-group">
      <label>Contraseña</label>
      <input id="l-pass" type="password" placeholder="••••••••" autocomplete="current-password" onkeydown="if(event.key==='Enter')doLogin()">
    </div>
    <button class="login-btn" onclick="doLogin()">Ingresar</button>
    <div class="login-err" id="l-err"></div>
  </div>
</div>

<!-- ── APP ── -->
<div id="app">

<!-- SIDEBAR -->
<nav class="sb">
  <div class="sb-top">
    <div class="sb-logo">BMW Punta del Este</div>
    <div class="sb-brand">Gestión</div>
    <div class="sb-user">
      <div class="sb-avatar" id="sb-av">?</div>
      <div>
        <div class="sb-uname" id="sb-nombre">—</div>
        <div class="sb-rol" id="sb-rol">—</div>
      </div>
    </div>
  </div>
  <div class="nav">
    <div class="nl">Principal</div>
    <button class="ni active" onclick="nav('menu',this)" id="nav-menu">
      <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/></svg>
      Menú
    </button>
    <div class="nl">Vehículos</div>
    <button class="ni" onclick="nav('ventas',this)" id="nav-ventas">
      <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>
      Vendidos
      <span class="badge-cnt" id="cnt-v">—</span>
    </button>
    <button class="ni" onclick="nav('compras',this)" id="nav-compras">
      <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 01-8 0"/></svg>
      Comprados
      <span class="badge-cnt" id="cnt-c">—</span>
    </button>
    <div class="nl">Personas</div>
    <button class="ni" onclick="nav('clientes',this)" id="nav-clientes">
      <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75"/></svg>
      Clientes
      <span class="badge-cnt" id="cnt-cl">—</span>
    </button>
    <div class="nl">Negocio</div>
    <button class="ni" onclick="nav('negocios',this)" id="nav-negocios">
      <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/></svg>
      Negocios
      <span class="badge-cnt" id="cnt-neg">—</span>
    </button>
    <button class="ni" onclick="nav('facturacion',this)" id="nav-facturacion">
      <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
      Facturación
    </button>
    <div class="nl">Inventario</div>
    <button class="ni" onclick="nav('stock',this)" id="nav-stock">
      <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8"/><path d="M10 12h4"/></svg>
      Stock
      <span class="badge-cnt" id="cnt-stk">—</span>
    </button>
  </div>
  <div class="sb-bot">
    <button class="sb-logout" onclick="doLogout()">
      <svg width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
      Cerrar sesión
    </button>
  </div>
</nav>

<main class="main">

<!-- MENU -->
<div id="page-menu" class="page active">
  <div class="topbar"><div style="display:flex;align-items:center"><div class="topbar-title">BMW Punta del Este</div></div>
    <button class="sync-btn" id="sync-btn" onclick="openSync()">
      <svg width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15"/></svg>
      Actualizar desde eFactura
    </button>
  </div>
  <div class="menu-hero">
    <div class="menu-greeting">Bienvenido</div>
    <div class="menu-title">BMW <span>Punta del Este</span></div>
    <div class="menu-sub" id="menu-fecha-sub">Sistema de gestión</div>
    <div class="menu-grid">
      <div class="mc" onclick="nav('clientes',document.getElementById('nav-clientes'))">
        <div class="mc-icon" style="background:var(--gnl)"><svg width="22" height="22" fill="none" stroke="var(--gn)" stroke-width="1.7" viewBox="0 0 24 24"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75"/></svg></div>
        <div><div class="mc-label">Personas</div><div class="mc-name">Clientes</div><div class="mc-desc">Buscá por nombre, apellido o documento</div></div>
        <svg class="mc-arrow" width="16" height="16" fill="none" stroke="var(--acc)" stroke-width="2.5" viewBox="0 0 24 24"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
      </div>
      <div class="mc" onclick="nav('ventas',document.getElementById('nav-ventas'))">
        <div class="mc-icon" style="background:var(--bll)"><svg width="22" height="22" fill="none" stroke="var(--bl)" stroke-width="1.7" viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg></div>
        <div><div class="mc-label">Vehículos</div><div class="mc-name">Autos Vendidos</div><div class="mc-desc">Historial completo de ventas con cliente y chasis</div></div>
        <svg class="mc-arrow" width="16" height="16" fill="none" stroke="var(--acc)" stroke-width="2.5" viewBox="0 0 24 24"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
      </div>
      <div class="mc" onclick="nav('compras',document.getElementById('nav-compras'))">
        <div class="mc-icon" style="background:var(--accl)"><svg width="22" height="22" fill="none" stroke="var(--acc)" stroke-width="1.7" viewBox="0 0 24 24"><path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 01-8 0"/></svg></div>
        <div><div class="mc-label">Inventario</div><div class="mc-name">Autos Comprados</div><div class="mc-desc">Registro de compras por proveedor y modelo</div></div>
        <svg class="mc-arrow" width="16" height="16" fill="none" stroke="var(--acc)" stroke-width="2.5" viewBox="0 0 24 24"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
      </div>
      <div class="mc" onclick="nav('negocios',document.getElementById('nav-negocios'))">
        <div class="mc-icon" style="background:rgba(192,132,252,.1)"><svg width="22" height="22" fill="none" stroke="#c084fc" stroke-width="1.7" viewBox="0 0 24 24"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/></svg></div>
        <div><div class="mc-label">Negocio</div><div class="mc-name">Negocios</div><div class="mc-desc">Gestión de operaciones y cuotas pendientes</div></div>
        <svg class="mc-arrow" width="16" height="16" fill="none" stroke="var(--acc)" stroke-width="2.5" viewBox="0 0 24 24"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
      </div>
      <div class="mc" onclick="nav('stock',document.getElementById('nav-stock'))">
        <div class="mc-icon" style="background:rgba(251,191,36,.1)"><svg width="22" height="22" fill="none" stroke="#fbbf24" stroke-width="1.7" viewBox="0 0 24 24"><path d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8"/><path d="M10 12h4"/></svg></div>
        <div><div class="mc-label">Inventario</div><div class="mc-name">Stock</div><div class="mc-desc">Accesorios, repuestos y movimientos</div></div>
        <svg class="mc-arrow" width="16" height="16" fill="none" stroke="var(--acc)" stroke-width="2.5" viewBox="0 0 24 24"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
      </div>
      <div class="mc" onclick="nav('facturacion',document.getElementById('nav-facturacion'))">
        <div class="mc-icon" style="background:var(--rdl)"><svg width="22" height="22" fill="none" stroke="var(--rd)" stroke-width="1.7" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg></div>
        <div><div class="mc-label">Finanzas</div><div class="mc-name">Facturación</div><div class="mc-desc">Totales de compras, ventas y sin facturar</div></div>
        <svg class="mc-arrow" width="16" height="16" fill="none" stroke="var(--acc)" stroke-width="2.5" viewBox="0 0 24 24"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
      </div>
    </div>
  </div>
</div>

<!-- VENTAS -->
<div id="page-ventas" class="page">
  <div class="topbar">
    <div style="display:flex;align-items:center"><div class="topbar-title">Vehículos Vendidos</div><span class="topbar-sub" id="v-total-sub"></span></div>
    <button class="btn pr" onclick="openOv('add-venta')">+ Nueva venta</button>
  </div>
  <div class="content">
    <div class="brand-bar" id="v-brand-bar"></div>
    <div class="tb">
      <div class="sw"><svg width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
        <input id="v-q" placeholder="Buscar cliente, modelo, chasis, motor..." oninput="vPg=1;loadVentas()">
      </div>
      <select class="fi" id="v-m" style="display:none" onchange="vPg=1;loadVentas()"></select>
      <select class="fi" id="v-a" onchange="vPg=1;loadVentas()"><option value="">Todos los años</option></select>
      <select class="fi" id="v-mn" onchange="vPg=1;loadVentas()"><option value="">USD + UYU</option><option>USD</option><option>UYU</option></select>
      <select class="fi" id="v-ps" onchange="vPg=1;loadVentas()"><option value="20">20/pág</option><option value="30">30/pág</option><option value="100">100/pág</option></select>
    </div>
    <div class="tc">
      <div class="tsc"><table><thead><tr>
        <th>Fecha</th><th>Cliente</th><th>Marca</th><th>Modelo</th><th>Año</th><th>Motor</th><th>Chasis</th><th>Precio</th><th>Nº</th><th></th>
      </tr></thead><tbody id="v-body"><tr><td colspan="10"><div class="loading"><div class="loading-spin"></div><br>Cargando...</div></td></tr></tbody></table></div>
      <div class="pag" id="v-pag"></div>
    </div>
  </div>
</div>

<!-- COMPRAS -->
<div id="page-compras" class="page">
  <div class="topbar">
    <div style="display:flex;align-items:center"><div class="topbar-title">Vehículos Comprados</div><span class="topbar-sub" id="c-total-sub"></span></div>
    <button class="btn pr" onclick="openOv('add-compra')">+ Nueva compra</button>
  </div>
  <div class="content">
    <div class="tb">
      <div class="sw"><svg width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
        <input id="c-q" placeholder="Buscar proveedor, modelo, chasis..." oninput="cPg=1;loadCompras()">
      </div>
      <select class="fi" id="c-m" onchange="cPg=1;loadCompras()"><option value="">Todas las marcas</option></select>
      <select class="fi" id="c-ps" onchange="cPg=1;loadCompras()"><option value="20">20/pág</option><option value="30">30/pág</option><option value="100">100/pág</option></select>
    </div>
    <div class="tc">
      <div class="tsc"><table><thead><tr>
        <th>Fecha</th><th>Proveedor</th><th>Marca</th><th>Modelo</th><th>Año</th><th>Motor</th><th>Chasis / VIN</th><th>Precio</th><th></th>
      </tr></thead><tbody id="c-body"></tbody></table></div>
      <div class="pag" id="c-pag"></div>
    </div>
  </div>
</div>

<!-- CLIENTES -->
<div id="page-clientes" class="page">
  <div class="topbar">
    <div style="display:flex;align-items:center"><div class="topbar-title">Clientes</div><span class="topbar-sub" id="cl-total-sub"></span></div>
    <button class="btn pr" onclick="openOv('add-cliente')">+ Agregar cliente</button>
  </div>
  <div class="content">
    <div class="tb">
      <div class="sw"><svg width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
        <input id="cl-q" placeholder="Buscar nombre, apellido o documento..." oninput="clPg=1;loadClientes()">
      </div>
      <select class="fi" id="cl-campo" onchange="clPg=1;loadClientes()"><option value="todos">Todos los campos</option><option value="nombre">Nombre / Apellido</option><option value="doc">Nº Documento</option></select>
      <select class="fi" id="cl-ps" onchange="clPg=1;loadClientes()"><option value="20">20/pág</option><option value="30">30/pág</option><option value="100">100/pág</option></select>
    </div>
    <div class="tc">
      <div class="tsc"><table><thead><tr>
        <th>Nombre</th><th>Documento</th><th>Ciudad</th><th>Teléfono</th><th>Mail</th><th>Dirección</th><th>Vehículos</th><th></th>
      </tr></thead><tbody id="cl-body"></tbody></table></div>
      <div class="pag" id="cl-pag"></div>
    </div>
  </div>
</div>

<!-- NEGOCIOS -->
<div id="page-negocios" class="page">
  <div class="topbar">
    <div style="display:flex;align-items:center"><div class="topbar-title">Negocios</div><span class="topbar-sub" id="neg-total-sub"></span></div>
    <button class="btn pr" onclick="openOv('add-negocio')">+ Nuevo negocio</button>
  </div>
  <div class="content">
    <div class="tb">
      <div class="sw"><svg width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
        <input id="neg-q" placeholder="Buscar cliente, modelo, chasis..." oninput="loadNegocios()">
      </div>
      <select class="fi" id="neg-estado" onchange="loadNegocios()"><option value="">Todos</option><option value="activo">Activos</option><option value="cerrado">Cerrados</option></select>
    </div>
    <div id="neg-list"></div>
  </div>
</div>

<!-- FACTURACIÓN -->
<div id="page-facturacion" class="page">
  <div class="topbar">
    <div style="display:flex;align-items:center"><div class="topbar-title">Facturación</div></div>
    <select class="fi" id="fac-mon" onchange="loadFac()"><option value="USD">USD</option><option value="UYU">UYU</option></select>
  </div>
  <div class="content">
    <div class="fac-grid" id="fac-totales"></div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:24px" id="fac-desglose"></div>
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">
      <div style="font-family:var(--fh);font-size:15px;font-weight:700">Vehículos sin facturar</div>
      <div id="fac-sf-cnt" style="background:var(--rdl);color:var(--rd);font-size:12px;font-family:var(--mo);font-weight:700;padding:3px 12px;border-radius:20px"></div>
    </div>
    <div class="tc">
      <div class="tsc"><table><thead><tr>
        <th>Fecha</th><th>Cliente</th><th>Marca</th><th>Modelo</th><th>Año</th><th>Chasis</th><th>Precio</th>
      </tr></thead><tbody id="fac-sf-body"></tbody></table></div>
    </div>
  </div>
</div>

<!-- STOCK -->
<div id="page-stock" class="page">
  <div class="topbar">
    <div style="display:flex;align-items:center"><div class="topbar-title">Stock</div><span class="topbar-sub" id="stk-total-sub"></span></div>
    <button class="btn pr" onclick="openOv('add-stock')">+ Agregar ítem</button>
  </div>
  <div class="content">
    <div class="tb">
      <div class="sw"><svg width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
        <input id="stk-q" placeholder="Buscar nombre, código, categoría..." oninput="loadStock()">
      </div>
      <select class="fi" id="stk-cat" onchange="loadStock()"><option value="">Todas las categorías</option><option>Accesorio</option><option>Repuesto</option><option>Lubricante</option><option>Neumático</option><option>Electrónico</option><option>Otro</option></select>
    </div>
    <div class="tc">
      <div class="tsc"><table><thead><tr>
        <th>Código</th><th>Nombre</th><th>Categoría</th><th>Compatible con</th><th>Stock</th><th>Precio venta</th><th>Ubicación</th><th></th>
      </tr></thead><tbody id="stk-body"></tbody></table></div>
    </div>
  </div>
</div>

</main>
</div><!-- /app -->

<!-- TOAST -->
<div class="toast" id="toast"></div>

<!-- ═══ MODALES ═══ -->

<!-- Add Venta -->
<div class="ov" id="ov-add-venta"><div class="mo-box">
  <div class="mh"><h2>Nueva venta</h2><button class="mc-close" onclick="closeOv('add-venta')">×</button></div>
  <div class="mb"><div class="fg">
    <div class="fi-g"><label>Marca</label><input id="av-marca" placeholder="BMW"></div>
    <div class="fi-g"><label>Modelo</label><input id="av-modelo" placeholder="X3 xDrive 30e M Sport"></div>
    <div class="fi-g"><label>Año</label><input id="av-anio" type="number" placeholder="2025"></div>
    <div class="fi-g"><label>Fecha</label><input id="av-fecha" type="date"></div>
    <div class="fi-g"><label>N° Motor</label><input id="av-motor" placeholder="B0427843"></div>
    <div class="fi-g"><label>N° Chasis</label><input id="av-chasis" placeholder="WBA65GP03TN357736"></div>
    <div class="fi-g full"><label>Cliente</label><input id="av-cliente" placeholder="Nombre completo del cliente"></div>
    <div class="fi-g"><label>Doc. cliente</label><input id="av-cliente-doc" placeholder="12345678"></div>
    <div class="fi-g"><label>Comprobante</label><input id="av-comp" placeholder="A 5200"></div>
    <div class="fi-g"><label>Precio</label><input id="av-precio" type="number" placeholder="85000"></div>
    <div class="fi-g"><label>Moneda</label><select id="av-moneda"><option>USD</option><option>UYU</option></select></div>
  </div></div>
  <div class="mf"><button class="btn" onclick="closeOv('add-venta')">Cancelar</button><button class="btn pr" onclick="saveVenta()">Guardar</button></div>
</div></div>

<!-- Add Compra -->
<div class="ov" id="ov-add-compra"><div class="mo-box">
  <div class="mh"><h2>Nueva compra</h2><button class="mc-close" onclick="closeOv('add-compra')">×</button></div>
  <div class="mb"><div class="fg">
    <div class="fi-g"><label>Marca</label><input id="ac-marca" placeholder="BMW"></div>
    <div class="fi-g"><label>Modelo</label><input id="ac-modelo" placeholder="X1 xDrive 25e"></div>
    <div class="fi-g"><label>Año</label><input id="ac-anio" type="number" placeholder="2025"></div>
    <div class="fi-g"><label>Fecha</label><input id="ac-fecha" type="date"></div>
    <div class="fi-g"><label>N° Motor</label><input id="ac-motor" placeholder="B48A20A"></div>
    <div class="fi-g"><label>N° Chasis / VIN</label><input id="ac-chasis" placeholder="WBA21EF0..."></div>
    <div class="fi-g full"><label>Proveedor</label><input id="ac-prov" placeholder="Nombre del proveedor"></div>
    <div class="fi-g"><label>Precio</label><input id="ac-precio" type="number" placeholder="60000"></div>
    <div class="fi-g"><label>Moneda</label><select id="ac-moneda"><option>USD</option><option>UYU</option></select></div>
    <div class="fi-g"><label>Color</label><input id="ac-color" placeholder="Negro"></div>
  </div></div>
  <div class="mf"><button class="btn" onclick="closeOv('add-compra')">Cancelar</button><button class="btn pr" onclick="saveCompra()">Guardar</button></div>
</div></div>

<!-- Add Cliente -->
<div class="ov" id="ov-add-cliente"><div class="mo-box">
  <div class="mh"><h2>Agregar cliente</h2><button class="mc-close" onclick="closeOv('add-cliente')">×</button></div>
  <div class="mb"><div class="fg">
    <div class="fi-g full"><label>Nombre completo</label><input id="acl-nombre" placeholder="Nombre completo"></div>
    <div class="fi-g"><label>Documento (CI / RUT)</label><input id="acl-doc" placeholder="12345678"></div>
    <div class="fi-g"><label>Teléfono</label><input id="acl-tel" placeholder="099 123 456"></div>
    <div class="fi-g full"><label>Dirección</label><input id="acl-dir" placeholder="Calle y número"></div>
    <div class="fi-g"><label>Ciudad</label><input id="acl-ciudad" placeholder="Punta del Este"></div>
    <div class="fi-g"><label>Mail</label><input id="acl-mail" placeholder="correo@ejemplo.com"></div>
    <div class="fi-g"><label>Relación</label><select id="acl-rel"><option>Cliente</option><option>Proveedor</option><option>Cliente/Proveedor</option></select></div>
  </div></div>
  <div class="mf"><button class="btn" onclick="closeOv('add-cliente')">Cancelar</button><button class="btn pr" onclick="saveCliente()">Guardar</button></div>
</div></div>

<!-- Add Negocio -->
<div class="ov" id="ov-add-negocio"><div class="mo-box wide">
  <div class="mh"><h2>Nuevo negocio</h2><button class="mc-close" onclick="closeOv('add-negocio')">×</button></div>
  <div class="mb"><div class="fg">
    <div class="fi-g full"><label>Cliente</label><input id="an-cliente" placeholder="Nombre del cliente"></div>
    <div class="fi-g"><label>Marca vehículo</label><input id="an-marca" placeholder="BMW"></div>
    <div class="fi-g"><label>Modelo</label><input id="an-modelo" placeholder="X3 xDrive 30e M Sport"></div>
    <div class="fi-g"><label>Año</label><input id="an-anio" type="number" placeholder="2025"></div>
    <div class="fi-g"><label>Chasis / VIN</label><input id="an-chasis" placeholder="WBA65GP..."></div>
    <div class="fi-g"><label>Precio venta</label><input id="an-precio" type="number" placeholder="85000"></div>
    <div class="fi-g"><label>Moneda</label><select id="an-moneda"><option>USD</option><option>UYU</option></select></div>
    <div class="fi-g"><label>Método de pago</label><select id="an-metodo">
      <option value="contado">Contado</option>
      <option value="financiado">Financiado</option>
      <option value="leasing">Leasing</option>
      <option value="permuta">Permuta</option>
      <option value="credito">Crédito bancario</option>
      <option value="cuotas">Cuotas directas</option>
    </select></div>
    <div class="fi-g"><label>Fecha negocio</label><input id="an-fecha" type="date"></div>
    <div class="fi-g"><label>N° Cuotas (0 = pago único)</label><input id="an-cuotas" type="number" value="0" min="0" oninput="toggleCuotas()"></div>
    <div id="cuotas-fields" style="display:none;grid-column:1/-1;display:none">
      <div class="fg">
        <div class="fi-g"><label>Monto por cuota</label><input id="an-monto-cuota" type="number" placeholder="2000"></div>
        <div class="fi-g"><label>Fecha 1ra cuota</label><input id="an-primera-cuota" type="date"></div>
      </div>
    </div>
    <div class="fi-g full"><label>Notas</label><textarea id="an-notas" placeholder="Observaciones del negocio..."></textarea></div>
  </div></div>
  <div class="mf"><button class="btn" onclick="closeOv('add-negocio')">Cancelar</button><button class="btn pr" onclick="saveNegocio()">Guardar</button></div>
</div></div>

<!-- Add Stock -->
<div class="ov" id="ov-add-stock"><div class="mo-box">
  <div class="mh"><h2>Agregar ítem al stock</h2><button class="mc-close" onclick="closeOv('add-stock')">×</button></div>
  <div class="mb"><div class="fg">
    <div class="fi-g"><label>Código</label><input id="as-codigo" placeholder="BMW-ACC-001"></div>
    <div class="fi-g"><label>Categoría</label><select id="as-cat"><option>Accesorio</option><option>Repuesto</option><option>Lubricante</option><option>Neumático</option><option>Electrónico</option><option>Otro</option></select></div>
    <div class="fi-g full"><label>Nombre</label><input id="as-nombre" placeholder="Nombre del producto"></div>
    <div class="fi-g"><label>Marca compatible</label><input id="as-marca" placeholder="BMW"></div>
    <div class="fi-g"><label>Modelo compatible</label><input id="as-modelo" placeholder="X3, X5, Serie 3..."></div>
    <div class="fi-g"><label>Cantidad inicial</label><input id="as-cant" type="number" value="0" min="0"></div>
    <div class="fi-g"><label>Precio costo</label><input id="as-costo" type="number" placeholder="0"></div>
    <div class="fi-g"><label>Precio venta</label><input id="as-venta" type="number" placeholder="0"></div>
    <div class="fi-g"><label>Moneda</label><select id="as-moneda"><option>USD</option><option>UYU</option></select></div>
    <div class="fi-g"><label>Ubicación</label><input id="as-ubic" placeholder="Estante A-3"></div>
    <div class="fi-g full"><label>Notas</label><input id="as-notas" placeholder="Observaciones..."></div>
  </div></div>
  <div class="mf"><button class="btn" onclick="closeOv('add-stock')">Cancelar</button><button class="btn pr" onclick="saveStock()">Guardar</button></div>
</div></div>

<!-- Detalle genérico -->
<div class="ov" id="ov-detail"><div class="mo-box">
  <div class="mh"><h2 id="det-t">Detalle</h2><button class="mc-close" onclick="closeOv('detail')">×</button></div>
  <div class="mb" id="det-b"></div>
  <div class="mf"><button class="btn pr" onclick="closeOv('detail')">Cerrar</button></div>
</div></div>

<!-- Detalle Negocio + Cuotas -->
<div class="ov" id="ov-det-neg"><div class="mo-box wide">
  <div class="mh"><h2 id="detneg-t">Negocio</h2><button class="mc-close" onclick="closeOv('det-neg')">×</button></div>
  <div class="mb" id="detneg-b"></div>
  <div class="mf">
    <button class="btn danger" id="btn-cerrar-neg" onclick="cerrarNegocio()">Marcar cerrado</button>
    <button class="btn pr" onclick="closeOv('det-neg')">Cerrar</button>
  </div>
</div></div>

<!-- Movimiento Stock -->
<div class="ov" id="ov-mov-stock"><div class="mo-box" style="width:380px">
  <div class="mh"><h2>Movimiento de stock</h2><button class="mc-close" onclick="closeOv('mov-stock')">×</button></div>
  <div class="mb"><div class="fg">
    <div class="fi-g full"><label>Producto</label><input id="ms-nombre" readonly style="background:var(--bg4);color:var(--tx3)"></div>
    <div class="fi-g"><label>Tipo</label><select id="ms-tipo"><option value="entrada">Entrada</option><option value="salida">Salida</option></select></div>
    <div class="fi-g"><label>Cantidad</label><input id="ms-cant" type="number" value="1" min="1"></div>
    <div class="fi-g full"><label>Motivo</label><input id="ms-motivo" placeholder="Ej: Venta a cliente, compra a proveedor..."></div>
  </div></div>
  <div class="mf"><button class="btn" onclick="closeOv('mov-stock')">Cancelar</button><button class="btn pr" onclick="saveMovStock()">Confirmar</button></div>
</div></div>

<!-- Sync eFactura -->
<div class="ov" id="ov-sync"><div class="mo-box" style="width:520px">
  <div class="mh"><h2>Actualizar desde eFactura</h2><button class="mc-close" onclick="closeOv('sync')">×</button></div>
  <div class="mb">
    <p style="font-size:13px;color:var(--tx2);margin-bottom:18px">Este proceso lee los datos actuales de eFactura y sincroniza ventas, compras y clientes con la base de datos local.</p>
    <div style="display:flex;gap:10px;margin-bottom:18px">
      <label style="display:flex;align-items:center;gap:6px;font-size:13px;cursor:pointer"><input type="checkbox" id="sync-ventas" checked> Ventas</label>
      <label style="display:flex;align-items:center;gap:6px;font-size:13px;cursor:pointer"><input type="checkbox" id="sync-compras" checked> Compras</label>
      <label style="display:flex;align-items:center;gap:6px;font-size:13px;cursor:pointer"><input type="checkbox" id="sync-clientes" checked> Clientes</label>
    </div>
    <div class="sync-progress" id="sync-prog-bar"><div class="sync-progress-fill" id="sync-prog-fill"></div></div>
    <div id="sync-status" style="font-size:12px;color:var(--tx3);margin-bottom:10px"></div>
    <div id="sync-log" style="max-height:200px;overflow-y:auto;background:var(--bg3);border-radius:8px;padding:10px;font-family:var(--mo);font-size:11.5px;display:none"></div>
  </div>
  <div class="mf">
    <button class="btn" onclick="closeOv('sync')">Cerrar</button>
    <button class="btn pr" id="sync-run-btn" onclick="runSync()">Iniciar sincronización</button>
  </div>
</div></div>

<script>
const API = 'http://localhost:8765';
let TOKEN = localStorage.getItem('bmw_token') || '';
let ME = JSON.parse(localStorage.getItem('bmw_me') || 'null');

// ── UTILS ──
function esc(s){return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;')}
function fmt(n,mon='USD'){if(!n&&n!==0)return '—';return(mon==='USD'?'U$S ':'$U ')+Number(n).toLocaleString('es-UY',{minimumFractionDigits:0,maximumFractionDigits:0})}
function fdate(d){return d?d.substring(0,10):'—'}

function toast(msg, type='ok'){
  const t=document.getElementById('toast');
  t.textContent=msg; t.className='toast '+type+' show';
  setTimeout(()=>t.classList.remove('show'),3000);
}

async function api(path, opts={}){
  const r = await fetch(API+path, {
    headers: {'Content-Type':'application/json', 'Authorization':'Bearer '+TOKEN, ...opts.headers},
    ...opts
  });
  const data = await r.json();
  if(r.status===401){doLogout();return null;}
  if(!r.ok) throw new Error(data.error||'Error');
  return data;
}

function openOv(id){document.getElementById('ov-'+id).classList.add('op')}
function closeOv(id){document.getElementById('ov-'+id).classList.remove('op')}
document.querySelectorAll('.ov').forEach(ov=>ov.addEventListener('click',e=>{if(e.target===ov)ov.classList.remove('op')}));

function initials(n){const w=(n||'').trim().split(/\s+/);return((w[0]?.[0]||'')+(w[1]?.[0]||'')).toUpperCase()}
function celTd(v,title=''){return`<td style="max-width:150px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="${esc(title||v)}">${esc(v)}</td>`}

const BRAND_COLORS={
  'BMW':['#1a2a4a','#6ba3ff'],'MINI':['#2a1a0a','#ffb86c'],'VOLVO':['#0a2a1a','#4ade80'],
  'MAZDA':['#2a0a0a','#ff6b6b'],'RANGE ROVER':['#1a0a2a','#c084fc'],'LAND ROVER':['#0a1a2a','#60a5fa'],
  'JAGUAR':['#002a20','#34d399'],'MERCEDES BENZ':['#0a1520','#93c5fd'],'AUDI':['#2a1500','#fbbf24'],
  'FERRARI':['#2a0000','#ff4444'],'PORSCHE':['#2a1000','#fb923c'],'VOLKSWAGEN':['#000a2a','#818cf8'],
};
function bb(m){if(!m)return'<span class="badge" style="background:var(--bg4);color:var(--tx3)">—</span>';const c=BRAND_COLORS[m]||['#1a1a1a','#888'];return`<span class="badge" style="background:${c[0]};color:${c[1]}">${esc(m)}</span>`}

function renderPag(prefix, page, totalPages, total, from, ps, loadFn){
  const el=document.getElementById(prefix+'-pag');
  if(!el)return;
  const to=Math.min(from+ps,total);
  if(totalPages<=1){el.innerHTML=`<span class="pi">${total} registros</span><div></div>`;return}
  let btns='';
  for(let i=1;i<=totalPages;i++){
    if(i===1||i===totalPages||(i>=page-2&&i<=page+2))btns+=`<button class="pb${i===page?' ac':''}" onclick="${loadFn}(${i})">${i}</button>`;
    else if(i===page-3||i===page+3)btns+=`<span style="padding:3px 4px;color:var(--tx3)">…</span>`;
  }
  el.innerHTML=`<span class="pi">${from+1}–${to} de ${total}</span><div class="pbs">${btns}</div>`;
}

// ── AUTH ──
async function doLogin(){
  const u=document.getElementById('l-user').value.trim();
  const p=document.getElementById('l-pass').value;
  document.getElementById('l-err').textContent='';
  try{
    const r=await fetch(API+'/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:u,password:p})});
    const data=await r.json();
    if(!r.ok){document.getElementById('l-err').textContent=data.error||'Error al iniciar sesión';return}
    TOKEN=data.token; ME=data;
    localStorage.setItem('bmw_token',TOKEN);
    localStorage.setItem('bmw_me',JSON.stringify(ME));
    showApp();
  }catch(e){document.getElementById('l-err').textContent='No se pudo conectar al servidor en localhost:8765'}
}

function doLogout(){
  TOKEN=''; ME=null;
  localStorage.removeItem('bmw_token');
  localStorage.removeItem('bmw_me');
  document.getElementById('app').style.display='none';
  document.getElementById('login-screen').style.display='flex';
}

async function showApp(){
  document.getElementById('login-screen').style.display='none';
  document.getElementById('app').style.display='block';
  // Actualizar sidebar usuario
  document.getElementById('sb-nombre').textContent=ME.nombre||ME.username;
  document.getElementById('sb-rol').textContent=ME.rol==='admin'?'Administrador':'Vendedor';
  document.getElementById('sb-av').textContent=initials(ME.nombre||ME.username);
  document.getElementById('menu-fecha-sub').textContent='Hoy: '+new Date().toLocaleDateString('es-UY',{day:'2-digit',month:'long',year:'numeric'});
  // Cargar stats
  try{
    const stats=await api('/api/stats');
    if(stats){
      document.getElementById('cnt-v').textContent=stats.ventas;
      document.getElementById('cnt-c').textContent=stats.compras;
      document.getElementById('cnt-cl').textContent=stats.clientes;
      document.getElementById('cnt-neg').textContent=stats.negocios_activos;
      document.getElementById('cnt-stk').textContent=stats.stock_items;
    }
  }catch(e){}
}

// Al cargar, si hay token válido, mostrar app
window.addEventListener('load',async()=>{
  if(TOKEN&&ME){
    try{const me=await api('/api/me');if(me)showApp();else doLogout();}catch(e){showApp();}
  }
});

// ── NAVEGACIÓN ──
function nav(page, btn){
  document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));
  document.querySelectorAll('.ni').forEach(b=>b.classList.remove('active'));
  document.getElementById('page-'+page).classList.add('active');
  if(btn)btn.classList.add('active');
  window.scrollTo(0,0);
  if(page==='ventas')loadVentas();
  else if(page==='compras')loadCompras();
  else if(page==='clientes')loadClientes();
  else if(page==='negocios')loadNegocios();
  else if(page==='facturacion')loadFac();
  else if(page==='stock')loadStock();
}

// ── VENTAS ──
let vPg=1, vBrandFilter='', vData=[], vBrandBuilt=false;

async function loadVentas(page){
  if(page)vPg=page;
  const PS=parseInt(document.getElementById('v-ps').value)||20;
  const q=document.getElementById('v-q').value;
  const marca=document.getElementById('v-m').value;
  const anio=document.getElementById('v-a').value;
  const moneda=document.getElementById('v-mn').value;

  const params=new URLSearchParams({limit:PS, offset:(vPg-1)*PS});
  if(q)params.set('q',q);
  if(marca)params.set('marca',marca);

  try{
    const res=await api('/api/ventas?'+params);
    if(!res)return;
    vData=res.data;
    document.getElementById('v-total-sub').textContent=`(${res.total} total)`;

    // Filtrar año/moneda client-side
    let data=res.data;
    if(anio)data=data.filter(v=>String(v.anio)===anio);
    if(moneda)data=data.filter(v=>v.moneda===moneda);

    // Años dropdown
    if(!anio){
      const years=[...new Set(vData.filter(v=>v.anio).map(v=>v.anio))].sort((a,b)=>b-a);
      const sa=document.getElementById('v-a'),cur=sa.value;
      sa.innerHTML='<option value="">Todos los años</option>'+years.map(y=>`<option${y==cur?' selected':''}>${y}</option>`).join('');
    }

    // Brand bar (solo primera vez)
    if(!vBrandBuilt){buildBrandBar(res.data);vBrandBuilt=true;}

    const tot=res.total, tp=Math.ceil(tot/PS)||1;
    document.getElementById('v-body').innerHTML=data.length?data.map((v,i)=>`<tr>
      <td style="white-space:nowrap;font-family:var(--mo);font-size:12px;color:var(--tx3)">${fdate(v.fecha)}</td>
      ${celTd(v.cliente||'—',v.cliente)}
      <td>${bb(v.marca)}</td>
      ${celTd(v.modelo||'—',v.modelo)}
      <td style="color:var(--tx3);font-family:var(--mo);font-size:12px">${v.anio||'—'}</td>
      <td class="mo" style="max-width:120px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="${esc(v.motor)}">${esc(v.motor||'—')}</td>
      <td class="mo" style="color:var(--acc2);max-width:150px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="${esc(v.chasis)}">${esc(v.chasis||'—')}</td>
      <td class="pr-val" style="white-space:nowrap">${fmt(v.precio,v.moneda)}</td>
      <td class="mo" style="white-space:nowrap;color:var(--tx3);font-size:11px">${v.comprobante||'—'}</td>
      <td><button class="btn sm" onclick="detVenta(${v.id})">Ver</button></td>
    </tr>`).join(''):`<tr><td colspan="10"><div class="empty"><div class="empty-icon">🔍</div>Sin resultados</div></td></tr>`;
    renderPag('v',vPg,tp,tot,(vPg-1)*PS,PS,'loadVentas');
  }catch(e){toast('Error cargando ventas','err')}
}

function buildBrandBar(){
  const bar=document.getElementById('v-brand-bar');
  if(!bar||vBrandBuilt)return;
  api('/api/stats').then(stats=>{
    if(!stats)return;
    const html=`<div class="bchip all active" onclick="setBrand('')">Todas <span class="bchip-cnt">${stats.ventas}</span></div>`+
      stats.marcas_ventas.map(({marca,cnt})=>{
        const c=BRAND_COLORS[marca]||['#1a1a1a','#888'];
        return`<div class="bchip" onclick="setBrand('${esc(marca)}')" id="bchip-${marca.replace(/\s+/g,'-')}" style="--bc:${c[0]};--bct:${c[1]}">
          <span style="color:${c[1]}">${esc(marca)}</span>
          <span class="bchip-cnt" style="color:${c[1]}">${cnt}</span>
        </div>`;
      }).join('');
    bar.innerHTML=html;
  });
}

function setBrand(marca){
  nav('ventas',document.getElementById('nav-ventas'));
  document.getElementById('v-m').value=marca;
  document.querySelectorAll('.bchip').forEach(c=>{c.classList.remove('active');c.style.background='';c.style.borderColor='';});
  if(!marca){document.querySelector('.bchip.all')?.classList.add('active');}
  else{const c=BRAND_COLORS[marca]||['#333','#aaa'],id='bchip-'+marca.replace(/\s+/g,'-'),el=document.getElementById(id);if(el){el.classList.add('active');el.style.background=c[0];el.style.borderColor=c[1];}}
  vPg=1;loadVentas();
}

async function detVenta(id){
  const v=vData.find(x=>x.id===id)||{};
  document.getElementById('det-t').textContent=(v.marca||'')+' '+(v.modelo||'');
  document.getElementById('det-b').innerHTML=[
    ['Comprobante',`<span class="mo">${esc(v.comprobante||'—')}</span>`],
    ['Fecha',fdate(v.fecha)],['Cliente',`<strong>${esc(v.cliente||'—')}</strong>`],
    ['Documento',`<span class="mo">${v.cliente_doc||'—'}</span>`],
    ['Marca',bb(v.marca)],['Modelo',esc(v.modelo||'—')],['Año',v.anio||'—'],
    ['N° Motor',`<span class="mo" style="color:var(--acc2)">${esc(v.motor||'—')}</span>`],
    ['N° Chasis',`<span class="mo" style="color:var(--acc2)">${esc(v.chasis||'—')}</span>`],
    ['Precio',`<span class="pr-val">${fmt(v.precio,v.moneda)}</span>`],
  ].map(([l,val])=>`<div class="dr"><span class="dl">${l}</span><span class="dv">${val}</span></div>`).join('');
  openOv('detail');
}

async function saveVenta(){
  const v={comprobante:document.getElementById('av-comp').value.trim(),fecha:document.getElementById('av-fecha').value,marca:document.getElementById('av-marca').value.trim().toUpperCase(),modelo:document.getElementById('av-modelo').value.trim().toUpperCase(),anio:parseInt(document.getElementById('av-anio').value)||null,motor:document.getElementById('av-motor').value.trim().toUpperCase(),chasis:document.getElementById('av-chasis').value.trim().toUpperCase(),cliente:document.getElementById('av-cliente').value.trim(),cliente_doc:document.getElementById('av-cliente-doc').value.trim(),precio:parseFloat(document.getElementById('av-precio').value)||0,moneda:document.getElementById('av-moneda').value};
  if(!v.marca||!v.cliente){toast('Marca y cliente son requeridos','err');return}
  try{await api('/api/ventas',{method:'POST',body:JSON.stringify(v)});closeOv('add-venta');toast('Venta guardada ✓');loadVentas();}catch(e){toast('Error: '+e.message,'err')}
}

// ── COMPRAS ──
let cPg=1, cData=[];
async function loadCompras(page){
  if(page)cPg=page;
  const PS=parseInt(document.getElementById('c-ps').value)||20;
  const q=document.getElementById('c-q').value;
  const marca=document.getElementById('c-m').value;
  const params=new URLSearchParams({limit:PS,offset:(cPg-1)*PS});
  if(q)params.set('q',q);if(marca)params.set('marca',marca);
  try{
    const res=await api('/api/compras?'+params);
    if(!res)return;
    cData=res.data;
    document.getElementById('c-total-sub').textContent=`(${res.total} total)`;
    // Marca options
    const sm=document.getElementById('c-m'),cur=sm.value;
    if(sm.options.length<=1){
      const ms=[...new Set(res.data.map(c=>c.marca).filter(Boolean))].sort();
      sm.innerHTML='<option value="">Todas las marcas</option>'+ms.map(m=>`<option${m===cur?' selected':''}>${m}</option>`).join('');
    }
    const tot=res.total,tp=Math.ceil(tot/PS)||1;
    document.getElementById('c-body').innerHTML=res.data.length?res.data.map(c=>`<tr>
      <td style="white-space:nowrap;font-family:var(--mo);font-size:12px;color:var(--tx3)">${fdate(c.fecha)}</td>
      ${celTd(c.proveedor||'—',c.proveedor)}
      <td>${bb(c.marca)}</td>
      ${celTd(c.modelo||c.detalle_original||'—',c.modelo||c.detalle_original||'')}
      <td style="color:var(--tx3);font-family:var(--mo);font-size:12px">${c.anio||'—'}</td>
      <td class="mo" style="max-width:110px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${esc(c.motor||'—')}</td>
      <td class="mo" style="color:var(--acc2);max-width:150px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="${esc(c.chasis)}">${esc(c.chasis||'—')}</td>
      <td class="pr-val" style="white-space:nowrap">${fmt(c.precio,c.moneda)}</td>
      <td><button class="btn sm" onclick="detCompra(${c.id})">Ver</button></td>
    </tr>`).join(''):`<tr><td colspan="9"><div class="empty"><div class="empty-icon">🔍</div>Sin resultados</div></td></tr>`;
    renderPag('c',cPg,tp,tot,(cPg-1)*PS,PS,'loadCompras');
  }catch(e){toast('Error cargando compras','err')}
}
async function detCompra(id){
  const c=cData.find(x=>x.id===id)||{};
  document.getElementById('det-t').textContent=(c.marca||'')+' '+(c.modelo||'');
  document.getElementById('det-b').innerHTML=[
    ['Fecha',fdate(c.fecha)],['Proveedor',`<strong>${esc(c.proveedor||'—')}</strong>`],
    ['Marca',bb(c.marca)],['Modelo',esc(c.modelo||'—')],['Año',c.anio||'—'],
    ['N° Motor',`<span class="mo" style="color:var(--acc2)">${esc(c.motor||'—')}</span>`],
    ['N° Chasis',`<span class="mo" style="color:var(--acc2)">${esc(c.chasis||'—')}</span>`],
    ['Color',c.color||'—'],['Precio',`<span class="pr-val">${fmt(c.precio,c.moneda)}</span>`],
  ].map(([l,v])=>`<div class="dr"><span class="dl">${l}</span><span class="dv">${v}</span></div>`).join('');
  openOv('detail');
}
async function saveCompra(){
  const v={fecha:document.getElementById('ac-fecha').value,marca:document.getElementById('ac-marca').value.trim().toUpperCase(),modelo:document.getElementById('ac-modelo').value.trim().toUpperCase(),anio:parseInt(document.getElementById('ac-anio').value)||null,motor:document.getElementById('ac-motor').value.trim().toUpperCase(),chasis:document.getElementById('ac-chasis').value.trim().toUpperCase(),proveedor:document.getElementById('ac-prov').value.trim(),precio:parseFloat(document.getElementById('ac-precio').value)||0,moneda:document.getElementById('ac-moneda').value,color:document.getElementById('ac-color').value.trim()};
  if(!v.marca||!v.proveedor){toast('Marca y proveedor son requeridos','err');return}
  try{await api('/api/compras',{method:'POST',body:JSON.stringify(v)});closeOv('add-compra');toast('Compra guardada ✓');loadCompras();}catch(e){toast('Error: '+e.message,'err')}
}

// ── CLIENTES ──
let clPg=1, clData=[];
async function loadClientes(page){
  if(page)clPg=page;
  const PS=parseInt(document.getElementById('cl-ps').value)||20;
  const q=document.getElementById('cl-q').value;
  const campo=document.getElementById('cl-campo').value;
  const params=new URLSearchParams({limit:PS,offset:(clPg-1)*PS});
  if(q){params.set('q',q);params.set('campo',campo);}
  try{
    const res=await api('/api/clientes?'+params);
    if(!res)return;
    clData=res.data;
    document.getElementById('cl-total-sub').textContent=`(${res.total} total)`;
    const tot=res.total,tp=Math.ceil(tot/PS)||1;
    document.getElementById('cl-body').innerHTML=res.data.length?res.data.map(cl=>{
      const nv=cl.compras?.length||0;
      return`<tr>
        <td style="font-weight:600;white-space:nowrap">${esc(cl.nombre||'—')}</td>
        <td><span style="background:var(--accl);color:var(--acc);padding:2px 9px;border-radius:20px;font-family:var(--mo);font-size:11px">${esc(cl.doc||'—')}</span></td>
        ${celTd(cl.ciudad||'—',cl.ciudad)}
        <td style="white-space:nowrap">${cl.telefono?`<a href="tel:${cl.telefono}" style="color:var(--gn);font-family:var(--mo);font-size:12px;text-decoration:none">${esc(cl.telefono)}</a>`:'<span style="color:var(--tx3)">—</span>'}</td>
        ${celTd(cl.mail||'—',cl.mail)}
        ${celTd(cl.direccion||'—',cl.direccion)}
        <td>${nv>0?`<span class="badge" style="background:var(--gnl);color:var(--gn)">${nv} veh.</span>`:'<span style="color:var(--tx3)">—</span>'}</td>
        <td><button class="btn sm" onclick="detCliente(${cl.id})">Ver</button></td>
      </tr>`;
    }).join(''):`<tr><td colspan="8"><div class="empty"><div class="empty-icon">👥</div>Sin resultados</div></td></tr>`;
    renderPag('cl',clPg,tp,tot,(clPg-1)*PS,PS,'loadClientes');
  }catch(e){toast('Error cargando clientes','err')}
}
async function detCliente(id){
  const cl=clData.find(x=>x.id===id)||{};
  const ini=initials(cl.nombre);
  const vehs=cl.compras||[];
  document.getElementById('det-t').textContent=cl.nombre||'Cliente';
  document.getElementById('det-b').innerHTML=`
    <div style="display:flex;align-items:center;gap:14px;margin-bottom:18px">
      <div style="width:44px;height:44px;border-radius:50%;background:var(--accl);display:flex;align-items:center;justify-content:center;font-family:var(--fh);font-size:17px;font-weight:800;color:var(--acc);flex-shrink:0">${ini}</div>
      <div><div style="font-family:var(--fh);font-size:17px;font-weight:700">${esc(cl.nombre||'—')}</div><div style="font-size:12px;color:var(--tx3)">${cl.relacion||'Cliente'}${cl.ciudad?' · '+esc(cl.ciudad):''}</div></div>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:0">
      <div class="dr"><span class="dl">Documento</span><span class="dv mo">${cl.doc||'—'}</span></div>
      <div class="dr"><span class="dl">Teléfono</span><span class="dv">${cl.telefono?`<a href="tel:${cl.telefono}" style="color:var(--gn);text-decoration:none">${esc(cl.telefono)}</a>`:'—'}</span></div>
      <div class="dr"><span class="dl">Ciudad</span><span class="dv">${esc(cl.ciudad||'—')}</span></div>
      <div class="dr"><span class="dl">Mail</span><span class="dv">${cl.mail?`<a href="mailto:${cl.mail}" style="color:var(--bl);text-decoration:none">${esc(cl.mail)}</a>`:'—'}</span></div>
      <div class="dr" style="grid-column:1/-1"><span class="dl">Dirección</span><span class="dv">${esc(cl.direccion||'—')}</span></div>
    </div>
    ${vehs.length?`<div style="margin-top:16px"><div style="font-family:var(--fh);font-size:12px;font-weight:700;color:var(--tx3);text-transform:uppercase;letter-spacing:1px;margin-bottom:10px">Vehículos (${vehs.length})</div>
    <table style="width:100%;font-size:12px;border-collapse:collapse"><thead><tr>${['Fecha','Marca','Modelo','Chasis','Precio'].map(h=>`<th style="padding:5px 8px;font-size:10px;color:var(--tx3);border-bottom:1px solid var(--bd);text-align:left">${h}</th>`).join('')}</tr></thead><tbody>
    ${vehs.map(v=>`<tr>
      <td style="padding:6px 8px;font-family:var(--mo);font-size:11px;color:var(--tx3);border-bottom:1px solid var(--bd)">${fdate(v.fecha)}</td>
      <td style="padding:6px 8px;border-bottom:1px solid var(--bd)">${bb(v.marca)}</td>
      <td style="padding:6px 8px;max-width:130px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;border-bottom:1px solid var(--bd)">${esc(v.modelo||'—')}</td>
      <td style="padding:6px 8px;font-family:var(--mo);font-size:11px;color:var(--acc2);border-bottom:1px solid var(--bd)">${esc(v.chasis||'—')}</td>
      <td style="padding:6px 8px;font-family:var(--mo);font-size:12px;color:var(--acc2);border-bottom:1px solid var(--bd)">${fmt(v.precio,v.moneda)}</td>
    </tr>`).join('')}</tbody></table></div>`:''}`;
  openOv('detail');
}
async function saveCliente(){
  const v={nombre:document.getElementById('acl-nombre').value.trim().toUpperCase(),doc:document.getElementById('acl-doc').value.trim(),telefono:document.getElementById('acl-tel').value.trim(),direccion:document.getElementById('acl-dir').value.trim(),ciudad:document.getElementById('acl-ciudad').value.trim().toUpperCase(),mail:document.getElementById('acl-mail').value.trim(),relacion:document.getElementById('acl-rel').value};
  if(!v.nombre){toast('El nombre es requerido','err');return}
  try{await api('/api/clientes',{method:'POST',body:JSON.stringify(v)});closeOv('add-cliente');toast('Cliente guardado ✓');loadClientes();}catch(e){toast('Error: '+e.message,'err')}
}

// ── NEGOCIOS ──
let negData=[], negDetId=null;
async function loadNegocios(){
  const q=document.getElementById('neg-q').value;
  const estado=document.getElementById('neg-estado').value;
  const params=new URLSearchParams({limit:200});
  if(q)params.set('q',q);if(estado)params.set('estado',estado);
  try{
    const res=await api('/api/negocios?'+params);
    if(!res)return;
    negData=res.data;
    document.getElementById('neg-total-sub').textContent=`(${res.total} total)`;
    document.getElementById('neg-list').innerHTML=res.data.length?res.data.map(n=>{
      const pend=n.cuotas_pendientes||0, tot=n.cuotas_total||0;
      const pct=tot?Math.round((tot-pend)/tot*100):100;
      const metodoLabel={'contado':'Contado','financiado':'Financiado','leasing':'Leasing','permuta':'Permuta','credito':'Crédito bancario','cuotas':'Cuotas directas'}[n.metodo_pago]||n.metodo_pago||'—';
      return`<div class="neg-card" onclick="detNegocio(${n.id})">
        <div class="neg-card-header">
          <div>
            <div class="neg-cliente">${esc(n.cliente_nombre||'—')}</div>
            <div class="neg-vehiculo">${esc([n.vehiculo_marca,n.vehiculo_modelo,n.vehiculo_anio].filter(Boolean).join(' '))}</div>
          </div>
          <div style="text-align:right">
            <div class="pr-val">${fmt(n.precio_venta,n.moneda)}</div>
            <div style="font-size:11px;color:var(--tx3);margin-top:2px">${metodoLabel}</div>
          </div>
        </div>
        <div class="neg-metas">
          <span class="neg-meta">📅 ${fdate(n.fecha_negocio)}</span>
          ${n.vehiculo_chasis?`<span class="neg-meta mo" style="font-size:11px">${esc(n.vehiculo_chasis)}</span>`:''}
          <span class="badge" style="background:${n.estado==='activo'?'var(--gnl)':'var(--bg4)'};color:${n.estado==='activo'?'var(--gn)':'var(--tx3)'}">${n.estado}</span>
          ${n.usuario_nombre?`<span class="neg-meta">👤 ${esc(n.usuario_nombre)}</span>`:''}
        </div>
        ${tot>0?`<div class="neg-cuotas-bar">
          <div class="neg-cuotas-label"><span>Cuotas</span><span>${tot-pend}/${tot} pagadas</span></div>
          <div class="neg-cuotas-track"><div class="neg-cuotas-fill" style="width:${pct}%"></div></div>
        </div>`:''}
      </div>`;
    }).join(''):`<div class="empty"><div class="empty-icon">📦</div>Sin negocios registrados</div>`;
  }catch(e){toast('Error cargando negocios','err')}
}

async function detNegocio(id){
  negDetId=id;
  const n=negData.find(x=>x.id===id)||{};
  document.getElementById('detneg-t').textContent=(n.vehiculo_marca||'')+' '+(n.vehiculo_modelo||'');
  // Cargar cuotas
  const cuotas=await api('/api/negocios/'+id+'/cuotas');
  const hoy=new Date().toISOString().slice(0,10);
  let cuotasHtml='';
  if(cuotas&&cuotas.length){
    cuotasHtml=`<div style="margin-top:18px"><div style="font-family:var(--fh);font-size:12px;font-weight:700;color:var(--tx3);text-transform:uppercase;letter-spacing:1px;margin-bottom:12px">Cuotas (${cuotas.length})</div>
    ${cuotas.map(c=>`<div class="cuota-row">
      <span class="cuota-num">#${c.numero}</span>
      <span class="cuota-fecha">${fdate(c.fecha_vencimiento)}</span>
      <span class="cuota-monto">${fmt(c.monto,c.moneda)}</span>
      ${c.pagada?`<span class="cuota-pagada">✓ Pagada</span>`:
        c.fecha_vencimiento<hoy?`<span class="cuota-vencida">⚠ Vencida</span><button class="btn sm" onclick="pagarCuota(${c.id},event)">Pagar</button>`:
        `<button class="btn sm" onclick="pagarCuota(${c.id},event)">Pagar</button>`}
    </div>`).join('')}</div>`;
  }
  document.getElementById('detneg-b').innerHTML=[
    ['Cliente',`<strong>${esc(n.cliente_nombre||'—')}</strong>`],
    ['Vehículo',esc([n.vehiculo_marca,n.vehiculo_modelo,n.vehiculo_anio].filter(Boolean).join(' '))],
    ['Chasis',`<span class="mo" style="color:var(--acc2)">${esc(n.vehiculo_chasis||'—')}</span>`],
    ['Precio',`<span class="pr-val">${fmt(n.precio_venta,n.moneda)}</span>`],
    ['Método',n.metodo_pago||'—'],['Fecha',fdate(n.fecha_negocio)],
    ['Estado',`<span class="badge" style="background:${n.estado==='activo'?'var(--gnl)':'var(--bg4)'};color:${n.estado==='activo'?'var(--gn)':'var(--tx3)'}">${n.estado}</span>`],
    ['Notas',n.notas||'—'],
  ].map(([l,v])=>`<div class="dr"><span class="dl">${l}</span><span class="dv">${v}</span></div>`).join('')+cuotasHtml;
  document.getElementById('btn-cerrar-neg').style.display=n.estado==='activo'?'':'none';
  openOv('det-neg');
}

async function pagarCuota(cid,e){
  e.stopPropagation();
  try{await api('/api/cuotas/pagar',{method:'POST',body:JSON.stringify({cuota_id:cid})});toast('Cuota marcada como pagada ✓');detNegocio(negDetId);}catch(e){toast('Error','err')}
}

async function cerrarNegocio(){
  if(!negDetId)return;
  try{await api('/api/negocios/'+negDetId,{method:'PUT',body:JSON.stringify({estado:'cerrado'})});toast('Negocio cerrado');closeOv('det-neg');loadNegocios();}catch(e){toast('Error','err')}
}

function toggleCuotas(){
  const n=parseInt(document.getElementById('an-cuotas').value)||0;
  document.getElementById('cuotas-fields').style.display=n>0?'block':'none';
}

async function saveNegocio(){
  const v={
    cliente_nombre:document.getElementById('an-cliente').value.trim(),
    vehiculo_marca:document.getElementById('an-marca').value.trim().toUpperCase(),
    vehiculo_modelo:document.getElementById('an-modelo').value.trim().toUpperCase(),
    vehiculo_anio:parseInt(document.getElementById('an-anio').value)||null,
    vehiculo_chasis:document.getElementById('an-chasis').value.trim().toUpperCase(),
    precio_venta:parseFloat(document.getElementById('an-precio').value)||0,
    moneda:document.getElementById('an-moneda').value,
    metodo_pago:document.getElementById('an-metodo').value,
    fecha_negocio:document.getElementById('an-fecha').value||new Date().toISOString().slice(0,10),
    cuotas:parseInt(document.getElementById('an-cuotas').value)||0,
    monto_cuota:parseFloat(document.getElementById('an-monto-cuota').value)||0,
    fecha_primera_cuota:document.getElementById('an-primera-cuota').value,
    notas:document.getElementById('an-notas').value.trim(),
  };
  if(!v.cliente_nombre){toast('El cliente es requerido','err');return}
  try{await api('/api/negocios',{method:'POST',body:JSON.stringify(v)});closeOv('add-negocio');toast('Negocio guardado ✓');loadNegocios();}catch(e){toast('Error: '+e.message,'err')}
}

// ── FACTURACIÓN ──
async function loadFac(){
  const mon=document.getElementById('fac-mon').value;
  try{
    const [vs,cs]=await Promise.all([api('/api/ventas?limit=5000'),api('/api/compras?limit=5000')]);
    if(!vs||!cs)return;
    const ventas=vs.data.filter(v=>v.moneda===mon);
    const compras=cs.data.filter(c=>c.moneda===mon);
    const tV=ventas.reduce((a,b)=>a+b.precio,0);
    const tC=compras.reduce((a,b)=>a+b.precio,0);
    const saldo=tV-tC;
    document.getElementById('fac-totales').innerHTML=`
      <div class="fac-card v"><div class="fc-label">Total Ventas</div><div class="fc-val" style="color:var(--bl)">${fmt(tV,mon)}</div><div class="fc-sub">${ventas.length} vehículos · ${mon}</div></div>
      <div class="fac-card c"><div class="fc-label">Total Compras</div><div class="fc-val" style="color:var(--acc2)">${fmt(tC,mon)}</div><div class="fc-sub">${compras.length} vehículos · ${mon}</div></div>
      <div class="fac-card s"><div class="fc-label">Diferencia</div><div class="fc-val" style="color:${saldo>=0?'var(--gn)':'var(--rd)'}">${fmt(Math.abs(saldo),mon)}</div><div class="fc-sub">${saldo>=0?'Resultado positivo':'Resultado negativo'}</div></div>`;
    // Desglose por marca
    const mv={},mc={};
    ventas.forEach(v=>{if(v.marca)mv[v.marca]=(mv[v.marca]||0)+v.precio});
    compras.forEach(c=>{if(c.marca)mc[c.marca]=(mc[c.marca]||0)+c.precio});
    const mkV=Object.entries(mv).sort((a,b)=>b[1]-a[1]);
    const mkC=Object.entries(mc).sort((a,b)=>b[1]-a[1]);
    document.getElementById('fac-desglose').innerHTML=`
      <div style="background:var(--bg2);border:1px solid var(--bd);border-radius:var(--rl);padding:18px 20px">
        <div style="font-family:var(--fh);font-size:11px;font-weight:700;color:var(--tx3);text-transform:uppercase;letter-spacing:1px;margin-bottom:14px">Ventas por marca · ${mon}</div>
        ${mkV.map(([m,v])=>`<div style="display:flex;justify-content:space-between;align-items:center;padding:7px 0;border-bottom:1px solid var(--bd);font-size:13px"><span style="color:var(--tx2)">${esc(m)}</span><span style="font-family:var(--mo);font-weight:600;color:var(--bl)">${fmt(v,mon)}</span></div>`).join('')}
      </div>
      <div style="background:var(--bg2);border:1px solid var(--bd);border-radius:var(--rl);padding:18px 20px">
        <div style="font-family:var(--fh);font-size:11px;font-weight:700;color:var(--tx3);text-transform:uppercase;letter-spacing:1px;margin-bottom:14px">Compras por marca · ${mon}</div>
        ${mkC.map(([m,v])=>`<div style="display:flex;justify-content:space-between;align-items:center;padding:7px 0;border-bottom:1px solid var(--bd);font-size:13px"><span style="color:var(--tx2)">${esc(m)}</span><span style="font-family:var(--mo);font-weight:600;color:var(--acc2)">${fmt(v,mon)}</span></div>`).join('')}
      </div>`;
    // Sin facturar
    const sf=vs.data.filter(v=>!v.comprobante||v.comprobante.trim()==='');
    document.getElementById('fac-sf-cnt').textContent=sf.length+' sin facturar';
    document.getElementById('fac-sf-body').innerHTML=sf.length?sf.map(v=>`<tr>
      <td style="white-space:nowrap;font-family:var(--mo);font-size:12px;color:var(--tx3)">${fdate(v.fecha)}</td>
      ${celTd(v.cliente||'—',v.cliente)}<td>${bb(v.marca)}</td>${celTd(v.modelo||'—',v.modelo)}
      <td style="font-family:var(--mo);font-size:12px;color:var(--tx3)">${v.anio||'—'}</td>
      <td class="mo" style="color:var(--acc2)">${esc(v.chasis||'—')}</td>
      <td class="pr-val">${fmt(v.precio,v.moneda)}</td>
    </tr>`).join(''):`<tr><td colspan="7"><div class="empty"><div class="empty-icon">✅</div>Sin vehículos pendientes</div></td></tr>`;
  }catch(e){toast('Error cargando facturación','err')}
}

// ── STOCK ──
let stkData=[], stkMovId=null;
async function loadStock(){
  const q=document.getElementById('stk-q').value;
  const cat=document.getElementById('stk-cat').value;
  const params=new URLSearchParams();
  if(q)params.set('q',q);if(cat)params.set('categoria',cat);
  try{
    const res=await api('/api/stock?'+params);
    if(!res)return;
    stkData=res.data;
    document.getElementById('stk-total-sub').textContent=`(${res.total} total)`;
    document.getElementById('stk-body').innerHTML=res.data.length?res.data.map(s=>{
      const bajo=s.cantidad<=3;
      return`<tr>
        <td class="mo" style="font-size:11px;color:var(--tx3)">${esc(s.codigo||'—')}</td>
        ${celTd(s.nombre,'')}<td><span class="badge" style="background:var(--bg4);color:var(--tx2)">${esc(s.categoria||'—')}</span></td>
        ${celTd([s.marca_compatible,s.modelo_compatible].filter(Boolean).join(' · '),'')}
        <td><span style="font-family:var(--mo);font-size:13px;font-weight:700;color:${bajo?'var(--rd)':'var(--gn)'}">${s.cantidad}</span></td>
        <td class="pr-val">${fmt(s.precio_venta,s.moneda)}</td>
        ${celTd(s.ubicacion||'—','')}
        <td style="white-space:nowrap"><button class="btn sm" onclick="openMovStock(${s.id})">±</button></td>
      </tr>`;
    }).join(''):`<tr><td colspan="8"><div class="empty"><div class="empty-icon">📦</div>Sin ítems en stock</div></td></tr>`;
  }catch(e){toast('Error cargando stock','err')}
}
function openMovStock(id){
  stkMovId=id;
  const s=stkData.find(x=>x.id===id)||{};
  document.getElementById('ms-nombre').value=s.nombre||'';
  document.getElementById('ms-cant').value=1;
  openOv('mov-stock');
}
async function saveMovStock(){
  const v={stock_id:stkMovId,tipo:document.getElementById('ms-tipo').value,cantidad:parseInt(document.getElementById('ms-cant').value)||1,motivo:document.getElementById('ms-motivo').value.trim()};
  try{await api('/api/stock/movimiento',{method:'POST',body:JSON.stringify(v)});closeOv('mov-stock');toast('Movimiento registrado ✓');loadStock();}catch(e){toast('Error','err')}
}
async function saveStock(){
  const v={codigo:document.getElementById('as-codigo').value.trim(),nombre:document.getElementById('as-nombre').value.trim(),categoria:document.getElementById('as-cat').value,marca_compatible:document.getElementById('as-marca').value.trim(),modelo_compatible:document.getElementById('as-modelo').value.trim(),cantidad:parseInt(document.getElementById('as-cant').value)||0,precio_costo:parseFloat(document.getElementById('as-costo').value)||0,precio_venta:parseFloat(document.getElementById('as-venta').value)||0,moneda:document.getElementById('as-moneda').value,ubicacion:document.getElementById('as-ubic').value.trim(),notas:document.getElementById('as-notas').value.trim()};
  if(!v.nombre){toast('El nombre es requerido','err');return}
  try{await api('/api/stock',{method:'POST',body:JSON.stringify(v)});closeOv('add-stock');toast('Ítem guardado ✓');loadStock();}catch(e){toast('Error: '+e.message,'err')}
}

// ── SYNC eFactura ──
function openSync(){
  document.getElementById('sync-log').style.display='none';
  document.getElementById('sync-log').innerHTML='';
  document.getElementById('sync-status').textContent='Listo para sincronizar';
  document.getElementById('sync-prog-fill').style.width='0%';
  document.getElementById('sync-run-btn').disabled=false;
  document.getElementById('sync-run-btn').textContent='Iniciar sincronización';
  openOv('sync');
}

function syncLog(msg, type=''){
  const el=document.getElementById('sync-log');
  el.style.display='block';
  el.innerHTML+=`<div class="sync-log-line ${type}">${esc(msg)}</div>`;
  el.scrollTop=el.scrollHeight;
}

async function runSync(){
  const btn=document.getElementById('sync-run-btn');
  btn.disabled=true;btn.textContent='Sincronizando...';
  const doVentas=document.getElementById('sync-ventas').checked;
  const doCompras=document.getElementById('sync-compras').checked;
  const doClientes=document.getElementById('sync-clientes').checked;

  document.getElementById('sync-log').innerHTML='';
  document.getElementById('sync-log').style.display='block';
  syncLog('Iniciando sincronización...');

  // Verificar si eFactura está abierto en el browser
  try{
    // Intentar leer datos de los JSONs locales (rebuild)
    document.getElementById('sync-status').textContent='Leyendo datos actuales...';
    document.getElementById('sync-prog-fill').style.width='20%';

    // Si tiene acceso a los JSONs locales, reimportar
    // En este contexto el servidor puede leer los JSONs directamente
    const payload={};
    let steps=0, total=(doVentas?1:0)+(doCompras?1:0)+(doClientes?1:0);

    if(doVentas){
      syncLog('📊 Leyendo ventas_full.json...');
      document.getElementById('sync-prog-fill').style.width=Math.round(20+steps/total*60)+'%';
      payload.tipo='ventas';
      steps++;
    }
    if(doCompras){
      syncLog('🚗 Leyendo compras_full.json...');
      document.getElementById('sync-prog-fill').style.width=Math.round(20+steps/total*60)+'%';
      payload.tipo='compras';
      steps++;
    }
    if(doClientes){
      syncLog('👥 Leyendo clientes_full.json...');
      document.getElementById('sync-prog-fill').style.width=Math.round(20+steps/total*60)+'%';
      payload.tipo='clientes';
      steps++;
    }

    // Llamar al endpoint de reimport
    payload.tipo='all';
    const res=await api('/api/sync/reimport',{method:'POST',body:JSON.stringify({ventas:doVentas,compras:doCompras,clientes:doClientes})});

    document.getElementById('sync-prog-fill').style.width='100%';
    if(res){
      syncLog(`✓ Ventas: ${res.ventas_nuevas||0} nuevas (${res.ventas_total||0} total)`,'ok');
      syncLog(`✓ Compras: ${res.compras_nuevas||0} nuevas (${res.compras_total||0} total)`,'ok');
      syncLog(`✓ Clientes: ${res.clientes_nuevas||0} nuevos (${res.clientes_total||0} total)`,'ok');
      syncLog('✓ Sincronización completada','ok');
      document.getElementById('sync-status').textContent='Completado';
      toast('Sincronización completada ✓');
      // Actualizar stats
      showApp();
    }
    btn.textContent='Completado';
  }catch(e){
    syncLog('✗ Error: '+e.message,'err');
    document.getElementById('sync-status').textContent='Error en sincronización';
    btn.disabled=false;btn.textContent='Reintentar';
    toast('Error en sincronización','err');
  }
}

</script>
</body>
</html>
"""


# ── CONFIG ──────────────────────────────────────────────
PORT = int(os.environ.get('PORT', 8765))
DB_PATH = os.path.join(os.path.dirname(__file__), 'db', 'bmw.db')
SECRET_KEY = 'bmw_punta_del_este_2026_secret_key_mofidec'
TOKEN_EXPIRY_HOURS = 12

# ── JWT SIMPLE (sin dependencias) ───────────────────────
def b64url_encode(data):
    if isinstance(data, str):
        data = data.encode()
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode()

def b64url_decode(s):
    padding = 4 - len(s) % 4
    if padding != 4:
        s += '=' * padding
    return base64.urlsafe_b64decode(s)

def create_token(payload):
    header = b64url_encode(json.dumps({'alg':'HS256','typ':'JWT'}))
    payload['exp'] = (datetime.datetime.utcnow() + datetime.timedelta(hours=TOKEN_EXPIRY_HOURS)).timestamp()
    body = b64url_encode(json.dumps(payload))
    sig_input = f"{header}.{body}".encode()
    sig = hmac.new(SECRET_KEY.encode(), sig_input, hashlib.sha256).digest()
    return f"{header}.{body}.{b64url_encode(sig)}"

def verify_token(token):
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        header, body, sig = parts
        sig_input = f"{header}.{body}".encode()
        expected = hmac.new(SECRET_KEY.encode(), sig_input, hashlib.sha256).digest()
        if not hmac.compare_digest(b64url_decode(sig), expected):
            return None
        payload = json.loads(b64url_decode(body))
        if payload.get('exp', 0) < time.time():
            return None
        return payload
    except:
        return None

def hash_password(pw):
    salt = secrets.token_hex(16)
    h = hashlib.sha256((salt + pw).encode()).hexdigest()
    return f"{salt}:{h}"

def check_password(pw, stored):
    try:
        salt, h = stored.split(':')
        return hmac.compare_digest(hashlib.sha256((salt + pw).encode()).hexdigest(), h)
    except:
        return False

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
        rol TEXT DEFAULT 'vendedor',
        activo INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    # Ventas
    c.execute('''CREATE TABLE IF NOT EXISTS ventas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        comprobante TEXT,
        fecha TEXT,
        marca TEXT,
        modelo TEXT,
        anio INTEGER,
        motor TEXT,
        chasis TEXT,
        cliente TEXT,
        cliente_doc TEXT,
        precio REAL,
        moneda TEXT DEFAULT 'USD',
        usuario_id INTEGER,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    # Compras
    c.execute('''CREATE TABLE IF NOT EXISTS compras (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT,
        marca TEXT,
        modelo TEXT,
        anio INTEGER,
        motor TEXT,
        chasis TEXT,
        proveedor TEXT,
        precio REAL,
        moneda TEXT DEFAULT 'USD',
        color TEXT,
        detalle_original TEXT,
        usuario_id INTEGER,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    # Clientes
    c.execute('''CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        doc TEXT,
        telefono TEXT,
        direccion TEXT,
        ciudad TEXT,
        mail TEXT,
        relacion TEXT DEFAULT 'Cliente',
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    # Negocios
    c.execute('''CREATE TABLE IF NOT EXISTS negocios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER,
        cliente_nombre TEXT,
        vehiculo_marca TEXT,
        vehiculo_modelo TEXT,
        vehiculo_anio INTEGER,
        vehiculo_chasis TEXT,
        precio_venta REAL,
        moneda TEXT DEFAULT 'USD',
        metodo_pago TEXT,
        cuotas INTEGER DEFAULT 0,
        monto_cuota REAL,
        fecha_primera_cuota TEXT,
        fecha_negocio TEXT,
        estado TEXT DEFAULT 'activo',
        notas TEXT,
        usuario_id INTEGER,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    # Cuotas
    c.execute('''CREATE TABLE IF NOT EXISTS cuotas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        negocio_id INTEGER,
        numero INTEGER,
        fecha_vencimiento TEXT,
        monto REAL,
        moneda TEXT DEFAULT 'USD',
        pagada INTEGER DEFAULT 0,
        fecha_pago TEXT,
        FOREIGN KEY(negocio_id) REFERENCES negocios(id)
    )''')

    # Stock accesorios/repuestos
    c.execute('''CREATE TABLE IF NOT EXISTS stock (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT,
        nombre TEXT NOT NULL,
        categoria TEXT,
        marca_compatible TEXT,
        modelo_compatible TEXT,
        cantidad INTEGER DEFAULT 0,
        precio_costo REAL,
        precio_venta REAL,
        moneda TEXT DEFAULT 'USD',
        ubicacion TEXT,
        notas TEXT,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    # Movimientos de stock
    c.execute('''CREATE TABLE IF NOT EXISTS stock_movimientos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stock_id INTEGER,
        tipo TEXT,
        cantidad INTEGER,
        motivo TEXT,
        usuario_id INTEGER,
        fecha TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(stock_id) REFERENCES stock(id)
    )''')

    # Log de sync
    c.execute('''CREATE TABLE IF NOT EXISTS sync_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT,
        registros_nuevos INTEGER,
        registros_total INTEGER,
        status TEXT,
        detalle TEXT,
        fecha TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    conn.commit()

    # Crear usuarios por defecto
    usuarios_default = [
        ('gonzalo',  'Gonzalo',  'bmw2026', 'admin'),
        ('andres',   'Andrés',   'bmw2026', 'admin'),
        ('guillermo','Guillermo','bmw2026', 'vendedor'),
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

# ── IMPORTAR DATOS EXISTENTES ────────────────────────────
def import_json_data():
    base = os.path.dirname(os.path.abspath(__file__))
    conn = get_db()
    c = conn.cursor()

    # Verificar si ya hay datos
    count = c.execute("SELECT COUNT(*) FROM ventas").fetchone()[0]
    if count > 0:
        print(f"✓ Datos ya importados ({count} ventas)")
        conn.close()
        return

    # Importar ventas - buscar varios nombres posibles
    for fname in ['ventas_data.json', 'ventas_full.json']:
        ventas_path = os.path.join(base, fname)
        if os.path.exists(ventas_path):
            with open(ventas_path) as f:
                ventas = json.load(f)
            for v in ventas:
                c.execute("""INSERT INTO ventas (comprobante,fecha,marca,modelo,anio,motor,chasis,cliente,cliente_doc,precio,moneda)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                    (v.get('comprobante'), v.get('fecha'), v.get('marca'), v.get('modelo'),
                     v.get('anio'), v.get('motor'), v.get('chasis'), v.get('cliente'),
                     v.get('cliente_doc'), v.get('precio',0), v.get('moneda','USD')))
            print(f"✓ {len(ventas)} ventas importadas desde {fname}")
            break
    else:
        print("⚠ No se encontró archivo de ventas")

    # Importar compras
    for fname in ['compras_data.json', 'compras_full.json']:
        compras_path = os.path.join(base, fname)
        if os.path.exists(compras_path):
            with open(compras_path) as f:
                compras = json.load(f)
            for c_ in compras:
                c.execute("""INSERT INTO compras (fecha,marca,modelo,anio,motor,chasis,proveedor,precio,moneda,color,detalle_original)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                    (c_.get('fecha'), c_.get('marca'), c_.get('modelo'), c_.get('anio'),
                     c_.get('motor'), c_.get('chasis'), c_.get('proveedor'),
                     c_.get('precio',0), c_.get('moneda','USD'), c_.get('color'),
                     c_.get('detalle_original')))
            print(f"✓ {len(compras)} compras importadas desde {fname}")
            break
    else:
        print("⚠ No se encontró archivo de compras")

    # Importar clientes
    for fname in ['clientes_data.json', 'clientes_full.json']:
        clientes_path = os.path.join(base, fname)
        if os.path.exists(clientes_path):
            with open(clientes_path) as f:
                clientes = json.load(f)
            for cl in clientes:
                c.execute("""INSERT INTO clientes (nombre,doc,telefono,direccion,ciudad,mail,relacion)
                    VALUES (?,?,?,?,?,?,?)""",
                    (cl.get('nombre'), cl.get('doc'), cl.get('telefono'),
                     cl.get('direccion'), cl.get('ciudad'), cl.get('mail'),
                     cl.get('relacion','Cliente')))
            print(f"✓ {len(clientes)} clientes importados desde {fname}")
            break
    else:
        print("⚠ No se encontró archivo de clientes")

    conn.commit()
    conn.close()

# ── SERVIDOR HTTP ────────────────────────────────────────
def json_response(handler, data, status=200):
    body = json.dumps(data, ensure_ascii=False, default=str).encode('utf-8')
    handler.send_response(status)
    handler.send_header('Content-Type', 'application/json; charset=utf-8')
    handler.send_header('Content-Length', len(body))
    handler.send_header('Access-Control-Allow-Origin', '*')
    handler.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    handler.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    handler.end_headers()
    handler.wfile.write(body)

def get_auth_user(handler):
    auth = handler.headers.get('Authorization', '')
    if auth.startswith('Bearer '):
        return verify_token(auth[7:])
    return None

def require_auth(handler):
    user = get_auth_user(handler)
    if not user:
        json_response(handler, {'error': 'No autorizado'}, 401)
        return None
    return user

def read_body(handler):
    length = int(handler.headers.get('Content-Length', 0))
    if length:
        return json.loads(handler.rfile.read(length).decode('utf-8'))
    return {}

class BMWHandler(http.server.BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        pass  # Silenciar logs por defecto

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)

        # Servir frontend
        if path == '/' or path == '/index.html':
            self._serve_html()
            return

        # API routes
        if path == '/api/health':
            json_response(self, {'status': 'ok', 'version': '1.0', 'empresa': 'BMW Punta del Este'})

        elif path == '/api/me':
            user = require_auth(self)
            if user:
                json_response(self, user)

        elif path == '/api/ventas':
            user = require_auth(self)
            if not user: return
            self._get_ventas(qs)

        elif path == '/api/compras':
            user = require_auth(self)
            if not user: return
            self._get_compras(qs)

        elif path == '/api/clientes':
            user = require_auth(self)
            if not user: return
            self._get_clientes(qs)

        elif path == '/api/negocios':
            user = require_auth(self)
            if not user: return
            self._get_negocios(qs)

        elif path == '/api/stock':
            user = require_auth(self)
            if not user: return
            self._get_stock(qs)

        elif path == '/api/cuotas/pendientes':
            user = require_auth(self)
            if not user: return
            self._get_cuotas_pendientes()

        elif path == '/api/stats':
            user = require_auth(self)
            if not user: return
            self._get_stats()

        elif re.match(r'^/api/negocios/(\d+)/cuotas$', path):
            user = require_auth(self)
            if not user: return
            nid = re.match(r'^/api/negocios/(\d+)/cuotas$', path).group(1)
            self._get_cuotas_negocio(nid)

        else:
            json_response(self, {'error': 'No encontrado'}, 404)

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path

        if path == '/api/login':
            self._login()

        elif path == '/api/ventas':
            user = require_auth(self)
            if not user: return
            self._post_venta(user)

        elif path == '/api/compras':
            user = require_auth(self)
            if not user: return
            self._post_compra(user)

        elif path == '/api/clientes':
            user = require_auth(self)
            if not user: return
            self._post_cliente(user)

        elif path == '/api/negocios':
            user = require_auth(self)
            if not user: return
            self._post_negocio(user)

        elif path == '/api/stock':
            user = require_auth(self)
            if not user: return
            self._post_stock(user)

        elif path == '/api/stock/movimiento':
            user = require_auth(self)
            if not user: return
            self._post_stock_movimiento(user)

        elif path == '/api/cuotas/pagar':
            user = require_auth(self)
            if not user: return
            self._pagar_cuota(user)

        elif path == '/api/sync/import':
            user = require_auth(self)
            if not user: return
            if user.get('rol') != 'admin':
                json_response(self, {'error': 'Solo admins'}, 403)
                return
            self._sync_import(user)

        elif path == '/api/change-password':
            user = require_auth(self)
            if not user: return
            self._change_password(user)

        else:
            json_response(self, {'error': 'No encontrado'}, 404)

    def do_PUT(self):
        path = urllib.parse.urlparse(self.path).path

        m = re.match(r'^/api/ventas/(\d+)$', path)
        if m:
            user = require_auth(self)
            if not user: return
            self._put_venta(m.group(1), user)
            return

        m = re.match(r'^/api/compras/(\d+)$', path)
        if m:
            user = require_auth(self)
            if not user: return
            self._put_compra(m.group(1), user)
            return

        m = re.match(r'^/api/clientes/(\d+)$', path)
        if m:
            user = require_auth(self)
            if not user: return
            self._put_cliente(m.group(1), user)
            return

        m = re.match(r'^/api/negocios/(\d+)$', path)
        if m:
            user = require_auth(self)
            if not user: return
            self._put_negocio(m.group(1), user)
            return

        m = re.match(r'^/api/stock/(\d+)$', path)
        if m:
            user = require_auth(self)
            if not user: return
            self._put_stock(m.group(1), user)
            return

        json_response(self, {'error': 'No encontrado'}, 404)

    # ── AUTH ──
    def _login(self):
        body = read_body(self)
        username = body.get('username', '').lower().strip()
        password = body.get('password', '')

        conn = get_db()
        row = conn.execute("SELECT * FROM usuarios WHERE username=? AND activo=1", (username,)).fetchone()
        conn.close()

        if not row or not check_password(password, row['password_hash']):
            json_response(self, {'error': 'Usuario o contraseña incorrectos'}, 401)
            return

        token = create_token({'id': row['id'], 'username': row['username'],
                               'nombre': row['nombre'], 'rol': row['rol']})
        json_response(self, {'token': token, 'nombre': row['nombre'],
                              'rol': row['rol'], 'username': row['username']})

    def _change_password(self, user):
        body = read_body(self)
        current = body.get('current_password', '')
        new_pw = body.get('new_password', '')
        if not current or not new_pw:
            json_response(self, {'error': 'Contraseña actual y nueva son requeridas'}, 400)
            return
        if len(new_pw) < 4:
            json_response(self, {'error': 'La nueva contraseña debe tener al menos 4 caracteres'}, 400)
            return
        conn = get_db()
        row = conn.execute("SELECT * FROM usuarios WHERE id=?", (user['id'],)).fetchone()
        if not row or not check_password(current, row['password_hash']):
            conn.close()
            json_response(self, {'error': 'Contraseña actual incorrecta'}, 400)
            return
        conn.execute("UPDATE usuarios SET password_hash=? WHERE id=?",
                     (hash_password(new_pw), user['id']))
        conn.commit()
        conn.close()
        json_response(self, {'ok': True, 'message': 'Contraseña actualizada'})

    # ── VENTAS ──
    def _get_ventas(self, qs):
        conn = get_db()
        q = qs.get('q', [''])[0].lower()
        marca = qs.get('marca', [''])[0]
        limit = int(qs.get('limit', ['500'])[0])
        offset = int(qs.get('offset', ['0'])[0])

        where, params = [], []
        if q:
            where.append("(LOWER(cliente)||' '||LOWER(COALESCE(marca,''))||' '||LOWER(COALESCE(modelo,''))||' '||LOWER(COALESCE(chasis,''))||' '||LOWER(COALESCE(motor,''))) LIKE ?")
            params.append(f'%{q}%')
        if marca:
            where.append("marca = ?")
            params.append(marca)

        sql = "SELECT * FROM ventas"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY fecha DESC, id DESC"
        sql += f" LIMIT {limit} OFFSET {offset}"

        rows = [dict(r) for r in conn.execute(sql, params).fetchall()]
        total = conn.execute("SELECT COUNT(*) FROM ventas" + (" WHERE " + " AND ".join(where) if where else ""), params).fetchone()[0]
        conn.close()
        json_response(self, {'data': rows, 'total': total})

    def _post_venta(self, user):
        v = read_body(self)
        conn = get_db()
        c = conn.cursor()
        c.execute("""INSERT INTO ventas (comprobante,fecha,marca,modelo,anio,motor,chasis,cliente,cliente_doc,precio,moneda,usuario_id,updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (v.get('comprobante'), v.get('fecha'), v.get('marca','').upper(),
             v.get('modelo','').upper(), v.get('anio'), v.get('motor','').upper(),
             v.get('chasis','').upper(), v.get('cliente'), v.get('cliente_doc'),
             v.get('precio',0), v.get('moneda','USD'), user['id'],
             datetime.datetime.now().isoformat()))
        conn.commit()
        new_id = c.lastrowid
        row = dict(conn.execute("SELECT * FROM ventas WHERE id=?", (new_id,)).fetchone())
        conn.close()
        json_response(self, row, 201)

    def _put_venta(self, vid, user):
        v = read_body(self)
        conn = get_db()
        conn.execute("""UPDATE ventas SET comprobante=?,fecha=?,marca=?,modelo=?,anio=?,motor=?,
            chasis=?,cliente=?,cliente_doc=?,precio=?,moneda=?,updated_at=? WHERE id=?""",
            (v.get('comprobante'), v.get('fecha'), v.get('marca','').upper(),
             v.get('modelo','').upper(), v.get('anio'), v.get('motor','').upper(),
             v.get('chasis','').upper(), v.get('cliente'), v.get('cliente_doc'),
             v.get('precio',0), v.get('moneda','USD'),
             datetime.datetime.now().isoformat(), vid))
        conn.commit()
        row = dict(conn.execute("SELECT * FROM ventas WHERE id=?", (vid,)).fetchone())
        conn.close()
        json_response(self, row)

    # ── COMPRAS ──
    def _get_compras(self, qs):
        conn = get_db()
        q = qs.get('q', [''])[0].lower()
        marca = qs.get('marca', [''])[0]
        limit = int(qs.get('limit', ['500'])[0])
        offset = int(qs.get('offset', ['0'])[0])

        where, params = [], []
        if q:
            where.append("(LOWER(proveedor)||' '||LOWER(COALESCE(marca,''))||' '||LOWER(COALESCE(modelo,''))||' '||LOWER(COALESCE(chasis,''))) LIKE ?")
            params.append(f'%{q}%')
        if marca:
            where.append("marca = ?")
            params.append(marca)

        sql = "SELECT * FROM compras"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY fecha DESC, id DESC"
        sql += f" LIMIT {limit} OFFSET {offset}"

        rows = [dict(r) for r in conn.execute(sql, params).fetchall()]
        total = conn.execute("SELECT COUNT(*) FROM compras" + (" WHERE " + " AND ".join(where) if where else ""), params).fetchone()[0]
        conn.close()
        json_response(self, {'data': rows, 'total': total})

    def _post_compra(self, user):
        v = read_body(self)
        conn = get_db()
        c = conn.cursor()
        c.execute("""INSERT INTO compras (fecha,marca,modelo,anio,motor,chasis,proveedor,precio,moneda,color,usuario_id,updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (v.get('fecha'), v.get('marca','').upper(), v.get('modelo','').upper(),
             v.get('anio'), v.get('motor','').upper(), v.get('chasis','').upper(),
             v.get('proveedor'), v.get('precio',0), v.get('moneda','USD'),
             v.get('color'), user['id'], datetime.datetime.now().isoformat()))
        conn.commit()
        row = dict(conn.execute("SELECT * FROM compras WHERE id=?", (c.lastrowid,)).fetchone())
        conn.close()
        json_response(self, row, 201)

    def _put_compra(self, cid, user):
        v = read_body(self)
        conn = get_db()
        conn.execute("""UPDATE compras SET fecha=?,marca=?,modelo=?,anio=?,motor=?,chasis=?,
            proveedor=?,precio=?,moneda=?,color=?,updated_at=? WHERE id=?""",
            (v.get('fecha'), v.get('marca','').upper(), v.get('modelo','').upper(),
             v.get('anio'), v.get('motor','').upper(), v.get('chasis','').upper(),
             v.get('proveedor'), v.get('precio',0), v.get('moneda','USD'),
             v.get('color'), datetime.datetime.now().isoformat(), cid))
        conn.commit()
        row = dict(conn.execute("SELECT * FROM compras WHERE id=?", (cid,)).fetchone())
        conn.close()
        json_response(self, row)

    # ── CLIENTES ──
    def _get_clientes(self, qs):
        conn = get_db()
        q = qs.get('q', [''])[0].lower()
        campo = qs.get('campo', ['todos'])[0]
        limit = int(qs.get('limit', ['500'])[0])
        offset = int(qs.get('offset', ['0'])[0])

        where, params = [], []
        if q:
            if campo == 'nombre':
                where.append("LOWER(nombre) LIKE ?")
            elif campo == 'doc':
                where.append("LOWER(COALESCE(doc,'')) LIKE ?")
            else:
                where.append("(LOWER(nombre)||' '||LOWER(COALESCE(doc,''))||' '||LOWER(COALESCE(ciudad,''))||' '||LOWER(COALESCE(mail,''))) LIKE ?")
            params.append(f'%{q}%')

        sql = "SELECT * FROM clientes"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY nombre ASC"
        sql += f" LIMIT {limit} OFFSET {offset}"

        rows = [dict(r) for r in conn.execute(sql, params).fetchall()]
        total = conn.execute("SELECT COUNT(*) FROM clientes" + (" WHERE " + " AND ".join(where) if where else ""), params).fetchone()[0]

        # Agregar historial de ventas para cada cliente
        for cl in rows:
            doc = (cl.get('doc') or '').strip()
            nombre = (cl.get('nombre') or '').strip()
            if doc:
                cl_ventas = conn.execute(
                    """SELECT comprobante,fecha,marca,modelo,chasis,precio,moneda FROM ventas
                       WHERE LOWER(TRIM(cliente_doc))=LOWER(?) OR LOWER(TRIM(cliente))=LOWER(?)
                       ORDER BY fecha DESC""",
                    (doc, nombre)).fetchall()
            else:
                cl_ventas = conn.execute(
                    """SELECT comprobante,fecha,marca,modelo,chasis,precio,moneda FROM ventas
                       WHERE LOWER(TRIM(cliente))=LOWER(?) ORDER BY fecha DESC""",
                    (nombre,)).fetchall()
            cl['compras'] = [dict(v) for v in cl_ventas]

        conn.close()
        json_response(self, {'data': rows, 'total': total})

    def _post_cliente(self, user):
        v = read_body(self)
        conn = get_db()
        c = conn.cursor()
        c.execute("""INSERT INTO clientes (nombre,doc,telefono,direccion,ciudad,mail,relacion,updated_at)
            VALUES (?,?,?,?,?,?,?,?)""",
            (v.get('nombre','').upper(), v.get('doc'), v.get('telefono'),
             v.get('direccion'), v.get('ciudad','').upper(), v.get('mail'),
             v.get('relacion','Cliente'), datetime.datetime.now().isoformat()))
        conn.commit()
        row = dict(conn.execute("SELECT * FROM clientes WHERE id=?", (c.lastrowid,)).fetchone())
        row['compras'] = []
        conn.close()
        json_response(self, row, 201)

    def _put_cliente(self, cid, user):
        v = read_body(self)
        conn = get_db()
        conn.execute("""UPDATE clientes SET nombre=?,doc=?,telefono=?,direccion=?,ciudad=?,mail=?,relacion=?,updated_at=? WHERE id=?""",
            (v.get('nombre','').upper(), v.get('doc'), v.get('telefono'),
             v.get('direccion'), v.get('ciudad','').upper(), v.get('mail'),
             v.get('relacion','Cliente'), datetime.datetime.now().isoformat(), cid))
        conn.commit()
        row = dict(conn.execute("SELECT * FROM clientes WHERE id=?", (cid,)).fetchone())
        row['compras'] = []
        conn.close()
        json_response(self, row)

    # ── NEGOCIOS ──
    def _get_negocios(self, qs):
        conn = get_db()
        q = qs.get('q', [''])[0].lower()
        estado = qs.get('estado', [''])[0]
        limit = int(qs.get('limit', ['200'])[0])
        offset = int(qs.get('offset', ['0'])[0])

        where, params = [], []
        if q:
            where.append("(LOWER(cliente_nombre)||' '||LOWER(COALESCE(vehiculo_modelo,''))||' '||LOWER(COALESCE(vehiculo_chasis,''))) LIKE ?")
            params.append(f'%{q}%')
        if estado:
            where.append("estado=?")
            params.append(estado)

        sql = "SELECT n.*, u.nombre as usuario_nombre FROM negocios n LEFT JOIN usuarios u ON n.usuario_id=u.id"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY created_at DESC"
        sql += f" LIMIT {limit} OFFSET {offset}"

        rows = [dict(r) for r in conn.execute(sql, params).fetchall()]
        total = conn.execute("SELECT COUNT(*) FROM negocios" + (" WHERE " + " AND ".join(where) if where else ""), params).fetchone()[0]

        # Agregar cuotas pendientes
        for n in rows:
            cuotas_pend = conn.execute("SELECT COUNT(*) FROM cuotas WHERE negocio_id=? AND pagada=0", (n['id'],)).fetchone()[0]
            cuotas_total = conn.execute("SELECT COUNT(*) FROM cuotas WHERE negocio_id=?", (n['id'],)).fetchone()[0]
            n['cuotas_pendientes'] = cuotas_pend
            n['cuotas_total'] = cuotas_total

        conn.close()
        json_response(self, {'data': rows, 'total': total})

    def _get_cuotas_negocio(self, nid):
        conn = get_db()
        rows = [dict(r) for r in conn.execute("SELECT * FROM cuotas WHERE negocio_id=? ORDER BY numero", (nid,)).fetchall()]
        conn.close()
        json_response(self, rows)

    def _get_cuotas_pendientes(self):
        conn = get_db()
        hoy = datetime.date.today().isoformat()
        rows = conn.execute("""
            SELECT c.*, n.cliente_nombre, n.vehiculo_marca, n.vehiculo_modelo
            FROM cuotas c JOIN negocios n ON c.negocio_id=n.id
            WHERE c.pagada=0 AND c.fecha_vencimiento <= ?
            ORDER BY c.fecha_vencimiento
        """, (hoy,)).fetchall()
        conn.close()
        json_response(self, [dict(r) for r in rows])

    def _post_negocio(self, user):
        v = read_body(self)
        conn = get_db()
        c = conn.cursor()
        c.execute("""INSERT INTO negocios (cliente_id,cliente_nombre,vehiculo_marca,vehiculo_modelo,
            vehiculo_anio,vehiculo_chasis,precio_venta,moneda,metodo_pago,cuotas,monto_cuota,
            fecha_primera_cuota,fecha_negocio,estado,notas,usuario_id)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (v.get('cliente_id'), v.get('cliente_nombre','').upper(),
             v.get('vehiculo_marca','').upper(), v.get('vehiculo_modelo','').upper(),
             v.get('vehiculo_anio'), v.get('vehiculo_chasis','').upper(),
             v.get('precio_venta',0), v.get('moneda','USD'), v.get('metodo_pago'),
             v.get('cuotas',0), v.get('monto_cuota'), v.get('fecha_primera_cuota'),
             v.get('fecha_negocio', datetime.date.today().isoformat()),
             v.get('estado','activo'), v.get('notas'), user['id']))
        conn.commit()
        neg_id = c.lastrowid

        # Generar cuotas si corresponde
        cuotas_n = v.get('cuotas', 0)
        if cuotas_n and cuotas_n > 0 and v.get('fecha_primera_cuota'):
            monto = v.get('monto_cuota', 0)
            moneda = v.get('moneda', 'USD')
            try:
                fecha = datetime.date.fromisoformat(v['fecha_primera_cuota'])
                for i in range(cuotas_n):
                    # siguiente mes
                    mes = fecha.month + i
                    anio = fecha.year + (mes - 1) // 12
                    mes = ((mes - 1) % 12) + 1
                    fv = fecha.replace(year=anio, month=mes)
                    c.execute("INSERT INTO cuotas (negocio_id,numero,fecha_vencimiento,monto,moneda) VALUES (?,?,?,?,?)",
                             (neg_id, i+1, fv.isoformat(), monto, moneda))
            except Exception as e:
                print(f"Error generando cuotas: {e}")
            conn.commit()

        row = dict(conn.execute("SELECT * FROM negocios WHERE id=?", (neg_id,)).fetchone())
        row['cuotas_pendientes'] = cuotas_n
        row['cuotas_total'] = cuotas_n
        conn.close()
        json_response(self, row, 201)

    def _put_negocio(self, nid, user):
        v = read_body(self)
        conn = get_db()
        conn.execute("""UPDATE negocios SET estado=?,notas=? WHERE id=?""",
            (v.get('estado','activo'), v.get('notas'), nid))
        conn.commit()
        row = dict(conn.execute("SELECT * FROM negocios WHERE id=?", (nid,)).fetchone())
        conn.close()
        json_response(self, row)

    def _pagar_cuota(self, user):
        v = read_body(self)
        cid = v.get('cuota_id')
        conn = get_db()
        conn.execute("UPDATE cuotas SET pagada=1, fecha_pago=? WHERE id=?",
                    (datetime.date.today().isoformat(), cid))
        conn.commit()
        conn.close()
        json_response(self, {'ok': True})

    # ── STOCK ──
    def _get_stock(self, qs):
        conn = get_db()
        q = qs.get('q', [''])[0].lower()
        cat = qs.get('categoria', [''])[0]

        where, params = [], []
        if q:
            where.append("(LOWER(nombre)||' '||LOWER(COALESCE(codigo,''))||' '||LOWER(COALESCE(categoria,''))) LIKE ?")
            params.append(f'%{q}%')
        if cat:
            where.append("categoria=?")
            params.append(cat)

        sql = "SELECT * FROM stock"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY categoria, nombre"

        rows = [dict(r) for r in conn.execute(sql, params).fetchall()]
        conn.close()
        json_response(self, {'data': rows, 'total': len(rows)})

    def _post_stock(self, user):
        v = read_body(self)
        conn = get_db()
        c = conn.cursor()
        c.execute("""INSERT INTO stock (codigo,nombre,categoria,marca_compatible,modelo_compatible,
            cantidad,precio_costo,precio_venta,moneda,ubicacion,notas,updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (v.get('codigo'), v.get('nombre'), v.get('categoria'), v.get('marca_compatible'),
             v.get('modelo_compatible'), v.get('cantidad',0), v.get('precio_costo'),
             v.get('precio_venta'), v.get('moneda','USD'), v.get('ubicacion'),
             v.get('notas'), datetime.datetime.now().isoformat()))
        conn.commit()
        row = dict(conn.execute("SELECT * FROM stock WHERE id=?", (c.lastrowid,)).fetchone())
        conn.close()
        json_response(self, row, 201)

    def _put_stock(self, sid, user):
        v = read_body(self)
        conn = get_db()
        conn.execute("""UPDATE stock SET codigo=?,nombre=?,categoria=?,marca_compatible=?,
            modelo_compatible=?,precio_costo=?,precio_venta=?,moneda=?,ubicacion=?,notas=?,updated_at=? WHERE id=?""",
            (v.get('codigo'), v.get('nombre'), v.get('categoria'), v.get('marca_compatible'),
             v.get('modelo_compatible'), v.get('precio_costo'), v.get('precio_venta'),
             v.get('moneda','USD'), v.get('ubicacion'), v.get('notas'),
             datetime.datetime.now().isoformat(), sid))
        conn.commit()
        row = dict(conn.execute("SELECT * FROM stock WHERE id=?", (sid,)).fetchone())
        conn.close()
        json_response(self, row)

    def _post_stock_movimiento(self, user):
        v = read_body(self)
        sid = v.get('stock_id')
        tipo = v.get('tipo')  # 'entrada' o 'salida'
        cantidad = int(v.get('cantidad', 0))
        conn = get_db()
        delta = cantidad if tipo == 'entrada' else -cantidad
        conn.execute("UPDATE stock SET cantidad=MAX(0,cantidad+?), updated_at=? WHERE id=?",
                    (delta, datetime.datetime.now().isoformat(), sid))
        conn.execute("INSERT INTO stock_movimientos (stock_id,tipo,cantidad,motivo,usuario_id) VALUES (?,?,?,?,?)",
                    (sid, tipo, cantidad, v.get('motivo'), user['id']))
        conn.commit()
        row = dict(conn.execute("SELECT * FROM stock WHERE id=?", (sid,)).fetchone())
        conn.close()
        json_response(self, row)

    # ── STATS ──
    def _get_stats(self):
        conn = get_db()
        stats = {
            'ventas': conn.execute("SELECT COUNT(*) FROM ventas").fetchone()[0],
            'compras': conn.execute("SELECT COUNT(*) FROM compras").fetchone()[0],
            'clientes': conn.execute("SELECT COUNT(*) FROM clientes").fetchone()[0],
            'negocios_activos': conn.execute("SELECT COUNT(*) FROM negocios WHERE estado='activo'").fetchone()[0],
            'cuotas_vencidas': conn.execute("SELECT COUNT(*) FROM cuotas WHERE pagada=0 AND fecha_vencimiento<?",
                                            (datetime.date.today().isoformat(),)).fetchone()[0],
            'stock_items': conn.execute("SELECT COUNT(*) FROM stock").fetchone()[0],
            'stock_bajo': conn.execute("SELECT COUNT(*) FROM stock WHERE cantidad<=3 AND cantidad>0").fetchone()[0],
            'marcas_ventas': [dict(r) for r in conn.execute(
                "SELECT marca, COUNT(*) as cnt FROM ventas WHERE marca IS NOT NULL GROUP BY marca ORDER BY cnt DESC").fetchall()],
        }
        conn.close()
        json_response(self, stats)

    # ── SYNC ──
    def _sync_import(self, user):
        """Importar datos frescos desde los JSONs (cuando se actualicen desde eFactura)"""
        v = read_body(self)
        tipo = v.get('tipo', 'all')  # 'ventas', 'compras', 'clientes', 'all'
        nuevos = v.get('datos', [])  # datos ya scrapeados enviados desde el frontend

        conn = get_db()
        count_new = 0

        if tipo in ('ventas', 'all') and v.get('ventas'):
            for rec in v['ventas']:
                existing = conn.execute("SELECT id FROM ventas WHERE comprobante=? AND comprobante IS NOT NULL",
                                       (rec.get('comprobante'),)).fetchone()
                if not existing:
                    conn.execute("""INSERT INTO ventas (comprobante,fecha,marca,modelo,anio,motor,chasis,cliente,cliente_doc,precio,moneda,updated_at)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                        (rec.get('comprobante'), rec.get('fecha'), rec.get('marca','').upper(),
                         rec.get('modelo','').upper(), rec.get('anio'), rec.get('motor','').upper(),
                         rec.get('chasis','').upper(), rec.get('cliente'), rec.get('cliente_doc'),
                         rec.get('precio',0), rec.get('moneda','USD'), datetime.datetime.now().isoformat()))
                    count_new += 1

        if tipo in ('compras', 'all') and v.get('compras'):
            for rec in v['compras']:
                existing = conn.execute("SELECT id FROM compras WHERE chasis=? AND chasis IS NOT NULL AND chasis!=''",
                                       (rec.get('chasis','').upper(),)).fetchone()
                if not existing:
                    conn.execute("""INSERT INTO compras (fecha,marca,modelo,anio,motor,chasis,proveedor,precio,moneda,color,updated_at)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                        (rec.get('fecha'), rec.get('marca','').upper(), rec.get('modelo','').upper(),
                         rec.get('anio'), rec.get('motor','').upper(), rec.get('chasis','').upper(),
                         rec.get('proveedor'), rec.get('precio',0), rec.get('moneda','USD'),
                         rec.get('color'), datetime.datetime.now().isoformat()))
                    count_new += 1

        if tipo in ('clientes', 'all') and v.get('clientes'):
            for rec in v['clientes']:
                existing = conn.execute("SELECT id FROM clientes WHERE doc=? AND doc IS NOT NULL",
                                       (rec.get('doc'),)).fetchone()
                if not existing:
                    conn.execute("""INSERT INTO clientes (nombre,doc,telefono,direccion,ciudad,mail,relacion,updated_at)
                        VALUES (?,?,?,?,?,?,?,?)""",
                        (rec.get('nombre','').upper(), rec.get('doc'), rec.get('telefono'),
                         rec.get('direccion'), rec.get('ciudad','').upper(), rec.get('mail'),
                         rec.get('relacion','Cliente'), datetime.datetime.now().isoformat()))
                    count_new += 1

        conn.execute("INSERT INTO sync_log (tipo,registros_nuevos,status) VALUES (?,?,?)",
                    (tipo, count_new, 'ok'))
        conn.commit()
        conn.close()

        total_ventas = get_db().execute("SELECT COUNT(*) FROM ventas").fetchone()[0]
        json_response(self, {'ok': True, 'nuevos': count_new, 'total_ventas': total_ventas})

    # ── SERVE FILES ──
    def _serve_html(self):
        # Servir index.html externo si existe, sino el HTML embebido
        index_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index.html')
        if os.path.exists(index_path):
            with open(index_path, 'rb') as f:
                body = f.read()
        else:
            body = HTML_CONTENT.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', len(body))
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(body)

    def _serve_file(self, path, content_type):
        try:
            with open(path, 'rb') as f:
                body = f.read()
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', len(body))
            self.end_headers()
            self.wfile.write(body)
        except FileNotFoundError:
            json_response(self, {'error': 'Archivo no encontrado'}, 404)

# ── MAIN ─────────────────────────────────────────────────
if __name__ == '__main__':
    print("=" * 50)
    print("  BMW Punta del Este - Servidor de Gestión")
    print("=" * 50)

    init_db()
    import_json_data()

    # Copiar index.html al static si existe el build
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    os.makedirs(static_dir, exist_ok=True)

    server = http.server.ThreadingHTTPServer(('0.0.0.0', PORT), BMWHandler)
    print(f"\n✓ Servidor corriendo en http://localhost:{PORT}")
    print(f"  Usuarios: gonzalo / andres / guillermo")
    print(f"  Contraseña por defecto: bmw2026")
    print(f"\n  Ctrl+C para detener\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n✓ Servidor detenido")
