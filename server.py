#!/usr/bin/env python3
"""
AutomotoraGV - Servidor Local
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

# -- HTML INCRUSTADO --------------------------------------
HTML_CONTENT = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>AutomotoraGV</title>
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

/* -- LOGIN -- */
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

/* -- APP -- */
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

/* -- MENU PRINCIPAL -- */
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

/* -- TOOLBAR + TABLE -- */
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

/* -- PAG -- */
.pag{display:flex;align-items:center;justify-content:space-between;padding:10px 14px;border-top:1px solid var(--bd);background:var(--bg3)}
.pi{font-size:12px;color:var(--tx3)}
.pbs{display:flex;gap:4px}
.pb{font-family:var(--mo);font-size:12px;padding:3px 9px;border-radius:6px;border:1px solid var(--bd);background:var(--bg4);cursor:pointer;color:var(--tx3);transition:all .12s}
.pb:hover{background:var(--bg3);color:var(--tx)}
.pb.ac{background:var(--acc);color:#0f0f0f;border-color:var(--acc);font-weight:700}

/* -- MODAL -- */
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

/* -- DETAIL ROWS -- */
.dr{display:flex;gap:12px;padding:7px 0;border-bottom:1px solid var(--bd);font-size:13px}
.dr:last-child{border-bottom:none}
.dl{color:var(--tx3);width:120px;flex-shrink:0;font-size:11px;font-family:var(--fh);text-transform:uppercase;letter-spacing:.4px;padding-top:1px}
.dv{color:var(--tx);word-break:break-all;flex:1}

/* -- BRAND CHIPS -- */
.brand-bar{display:flex;flex-wrap:wrap;gap:7px;margin-bottom:14px}
.bchip{display:flex;align-items:center;gap:7px;padding:6px 13px;border-radius:9px;border:1px solid var(--bd);background:var(--bg2);cursor:pointer;transition:all .15s;user-select:none;font-family:var(--fh);font-size:12px;font-weight:700}
.bchip:hover{border-color:var(--bd2);background:var(--bg3)}
.bchip.all{background:var(--bg3)}
.bchip.all.active{background:var(--acc);border-color:var(--acc);color:#0f0f0f}
.bchip-cnt{font-family:var(--mo);font-size:11px;opacity:.7}

/* -- LOADING / EMPTY -- */
.loading{text-align:center;padding:48px;color:var(--tx3);font-size:13px}
.loading-spin{display:inline-block;width:20px;height:20px;border:2px solid var(--bd2);border-top-color:var(--acc);border-radius:50%;animation:spin .7s linear infinite;margin-bottom:10px}
@keyframes spin{to{transform:rotate(360deg)}}
.empty{text-align:center;padding:48px;color:var(--tx3);font-size:13px}
.empty-icon{font-size:32px;margin-bottom:8px}

/* -- NEGOCIOS -- */
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

/* -- STOCK -- */
.stock-low{color:var(--rd) !important}
.stock-ok{color:var(--gn) !important}

/* -- FACTURACION -- */
.fac-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:24px}
.fac-card{background:var(--bg2);border:1px solid var(--bd);border-radius:var(--rl);padding:22px 24px;position:relative;overflow:hidden}
.fac-card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px}
.fac-card.v::before{background:var(--bl)}
.fac-card.c::before{background:var(--acc)}
.fac-card.s::before{background:var(--gn)}
.fc-label{font-size:11px;font-family:var(--fh);text-transform:uppercase;letter-spacing:1px;color:var(--tx3);margin-bottom:10px}
.fc-val{font-family:var(--mo);font-size:26px;font-weight:700;line-height:1;margin-bottom:4px}
.fc-sub{font-size:12px;color:var(--tx3)}

/* -- CUOTAS -- */
.cuota-row{display:flex;align-items:center;justify-content:space-between;padding:9px 0;border-bottom:1px solid var(--bd);gap:12px}
.cuota-row:last-child{border-bottom:none}
.cuota-num{font-family:var(--mo);font-size:11px;color:var(--tx3);width:40px;flex-shrink:0}
.cuota-fecha{font-family:var(--mo);font-size:12px;color:var(--tx2);flex:1}
.cuota-monto{font-family:var(--mo);font-size:13px;font-weight:600;color:var(--acc2)}
.cuota-pagada{color:var(--gn);font-size:11px;font-family:var(--fh);font-weight:700}
.cuota-vencida{color:var(--rd);font-size:11px;font-family:var(--fh);font-weight:700}

/* -- TOAST -- */
.toast{position:fixed;bottom:24px;right:24px;background:var(--bg3);border:1px solid var(--bd2);border-radius:10px;padding:12px 18px;font-size:13px;color:var(--tx);z-index:999;transform:translateY(20px);opacity:0;transition:all .25s;box-shadow:0 4px 20px rgba(0,0,0,.4)}
.toast.show{transform:translateY(0);opacity:1}
.toast.ok{border-left:3px solid var(--gn)}
.toast.err{border-left:3px solid var(--rd)}

/* -- SYNC BUTTON -- */
.sync-btn{display:flex;align-items:center;gap:6px;font-family:var(--fn);font-size:12px;font-weight:500;padding:6px 14px;border-radius:8px;border:1px solid var(--bd);cursor:pointer;background:var(--bg3);color:var(--tx2);transition:all .15s}
.sync-btn:hover{border-color:var(--acc);color:var(--acc)}
.sync-btn.syncing svg{animation:spin .7s linear infinite}

/* -- PAGE -- */
.page{display:none}
.page.active{display:block}

/* -- SCROLLBAR -- */
::-webkit-scrollbar{width:5px;height:5px}
::-webkit-scrollbar-track{background:var(--bg)}
::-webkit-scrollbar-thumb{background:var(--bd2);border-radius:3px}

/* -- SYNC MODAL -- */
.sync-log-line{font-family:var(--mo);font-size:12px;padding:4px 0;border-bottom:1px solid var(--bd);color:var(--tx2)}
.sync-log-line.ok{color:var(--gn)}
.sync-log-line.err{color:var(--rd)}
.sync-progress{background:var(--bg4);border-radius:6px;height:8px;overflow:hidden;margin:10px 0}
.sync-progress-fill{height:100%;background:var(--acc);border-radius:6px;transition:width .3s;width:0%}

/*    MOBILE RESPONSIVE                                 */
@media (max-width: 768px) {
  #sidebar {
    position: fixed; left: -230px; top: 0; height: 100vh;
    z-index: 200; transition: left .25s ease; width: 220px !important;
  }
  #sidebar.open { left: 0; }
  #main { margin-left: 0 !important; padding: 12px !important; }
  #topbar { padding: 10px 12px !important; }
  #topbar h1 { font-size: 16px !important; }
  .hamburger {
    display: flex !important; position: fixed; top: 12px; left: 12px;
    z-index: 300; background: var(--bg2); border: 1px solid var(--bg4);
    border-radius: 8px; padding: 8px; cursor: pointer; flex-direction: column;
    gap: 4px; align-items: center; justify-content: center;
  }
  .hamburger span { display: block; width: 20px; height: 2px; background: var(--tx1); border-radius: 2px; }
  .sidebar-overlay {
    display: none; position: fixed; inset: 0; background: rgba(0,0,0,.5);
    z-index: 150;
  }
  .sidebar-overlay.open { display: block; }
  table { font-size: 12px !important; }
  th, td { padding: 6px 8px !important; }
  .cards-grid { grid-template-columns: 1fr !important; }
  .stat-cards { grid-template-columns: 1fr 1fr !important; }
  .ov > div { width: 95vw !important; max-height: 90vh; overflow-y: auto; }
  #topbar .sync-btn span { display: none; }
  .page-header { flex-direction: column; gap: 8px; align-items: flex-start !important; }
  .filters-row { flex-wrap: wrap; gap: 6px !important; }
  .filters-row select, .filters-row input { flex: 1 1 120px !important; }
}
@media (min-width: 769px) {
  .hamburger { display: none !important; }
  .sidebar-overlay { display: none !important; }
}

</style>
</head>
<body>
<div id="splash" style="position:fixed;inset:0;background:#000;display:flex;flex-direction:column;align-items:center;justify-content:center;z-index:99999;transition:opacity 0.6s ease">
  <img src="data:image/jpeg;base64,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AQEBAQEAAAAAAAABAgMEBQYHCAkKC//EALURAAIBAgQEAwQHBQQEAAECdwABAgMRBAUhMQYSQVEHYXETIjKBCBRCkaGxwQkjM1LwFWJy0QoWJDThJfEXGBkaJicoKSo1Njc4OTpDREVGR0hJSlNUVVZXWFlaY2RlZmdoaWpzdHV2d3h5eoKDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uLj5OXm5+jp6vLz9PX29/j5+v/bAEMAAgICAgICAwICAwUDAwMFBgUFBQUGCAYGBgYGCAoICAgICAgKCgoKCgoKCgwMDAwMDA4ODg4ODw8PDw8PDw8PD//bAEMBAgMDBAQEBwQEBxALCQsQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEP/dAAQAgP/aAAwDAQACEQMRAD8A/n/oAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKAP/Q/n/oAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKAP/R/n/oAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKAP/S/n/oAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKAP/T/n/oAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKAP/U/n/oAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKAP/V/n/oAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKAP/W/n/oAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKAP/X/n/oAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKAP/Q/n/oAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKAP/R/n/oAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKAP/S/n/oAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKAP/T/n/oAk2+1ABt9qADb7UAG32oANvtQAbfagA2+1ABt9qADb7UAG32oANvtQAbfagA2+1ABt9qADb7UAG32oANvtQAbfagA2+1ABt9qADb7UAG32oANvtQAbfagA2+1ABt9qADb7UAG32oANvtQAbfagA2+1ABt9qADb7UAG32oANvtQAbfagA2+1ABt9qADb7UAG32oANvtQAbfagA2+1ABt9qADb7UAG32oANvtQAbfagA2+1ABt9qADb7UAG32oANvtQAbfagA2+1ABt9qADb7UAG32oANvtQAbfagA2+1ABt9qADb7UAG32oANvtQAbfagA2+1ABt9qADb7UAG32oANvtQAbfagA2+1ABt9qADb7UAG32oANvtQAbfagA2+1ABt9qADb7UAG32oANvtQAbfagA2+1ABt9qADb7UAG32oANvtQAbfagA2+1ABt9qADb7UAG32oANvtQAbfagA2+1ABt9qADb7UAG32oANvtQAbfagA2+1ABt9qADb7UAG32oANvtQAbfagA2+1ABt9qADb7UAG32oANvtQAbfagA2+1ABt9qADb7UAG32oANvtQAbfagA2+1ABt9qADb7UAR0AFABQAUAf/1P5/6ALFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAfwUARt9+gCOgAoAKAP/V/ADvQBPQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAH8FAELfeNADaACgAoA//W/ADvQBPQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAH8FAELfeNADaACgAoA//X/ADvQBPQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAH8FAELfeNADaACgAoA//Q/ADvQBPQ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seJPFX/CQSavJ8jbloA+7Pgj/wAFBbjW/Dsvg74hyrNFPF5W6SgD81P2gIdAl+IF3feG5Veynbcu2gDwagAoAKANXRbaC61K3gnfy0dvmagD9i/D37XXhj4D/Ce30Dwc0T6m8W1mX79AHwf4n/a5+LeseJU1z+15PkbcqrQB9+fBz9vx/EnhK48HfEaVX8+LZuagD8vPjp/Yz+OLu70OVZbe6d2+WgDxagAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKAD+CgCFvvGgBtABQAUAf//T/ADvQBPQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQBG9AEsM0kR+RtmaAJJ7iSZ97u0n+9QBFQBIlzJF/q2ZKAFad7h/Mn+egCKgAoAKABHdG+SgCV5pp3/AHzb6AIvv0ASJNNCf3bNQAwu8j/P9+gBKACgAd6AJVvLrbs81tlAEVABu96ALH26fb5e9tn92gCvv30AFABQAu50felAEhmmdfmbfQBFQBJDNJC/mI/z0ASTXk9y379t9AFegAoAKABXdG8yP5KALE1zPN/r23mgCvQBKkzxPvRmjf8A2aAEmuHl5dmf/eoAjoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgA/goAhb7xoAbQAUAFAH//U/ADvQBPQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFAB9ygAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAP4KAIW+8aAG0AFABQB//9X8AO9AE9ABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAfwUAQt940ANoAKACgD/9b8A/46AJKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgA/goAhb7xoAbQAUAFAH//X/AP+OgCSgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAP4KAIW+8aAG0AFABQB//0PwD/joAkoAKACgAoAKACgAoAKACgA+/QAUAFABQAUAFABQAbXoAk2vQBHQAUAFABQAUAFABQAUAFABt9qACgA2O/SgA+5QAUAFABQAUAFABQAbfagAoAKACgAoAKACgAoAKACgAoAKACgAoAPv/AHKAF2P/AHWoASgAoAKACgAoAKACgAoAKACgAoAKACgA/goAKACgAoAKACgAoAKADZsoAKACgAoAKACgA/goAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgA2+1ABQA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vlefHYx70/2qAPF/HP8AwVxSaCVPDmnqkqfdagD8v/jf+2B8TfjTcONV1CWG0f8A5Zq1AHyY7738z1oARPloA9F8B/FDxf8ADnVE1Hw5qEls6N/C1AH6n/Cb/gqn408OWtvYeK4vtiQfxbqAPsjTf+CrngC/t0kvrGNH/wB6gCvqv/BWPwPYRP8AZbGN/wC5QB8f/Fr/AIKp+NPElnLY+FYvsaP/ABK1AH5b/EL4reMfiRqL6j4mvpblpG+6zUAeZ/foAKAD+CgCFvvGgBtABQAUAf/X/AP+OgCSgAoAKACgAoAKACgAoAKACgAoAKACgAoAKABKADf8lAA9ABQAUAFAB/HQAUAFABQAUAFAB/HQAUAH8dABQAUAFABQAZ/2qACgAz/tUAR/PQBJQAUAFABQAUAFABQAUAFABj/ZoAKACgA/goAKAJPk20AR0AG32oAKACgAoAKACgAoAKACgAoAVHkjoATfvoAKACgAoAKADP8AtUAFAB8+2gAoAKACgAoAKAB6ABPloAKADP8AtUAFABQAUAK7JQAn/XOgAoAKAD+OgA3e9ABu96ACgA/goAN/+9QAvmP/AHm2UAJv30AFABQAUAFABu96AF8+Tbs3N/31QAKzueKAEoAKACgAoAFd16NQAb5P71ABn/aoAKACgAoAKACgA3yf3qAF3yD7+40AJ8lAB/BQAUAFAB/BQBC33jQA2gAoAKAP/9D8A/46AJKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAPuUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFAB/BQBC33jQA2gAoAKAP/0fwD/joAkoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAHoAEoAKACgAoAKACgAoAKACgAoAKACgAoAKACgCTY6daAI6ACgAoAKACgAoAKACgAoAKACgAoAKA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th9V3onzLHQB43+0V+0DpXjDS4vA/gtPJ0S1VF+X+OgDoP2Y/jr4O8JeHL3wd41Xy7K6XbQB438dbz4c2fi20vvhXLshT96zf7dAH0r4B+Pvw5+I/g238HfF+Jd1quxZ6AOj03/hlfwBdf8ACR6bc/b7hPmWNqAPkD4//G68+KmveTZt5OkW/wAsUafcoA+cqACgAoAKACgAoAKACgCRfv0ASv8AcoArUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAH8FAELfeNADaACgAoA//1/wD/joAkoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgBD0NAEFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQBZ+fO7dQAlABQAUASb3TpQBHvfd5nzUASb/AJKAI6ACgAoAMP8A36AFV/k2bqAH79n3KAB5qAB3+SgCOgAoAKAF3v8A6ve2ygBNz0ASO+//AFn36AI939ygBd25v3m6gBPZ3oAM/wC1QAUAFAB9+gAoAKAF3f8ALOgBKAJd7/3moAioAkR9n8Pz0AR7noAKAJfOfo5b/doAjd93+xQAlABQAUAFABQAUAFABQBYVP4zQBJQBT/joAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAP4KAIW+8aAG0AFABQB//0PwD/joAkoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgBD0NAEFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQBYoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKALqfcoASgCu336AI6ACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAP4KAIW+8aAG0AFABQB//9H8A/46AJNyUAG5KADclABuSgA3JQAbkoANyUAG5KADclABuSgA3JQAbkoANyUAG5KADclABuSgA3JQAuE3fe9qAJXZFRl9QaAKNABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQBY3JQAbkoANyUAG5KADclABuSgA3JQAbkoANyUAG5KADclABuSgA3JQAbkoANyUAG5KADclABuSgCXMH96gBP3NAC5g/vUAGxP7y0ARYT+/QAbkoANyUAG5KADclABuSgA3JQAbkoANyUAG5KADclABuSgA3JQAbkoANyUAG5KADclABuSgA3JQAbkoANyUAG5KADclAB8lAEmE/v0AS+cn9/8Az+VAB5yf3/8AP5UAV2ZC2Q1ACfJQAbkoANyUAG5KADclABuSgA3JQAbkoANyUAG5KADclABuSgA3JQAbkoANyUAG5KADclABuSgBcJt+97UAQN940ANoAKACgD//0v5/6ACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgD/0/5/6ACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgD/1P5/6ACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgD/1f5/6ACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgD/1v5/6ACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgD/1/5/6ACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgD/0P5/6ACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKAC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oAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgD/0v5/6ACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgD/0/5/6ACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgD/1P5/6ACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgD/1f5/6ACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgD/1v5/6ACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgD/1/5/6ACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgD/0P5/6ACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgD/0f5/6ACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgD/0v5/6ACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgD/0/5/6ACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgD/1P5/6ACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgD/1f5/6ACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgD/1v5/6ACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgD/1/5/6ACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgD/0P5/6ACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgD/0f5/6ACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgD/0v5/6ACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgD/0/5/6ACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgD/1P5/6ACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgD/1f5/6ACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgD/1v5/6ACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgD/1/5/6ACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgD/0P5/6ACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgD/2Q==" style="width:min(480px,85vw);opacity:0;transition:opacity 1s ease" id="splash-logo">
  <div style="margin-top:32px;display:flex;gap:8px" id="splash-dots">
    <div style="width:7px;height:7px;border-radius:50%;background:#c9a84c;animation:sdot 1.2s infinite 0s"></div>
    <div style="width:7px;height:7px;border-radius:50%;background:#c9a84c;animation:sdot 1.2s infinite 0.2s"></div>
    <div style="width:7px;height:7px;border-radius:50%;background:#c9a84c;animation:sdot 1.2s infinite 0.4s"></div>
  </div>
</div>
<style>
@keyframes sdot{0%,80%,100%{transform:scale(0.5);opacity:0.3}40%{transform:scale(1);opacity:1}}
</style>
<script>
(function(){
  var logo = document.getElementById('splash-logo');
  var splash = document.getElementById('splash');
  // Fade in logo
  setTimeout(function(){ logo.style.opacity='1'; }, 100);
  // Ocultar splash cuando la app este lista (minimo 2.5s)
  window._splashReady = false;
  window._hideSplash = function(){
    if(window._splashReady) return;
    window._splashReady = true;
    splash.style.opacity='0';
    setTimeout(function(){ splash.style.display='none'; }, 700);
  };
  setTimeout(function(){ window._hideSplash(); }, 2800);
})();
</script>

<!-- -- LOGIN -- -->
<div id="login-screen">
  <div class="login-box">
    <div class="login-logo">AutomotoraGV</div>
    <div class="login-title">AutomotoraGV</div>
    <div class="login-sub">Sistema de gestion . Inicia sesion</div>
    <div class="lf-group">
      <label>Usuario</label>
      <input id="l-user" placeholder="aacosta / gvillasuso / gyozzi" autocomplete="username" onkeydown="if(event.key==='Enter')doLogin()">
    </div>
    <div class="lf-group">
      <label>Contrasena</label>
      <input id="l-pass" type="password" placeholder="********" autocomplete="current-password" onkeydown="if(event.key==='Enter')doLogin()">
    </div>
    <button class="login-btn" onclick="doLogin()">Ingresar</button>
    <div class="login-err" id="l-err"></div>
  </div>
</div>

<!-- -- APP -- -->
<div id="app">

<!-- SIDEBAR -->
<nav class="sb">
  <div class="sb-top">
    <div class="sb-logo">AutomotoraGV</div>
    <div class="sb-brand">Gestion</div>
    <div class="sb-user">
      <div class="sb-avatar" id="sb-av">?</div>
      <div>
        <div class="sb-uname" id="sb-nombre"></div>
        <div class="sb-rol" id="sb-rol"></div>
      </div>
    </div>
  </div>
  <div class="nav">
    <div class="nl">Principal</div>
    <button class="ni active" onclick="nav('menu',this)" id="nav-menu">
      <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/></svg>
      Menu
    </button>
    <div class="nl">Vehiculos</div>
    <button class="ni" onclick="nav('ventas',this)" id="nav-ventas">
      <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>
      Vendidos
      <span class="badge-cnt" id="cnt-v"></span>
    </button>
    <button class="ni" onclick="nav('compras',this)" id="nav-compras">
      <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 01-8 0"/></svg>
      Comprados
      <span class="badge-cnt" id="cnt-c"></span>
    </button>
    <div class="nl">Personas</div>
    <button class="ni" onclick="nav('clientes',this)" id="nav-clientes">
      <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75"/></svg>
      Clientes
      <span class="badge-cnt" id="cnt-cl"></span>
    </button>
    <div class="nl">Negocio</div>
    <button class="ni" onclick="nav('negocios',this)" id="nav-negocios">
      <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/></svg>
      Negocios
      <span class="badge-cnt" id="cnt-neg"></span>
    </button>
    <button class="ni" onclick="nav('facturacion',this)" id="nav-facturacion">
      <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
      Facturacion
    </button>
    <div class="nl">Inventario</div>
    <button class="ni" onclick="nav('stock',this)" id="nav-stock">
      <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8"/><path d="M10 12h4"/></svg>
      Stock
      <span class="badge-cnt" id="cnt-stk"></span>
    </button>
  </div>
  <div class="sb-bot">
    <button class="sb-logout" onclick="openOv('ov-cambiar-pw')" style="margin-bottom:4px">
      <svg width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>
      Cambiar contrasena
    </button>
    <button class="sb-logout" onclick="doLogout()">
      <svg width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
      Cerrar sesion
    </button>
  </div>
</nav>

<main class="main">

<!-- MENU -->
<div id="page-menu" class="page active">
  <div class="topbar"><div style="display:flex;align-items:center"><div class="topbar-title">AutomotoraGV</div></div>
    <button class="sync-btn" id="sync-btn" onclick="openSync()">
      <svg width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15"/></svg>
      Actualizar desde eFactura
    </button>
  </div>
  <div class="menu-hero">
    <div class="menu-greeting">Bienvenido</div>
    <div class="menu-title">BMW <span>Punta del Este</span></div>
    <div class="menu-sub" id="menu-fecha-sub">Sistema de gestion</div>
    <div class="menu-grid">
      <div class="mc" onclick="nav('clientes',document.getElementById('nav-clientes'))">
        <div class="mc-icon" style="background:var(--gnl)"><svg width="22" height="22" fill="none" stroke="var(--gn)" stroke-width="1.7" viewBox="0 0 24 24"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75"/></svg></div>
        <div><div class="mc-label">Personas</div><div class="mc-name">Clientes</div><div class="mc-desc">Busca por nombre, apellido o documento</div></div>
        <svg class="mc-arrow" width="16" height="16" fill="none" stroke="var(--acc)" stroke-width="2.5" viewBox="0 0 24 24"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
      </div>
      <div class="mc" onclick="nav('ventas',document.getElementById('nav-ventas'))">
        <div class="mc-icon" style="background:var(--bll)"><svg width="22" height="22" fill="none" stroke="var(--bl)" stroke-width="1.7" viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg></div>
        <div><div class="mc-label">Vehiculos</div><div class="mc-name">Autos Vendidos</div><div class="mc-desc">Historial completo de ventas con cliente y chasis</div></div>
        <svg class="mc-arrow" width="16" height="16" fill="none" stroke="var(--acc)" stroke-width="2.5" viewBox="0 0 24 24"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
      </div>
      <div class="mc" onclick="nav('compras',document.getElementById('nav-compras'))">
        <div class="mc-icon" style="background:var(--accl)"><svg width="22" height="22" fill="none" stroke="var(--acc)" stroke-width="1.7" viewBox="0 0 24 24"><path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 01-8 0"/></svg></div>
        <div><div class="mc-label">Inventario</div><div class="mc-name">Autos Comprados</div><div class="mc-desc">Registro de compras por proveedor y modelo</div></div>
        <svg class="mc-arrow" width="16" height="16" fill="none" stroke="var(--acc)" stroke-width="2.5" viewBox="0 0 24 24"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
      </div>
      <div class="mc" onclick="nav('negocios',document.getElementById('nav-negocios'))">
        <div class="mc-icon" style="background:rgba(192,132,252,.1)"><svg width="22" height="22" fill="none" stroke="#c084fc" stroke-width="1.7" viewBox="0 0 24 24"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/></svg></div>
        <div><div class="mc-label">Negocio</div><div class="mc-name">Negocios</div><div class="mc-desc">Gestion de operaciones y cuotas pendientes</div></div>
        <svg class="mc-arrow" width="16" height="16" fill="none" stroke="var(--acc)" stroke-width="2.5" viewBox="0 0 24 24"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
      </div>
      <div class="mc" onclick="nav('stock',document.getElementById('nav-stock'))">
        <div class="mc-icon" style="background:rgba(251,191,36,.1)"><svg width="22" height="22" fill="none" stroke="#fbbf24" stroke-width="1.7" viewBox="0 0 24 24"><path d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8"/><path d="M10 12h4"/></svg></div>
        <div><div class="mc-label">Inventario</div><div class="mc-name">Stock</div><div class="mc-desc">Accesorios, repuestos y movimientos</div></div>
        <svg class="mc-arrow" width="16" height="16" fill="none" stroke="var(--acc)" stroke-width="2.5" viewBox="0 0 24 24"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
      </div>
      <div class="mc" onclick="nav('facturacion',document.getElementById('nav-facturacion'))">
        <div class="mc-icon" style="background:var(--rdl)"><svg width="22" height="22" fill="none" stroke="var(--rd)" stroke-width="1.7" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg></div>
        <div><div class="mc-label">Finanzas</div><div class="mc-name">Facturacion</div><div class="mc-desc">Totales de compras, ventas y sin facturar</div></div>
        <svg class="mc-arrow" width="16" height="16" fill="none" stroke="var(--acc)" stroke-width="2.5" viewBox="0 0 24 24"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
      </div>
    </div>
  </div>
</div>

<!-- VENTAS -->
<div id="page-ventas" class="page">
  <div class="topbar">
    <div style="display:flex;align-items:center"><div class="topbar-title">Vehiculos Vendidos</div><span class="topbar-sub" id="v-total-sub"></span></div>
    <button class="btn pr" onclick="openOv('add-venta')">+ Nueva venta</button>
  </div>
  <div class="content">
    <div class="brand-bar" id="v-brand-bar"></div>
    <div class="tb">
      <div class="sw"><svg width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
        <input id="v-q" placeholder="Buscar cliente, modelo, chasis, motor..." oninput="vPg=1;loadVentas()">
      </div>
      <select class="fi" id="v-m" style="display:none" onchange="vPg=1;loadVentas()"></select>
      <select class="fi" id="v-a" onchange="vPg=1;loadVentas()"><option value="">Todos los anos</option></select>
      <select class="fi" id="v-mn" onchange="vPg=1;loadVentas()"><option value="">USD + UYU</option><option>USD</option><option>UYU</option></select>
      <select class="fi" id="v-ps" onchange="vPg=1;loadVentas()"><option value="20">20/pag</option><option value="30">30/pag</option><option value="100">100/pag</option></select>
    </div>
    <div class="tc">
      <div class="tsc"><table><thead><tr>
        <th>Fecha</th><th>Cliente</th><th>Marca</th><th>Modelo</th><th>Ano</th><th>Motor</th><th>Chasis</th><th>Precio</th><th>No</th><th></th>
      </tr></thead><tbody id="v-body"><tr><td colspan="10"><div class="loading"><div class="loading-spin"></div><br>Cargando...</div></td></tr></tbody></table></div>
      <div class="pag" id="v-pag"></div>
    </div>
  </div>
</div>

<!-- COMPRAS -->
<div id="page-compras" class="page">
  <div class="topbar">
    <div style="display:flex;align-items:center"><div class="topbar-title">Vehiculos Comprados</div><span class="topbar-sub" id="c-total-sub"></span></div>
    <button class="btn pr" onclick="openOv('add-compra')">+ Nueva compra</button>
  </div>
  <div class="content">
    <div class="tb">
      <div class="sw"><svg width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
        <input id="c-q" placeholder="Buscar proveedor, modelo, chasis..." oninput="cPg=1;loadCompras()">
      </div>
      <select class="fi" id="c-m" onchange="cPg=1;loadCompras()"><option value="">Todas las marcas</option></select>
      <select class="fi" id="c-ps" onchange="cPg=1;loadCompras()"><option value="20">20/pag</option><option value="30">30/pag</option><option value="100">100/pag</option></select>
    </div>
    <div class="tc">
      <div class="tsc"><table><thead><tr>
        <th>Fecha</th><th>Proveedor</th><th>Marca</th><th>Modelo</th><th>Chasis / VIN</th><th>Motor</th><th>Precio</th><th></th>
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
      <select class="fi" id="cl-campo" onchange="clPg=1;loadClientes()"><option value="todos">Todos los campos</option><option value="nombre">Nombre / Apellido</option><option value="doc">No Documento</option></select>
      <select class="fi" id="cl-ps" onchange="clPg=1;loadClientes()"><option value="20">20/pag</option><option value="30">30/pag</option><option value="100">100/pag</option></select>
    </div>
    <div class="tc">
      <div class="tsc"><table><thead><tr>
        <th>Nombre</th><th>Documento</th><th>Tipo Doc</th><th>Pais</th><th>Vehiculos</th><th></th>
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

<!-- FACTURACION -->
<div id="page-facturacion" class="page">
  <div class="topbar">
    <div style="display:flex;align-items:center"><div class="topbar-title">Facturacion</div></div>
    <select class="fi" id="fac-mon" onchange="loadFac()"><option value="USD">USD</option><option value="UYU">UYU</option></select>
  </div>
  <div class="content">
    <div class="fac-grid" id="fac-totales"></div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:24px" id="fac-desglose"></div>
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">
      <div style="font-family:var(--fh);font-size:15px;font-weight:700">Vehiculos sin facturar</div>
      <div id="fac-sf-cnt" style="background:var(--rdl);color:var(--rd);font-size:12px;font-family:var(--mo);font-weight:700;padding:3px 12px;border-radius:20px"></div>
    </div>
    <div class="tc">
      <div class="tsc"><table><thead><tr>
        <th>Fecha</th><th>Cliente</th><th>Marca</th><th>Modelo</th><th>Ano</th><th>Chasis</th><th>Precio</th>
      </tr></thead><tbody id="fac-sf-body"></tbody></table></div>
    </div>
  </div>
</div>

<!-- STOCK -->
<div id="page-stock" class="page">
  <div class="topbar">
    <div style="display:flex;align-items:center"><div class="topbar-title">Stock</div><span class="topbar-sub" id="stk-total-sub"></span></div>
    <button class="btn pr" onclick="openOv('add-stock')">+ Agregar item</button>
  </div>
  <div class="content">
    <div class="tb">
      <div class="sw"><svg width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
        <input id="stk-q" placeholder="Buscar nombre, codigo, categoria..." oninput="loadStock()">
      </div>
      <select class="fi" id="stk-cat" onchange="loadStock()"><option value="">Todas las categorias</option><option>Accesorio</option><option>Repuesto</option><option>Lubricante</option><option>Neumatico</option><option>Electronico</option><option>Otro</option></select>
    </div>
    <div class="tc">
      <div class="tsc"><table><thead><tr>
        <th>Codigo</th><th>Nombre</th><th>Categoria</th><th>Compatible con</th><th>Stock</th><th>Precio costo</th><th>Precio venta</th><th>Ubicacion</th><th></th>
      </tr></thead><tbody id="stk-body"></tbody></table></div>
    </div>
  </div>
</div>

</main>
</div><!-- /app -->

<!-- TOAST -->
<div class="toast" id="toast"></div>

<!-- === MODALES === -->

<!-- Add Venta -->
<div class="ov" id="ov-add-venta"><div class="mo-box">
  <div class="mh"><h2>Nueva venta</h2><button class="mc-close" onclick="closeOv('add-venta')"></button></div>
  <div class="mb"><div class="fg">
    <div class="fi-g"><label>Marca</label><input id="av-marca" placeholder="BMW"></div>
    <div class="fi-g"><label>Modelo</label><input id="av-modelo" placeholder="X3 xDrive 30e M Sport"></div>
    <div class="fi-g"><label>Ano</label><input id="av-anio" type="number" placeholder="2025"></div>
    <div class="fi-g"><label>Fecha</label><input id="av-fecha" type="date"></div>
    <div class="fi-g"><label>No Motor</label><input id="av-motor" placeholder="B0427843"></div>
    <div class="fi-g"><label>No Chasis</label><input id="av-chasis" placeholder="WBA65GP03TN357736"></div>
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
  <div class="mh"><h2>Nueva compra</h2><button class="mc-close" onclick="closeOv('add-compra')"></button></div>
  <div class="mb"><div class="fg">
    <div class="fi-g"><label>Marca</label><input id="ac-marca" placeholder="BMW"></div>
    <div class="fi-g"><label>Modelo</label><input id="ac-modelo" placeholder="X1 xDrive 25e"></div>
    <div class="fi-g"><label>Ano</label><input id="ac-anio" type="number" placeholder="2025"></div>
    <div class="fi-g"><label>Fecha</label><input id="ac-fecha" type="date"></div>
    <div class="fi-g"><label>No Motor</label><input id="ac-motor" placeholder="B48A20A"></div>
    <div class="fi-g"><label>No Chasis / VIN</label><input id="ac-chasis" placeholder="WBA21EF0..."></div>
    <div class="fi-g full"><label>Proveedor</label><input id="ac-prov" placeholder="Nombre del proveedor"></div>
    <div class="fi-g"><label>Precio</label><input id="ac-precio" type="number" placeholder="60000"></div>
    <div class="fi-g"><label>Moneda</label><select id="ac-moneda"><option>USD</option><option>UYU</option></select></div>
    <div class="fi-g"><label>Color</label><input id="ac-color" placeholder="Negro"></div>
  </div></div>
  <div class="mf"><button class="btn" onclick="closeOv('add-compra')">Cancelar</button><button class="btn pr" onclick="saveCompra()">Guardar</button></div>
</div></div>

<!-- Add Cliente -->
<div class="ov" id="ov-add-cliente"><div class="mo-box">
  <div class="mh"><h2>Agregar cliente</h2><button class="mc-close" onclick="closeOv('add-cliente')"></button></div>
  <div class="mb"><div class="fg">
    <div class="fi-g full"><label>Nombre completo</label><input id="acl-nombre" placeholder="Nombre completo"></div>
    <div class="fi-g"><label>Documento (CI / RUT)</label><input id="acl-doc" placeholder="12345678"></div>
    <div class="fi-g"><label>Telefono</label><input id="acl-tel" placeholder="099 123 456"></div>
    <div class="fi-g full"><label>Direccion</label><input id="acl-dir" placeholder="Calle y numero"></div>
    <div class="fi-g"><label>Ciudad</label><input id="acl-ciudad" placeholder="Punta del Este"></div>
    <div class="fi-g"><label>Mail</label><input id="acl-mail" placeholder="correo@ejemplo.com"></div>
    <div class="fi-g"><label>Relacion</label><select id="acl-rel"><option>Cliente</option><option>Proveedor</option><option>Cliente/Proveedor</option></select></div>
  </div></div>
  <div class="mf"><button class="btn" onclick="closeOv('add-cliente')">Cancelar</button><button class="btn pr" onclick="saveCliente()">Guardar</button></div>
</div></div>

<!-- Add Negocio -->
<div class="ov" id="ov-add-negocio"><div class="mo-box wide">
  <div class="mh"><h2>Nuevo negocio</h2><button class="mc-close" onclick="closeOv('add-negocio')"></button></div>
  <div class="mb"><div class="fg">
    <div class="fi-g full"><label>Cliente</label><input id="an-cliente" placeholder="Nombre del cliente"></div>
    <div class="fi-g"><label>Marca vehiculo</label><input id="an-marca" placeholder="BMW"></div>
    <div class="fi-g"><label>Modelo</label><input id="an-modelo" placeholder="X3 xDrive 30e M Sport"></div>
    <div class="fi-g"><label>Ano</label><input id="an-anio" type="number" placeholder="2025"></div>
    <div class="fi-g"><label>Chasis / VIN</label><input id="an-chasis" placeholder="WBA65GP..."></div>
    <div class="fi-g"><label>Precio venta</label><input id="an-precio" type="number" placeholder="85000"></div>
    <div class="fi-g"><label>Moneda</label><select id="an-moneda"><option>USD</option><option>UYU</option></select></div>
    <div class="fi-g"><label>Metodo de pago</label><select id="an-metodo">
      <option value="contado">Contado</option>
      <option value="financiado">Financiado</option>
      <option value="leasing">Leasing</option>
      <option value="permuta">Permuta</option>
      <option value="credito">Credito bancario</option>
      <option value="cuotas">Cuotas directas</option>
    </select></div>
    <div class="fi-g"><label>Fecha negocio</label><input id="an-fecha" type="date"></div>
    <div class="fi-g"><label>No Cuotas (0 = pago unico)</label><input id="an-cuotas" type="number" value="0" min="0" oninput="toggleCuotas()"></div>
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
  <div class="mh"><h2>Agregar item al stock</h2><button class="mc-close" onclick="closeOv('add-stock')"></button></div>
  <div class="mb"><div class="fg">
    <div class="fi-g"><label>Codigo</label><input id="as-codigo" placeholder="BMW-ACC-001"></div>
    <div class="fi-g"><label>Categoria</label><select id="as-cat"><option>Accesorio</option><option>Repuesto</option><option>Lubricante</option><option>Neumatico</option><option>Electronico</option><option>Otro</option></select></div>
    <div class="fi-g full"><label>Nombre</label><input id="as-nombre" placeholder="Nombre del producto"></div>
    <div class="fi-g"><label>Marca compatible</label><input id="as-marca" placeholder="BMW"></div>
    <div class="fi-g"><label>Modelo compatible</label><input id="as-modelo" placeholder="X3, X5, Serie 3..."></div>
    <div class="fi-g"><label>Cantidad inicial</label><input id="as-cant" type="number" value="0" min="0"></div>
    <div class="fi-g"><label>Precio costo</label><input id="as-costo" type="number" placeholder="0"></div>
    <div class="fi-g"><label>Precio venta</label><input id="as-venta" type="number" placeholder="0"></div>
    <div class="fi-g"><label>Moneda</label><select id="as-moneda"><option>USD</option><option>UYU</option></select></div>
    <div class="fi-g"><label>Ubicacion</label><input id="as-ubic" placeholder="Estante A-3"></div>
    <div class="fi-g full"><label>Notas</label><input id="as-notas" placeholder="Observaciones..."></div>
  </div></div>
  <div class="mf"><button class="btn" onclick="closeOv('add-stock')">Cancelar</button><button class="btn pr" onclick="saveStock()">Guardar</button></div>
</div></div>

<!-- Detalle generico -->
<div class="ov" id="ov-detail"><div class="mo-box">
  <div class="mh"><h2 id="det-t">Detalle</h2><button class="mc-close" onclick="closeOv('detail')"></button></div>
  <div class="mb" id="det-b"></div>
  <div class="mf"><button class="btn pr" onclick="closeOv('detail')">Cerrar</button></div>
</div></div>

<!-- Detalle Negocio + Cuotas -->
<div class="ov" id="ov-det-neg"><div class="mo-box wide">
  <div class="mh"><h2 id="detneg-t">Negocio</h2><button class="mc-close" onclick="closeOv('det-neg')"></button></div>
  <div class="mb" id="detneg-b"></div>
  <div class="mf">
    <button class="btn danger" id="btn-cerrar-neg" onclick="cerrarNegocio()">Marcar cerrado</button>
    <button class="btn pr" onclick="closeOv('det-neg')">Cerrar</button>
  </div>
</div></div>

<!-- Movimiento Stock -->
<div class="ov" id="ov-mov-stock"><div class="mo-box" style="width:380px">
  <div class="mh"><h2>Movimiento de stock</h2><button class="mc-close" onclick="closeOv('mov-stock')"></button></div>
  <div class="mb"><div class="fg">
    <div class="fi-g full"><label>Producto</label><input id="ms-nombre" readonly style="background:var(--bg4);color:var(--tx3)"></div>
    <div class="fi-g"><label>Tipo</label><select id="ms-tipo"><option value="entrada">Entrada</option><option value="salida">Salida</option></select></div>
    <div class="fi-g"><label>Cantidad</label><input id="ms-cant" type="number" value="1" min="1"></div>
    <div class="fi-g full"><label>Motivo</label><input id="ms-motivo" placeholder="Ej: Venta a cliente, compra a proveedor..."></div>
  </div></div>
  <div class="mf"><button class="btn" onclick="closeOv('mov-stock')">Cancelar</button><button class="btn pr" onclick="saveMovStock()">Confirmar</button></div>
</div></div>

<!-- Cambiar contrasena -->
<div class="ov" id="ov-cambiar-pw"><div class="mo-box" style="width:400px">
  <div class="mh"><h2>Cambiar contrasena</h2><button class="mc-close" onclick="closeOv('cambiar-pw')"></button></div>
  <div class="mb">
    <div class="fi-g full"><label>Contrasena actual</label><input type="password" id="cp-actual" placeholder="********" autocomplete="current-password"></div>
    <div class="fi-g full"><label>Nueva contrasena</label><input type="password" id="cp-nueva" placeholder="Minimo 6 caracteres" autocomplete="new-password"></div>
    <div class="fi-g full"><label>Confirmar nueva contrasena</label><input type="password" id="cp-confirma" placeholder="Repeti la nueva contrasena" autocomplete="new-password"></div>
  </div>
  <div class="mf">
    <button class="btn" onclick="closeOv('cambiar-pw')">Cancelar</button>
    <button class="btn pr" onclick="doCambiarPw()">Actualizar contrasena</button>
  </div>
</div></div>


<div class="ov" id="ov-sync"><div class="mo-box" style="width:520px">
  <div class="mh"><h2>Actualizar desde eFactura</h2><button class="mc-close" onclick="closeOv('sync')"></button></div>
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
    <button class="btn pr" id="sync-run-btn" onclick="runSync()">Iniciar sincronizacion</button>
  </div>
</div></div>

<script>
const API = window.location.origin;
let TOKEN = localStorage.getItem('bmw_token') || '';
let ME = JSON.parse(localStorage.getItem('bmw_me') || 'null');

// -- UTILS --
function esc(s){return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;')}
function fmt(n,mon='USD'){if(!n&&n!==0)return '';return(mon==='USD'?'U$S ':'$U ')+Number(n).toLocaleString('es-UY',{minimumFractionDigits:0,maximumFractionDigits:0})}
function fdate(d){return d?d.substring(0,10):''}

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


function toggleSidebar() {
  const sb = document.getElementById('sidebar');
  const ov = document.getElementById('sidebar-overlay');
  sb.classList.toggle('open');
  ov.classList.toggle('open');
}
// Cerrar sidebar al navegar en mobile
const _origShowSection = typeof showSection === 'function' ? showSection : null;

function initials(n){const w=(n||'').trim().split(/\s+/);return((w[0]?.[0]||'')+(w[1]?.[0]||'')).toUpperCase()}
function celTd(v,title=''){return`<td style="max-width:150px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="${esc(title||v)}">${esc(v)}</td>`}

const BRAND_COLORS={
  'BMW':['#1a2a4a','#6ba3ff'],'MINI':['#2a1a0a','#ffb86c'],'VOLVO':['#0a2a1a','#4ade80'],
  'MAZDA':['#2a0a0a','#ff6b6b'],'RANGE ROVER':['#1a0a2a','#c084fc'],'LAND ROVER':['#0a1a2a','#60a5fa'],
  'JAGUAR':['#002a20','#34d399'],'MERCEDES BENZ':['#0a1520','#93c5fd'],'AUDI':['#2a1500','#fbbf24'],
  'FERRARI':['#2a0000','#ff4444'],'PORSCHE':['#2a1000','#fb923c'],'VOLKSWAGEN':['#000a2a','#818cf8'],
};
function bb(m){if(!m)return'<span class="badge" style="background:var(--bg4);color:var(--tx3)"></span>';const c=BRAND_COLORS[m]||['#1a1a1a','#888'];return`<span class="badge" style="background:${c[0]};color:${c[1]}">${esc(m)}</span>`}

function renderPag(prefix, page, totalPages, total, from, ps, loadFn){
  const el=document.getElementById(prefix+'-pag');
  if(!el)return;
  const to=Math.min(from+ps,total);
  if(totalPages<=1){el.innerHTML=`<span class="pi">${total} registros</span><div></div>`;return}
  let btns='';
  for(let i=1;i<=totalPages;i++){
    if(i===1||i===totalPages||(i>=page-2&&i<=page+2))btns+=`<button class="pb${i===page?' ac':''}" onclick="${loadFn}(${i})">${i}</button>`;
    else if(i===page-3||i===page+3)btns+=`<span style="padding:3px 4px;color:var(--tx3)">...</span>`;
  }
  el.innerHTML=`<span class="pi">${from+1}${to} de ${total}</span><div class="pbs">${btns}</div>`;
}

// -- AUTH --
async function doLogin(){ if(window._hideSplash) window._hideSplash();
  const u=document.getElementById('l-user').value.trim();
  const p=document.getElementById('l-pass').value;
  document.getElementById('l-err').textContent='';
  try{
    const r=await fetch(API+'/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:u,password:p})});
    const data=await r.json();
    if(!r.ok){document.getElementById('l-err').textContent=data.error||'Error al iniciar sesion';return}
    TOKEN=data.token; ME=data;
    localStorage.setItem('bmw_token',TOKEN);
    localStorage.setItem('bmw_me',JSON.stringify(ME));
    showApp();
  }catch(e){document.getElementById('l-err').textContent='No se pudo conectar al servidor'}
}

function doLogout(){
  TOKEN=''; ME=null;
  localStorage.removeItem('bmw_token');
  localStorage.removeItem('bmw_me');
  document.getElementById('app').style.display='none';
  document.getElementById('login-screen').style.display='flex';
}

async function doCambiarPw(){
  const actual=document.getElementById('cp-actual').value;
  const nueva=document.getElementById('cp-nueva').value;
  const confirma=document.getElementById('cp-confirma').value;
  if(!actual||!nueva){toast('Completa todos los campos','err');return;}
  if(nueva!==confirma){toast('Las contrasenas no coinciden','err');return;}
  if(nueva.length<6){toast('Minimo 6 caracteres','err');return;}
  try{
    await api('/api/change-password',{method:'POST',body:JSON.stringify({current_password:actual,new_password:nueva})});
    toast('Contrasena actualizada ');
    closeOv('cambiar-pw');
    document.getElementById('cp-actual').value='';
    document.getElementById('cp-nueva').value='';
    document.getElementById('cp-confirma').value='';
  }catch(e){toast(e.message||'Error al cambiar contrasena','err');}
}


async function showApp(){ if(window._hideSplash) window._hideSplash();
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

// Al cargar, si hay token valido, mostrar app
window.addEventListener('load',async()=>{
  if(TOKEN&&ME){
    try{const me=await api('/api/me');if(me)showApp();else doLogout();}catch(e){showApp();}
  }
});

// -- NAVEGACION --
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

// -- VENTAS --
let vPg=1, vBrandFilter='', vData=[], vBrandBuilt=false;

async function loadVentas(page){
  if(page)vPg=page;
  const PS=50;
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

    // Filtrar ano/moneda client-side
    let data=res.data;
    if(anio)data=data.filter(v=>String(v.anio)===anio);
    if(moneda)data=data.filter(v=>v.moneda===moneda);

    // Anos dropdown
    if(!anio){
      const years=[...new Set(vData.filter(v=>v.anio).map(v=>v.anio))].sort((a,b)=>b-a);
      const sa=document.getElementById('v-a'),cur=sa.value;
      sa.innerHTML='<option value="">Todos los anos</option>'+years.map(y=>`<option${y==cur?' selected':''}>${y}</option>`).join('');
    }

    // Brand bar (solo primera vez)
    if(!vBrandBuilt){buildBrandBar(res.data);vBrandBuilt=true;}

    const tot=res.total, tp=Math.ceil(tot/PS)||1;
    document.getElementById('v-body').innerHTML=data.length?data.map((v,i)=>`<tr>
      <td style="white-space:nowrap;font-family:var(--mo);font-size:12px;color:var(--tx3)">${fdate(v.fecha)}</td>
      ${celTd(v.cliente||'',v.cliente)}
      <td>${bb(v.marca)}</td>
      ${celTd(v.modelo||'',v.modelo)}
      <td style="color:var(--tx3);font-family:var(--mo);font-size:12px">${v.anio||''}</td>
      <td class="mo" style="max-width:120px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="${esc(v.motor)}">${esc(v.motor||'')}</td>
      <td class="mo" style="color:var(--acc2);max-width:150px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="${esc(v.chasis)}">${esc(v.chasis||'')}</td>
      <td class="pr-val" style="white-space:nowrap">${fmt(v.precio,v.moneda)}</td>
      <td class="mo" style="white-space:nowrap;color:var(--tx3);font-size:11px">${v.comprobante||''}</td>
      <td><button class="btn sm" onclick="detVenta(${v.id})">Ver</button></td>
    </tr>`).join(''):`<tr><td colspan="10"><div class="empty"><div class="empty-icon"></div>Sin resultados</div></td></tr>`;
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
    ['Comprobante',`<span class="mo">${esc(v.comprobante||'')}</span>`],
    ['Fecha',fdate(v.fecha)],['Cliente',`<strong>${esc(v.cliente||'')}</strong>`],
    ['Documento',`<span class="mo">${v.cliente_doc||''}</span>`],
    ['Marca',bb(v.marca)],['Modelo',esc(v.modelo||'')],['Ano',v.anio||''],
    ['No Motor',`<span class="mo" style="color:var(--acc2)">${esc(v.motor||'')}</span>`],
    ['No Chasis',`<span class="mo" style="color:var(--acc2)">${esc(v.chasis||'')}</span>`],
    ['Precio',`<span class="pr-val">${fmt(v.precio,v.moneda)}</span>`],
  ].map(([l,val])=>`<div class="dr"><span class="dl">${l}</span><span class="dv">${val}</span></div>`).join('');
  openOv('detail');
}

async function saveVenta(){
  const v={comprobante:document.getElementById('av-comp').value.trim(),fecha:document.getElementById('av-fecha').value,marca:document.getElementById('av-marca').value.trim().toUpperCase(),modelo:document.getElementById('av-modelo').value.trim().toUpperCase(),anio:parseInt(document.getElementById('av-anio').value)||null,motor:document.getElementById('av-motor').value.trim().toUpperCase(),chasis:document.getElementById('av-chasis').value.trim().toUpperCase(),cliente:document.getElementById('av-cliente').value.trim(),cliente_doc:document.getElementById('av-cliente-doc').value.trim(),precio:parseFloat(document.getElementById('av-precio').value)||0,moneda:document.getElementById('av-moneda').value};
  if(!v.marca||!v.cliente){toast('Marca y cliente son requeridos','err');return}
  try{await api('/api/ventas',{method:'POST',body:JSON.stringify(v)});closeOv('add-venta');toast('Venta guardada ');loadVentas();}catch(e){toast('Error: '+e.message,'err')}
}

// -- COMPRAS --
let cPg=1, cData=[];
async function loadCompras(page){
  if(page)cPg=page;
  const PS=50;
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
      ${celTd(c.proveedor||'',c.proveedor)}
      <td>${bb(c.marca)}</td>
      ${celTd(c.modelo||c.detalle_original||'',c.modelo||c.detalle_original||'')}
      <td class="mo" style="max-width:110px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${esc(c.motor||'')}</td>
      <td class="mo" style="color:var(--acc2);max-width:150px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="${esc(c.chasis)}">${esc(c.chasis||'')}</td>
      <td class="pr-val" style="white-space:nowrap">${fmt(c.precio,c.moneda)}</td>
      <td><button class="btn sm" onclick="detCompra(${c.id})">Ver</button></td>
    </tr>`).join(''):`<tr><td colspan="9"><div class="empty"><div class="empty-icon"></div>Sin resultados</div></td></tr>`;
    renderPag('c',cPg,tp,tot,(cPg-1)*PS,PS,'loadCompras');
  }catch(e){toast('Error cargando compras','err')}
}
async function detCompra(id){
  const c=cData.find(x=>x.id===id)||{};
  document.getElementById('det-t').textContent=(c.marca||'')+' '+(c.modelo||'');
  document.getElementById('det-b').innerHTML=[
    ['Fecha',fdate(c.fecha)],['Proveedor',`<strong>${esc(c.proveedor||'')}</strong>`],
    ['Marca',bb(c.marca)],['Modelo',esc(c.modelo||'')],['Ano',c.anio||''],
    ['No Motor',`<span class="mo" style="color:var(--acc2)">${esc(c.motor||'')}</span>`],
    ['No Chasis',`<span class="mo" style="color:var(--acc2)">${esc(c.chasis||'')}</span>`],
    ['Color',c.color||''],['Precio',`<span class="pr-val">${fmt(c.precio,c.moneda)}</span>`],
  ].map(([l,v])=>`<div class="dr"><span class="dl">${l}</span><span class="dv">${v}</span></div>`).join('');
  openOv('detail');
}
async function saveCompra(){
  const v={fecha:document.getElementById('ac-fecha').value,marca:document.getElementById('ac-marca').value.trim().toUpperCase(),modelo:document.getElementById('ac-modelo').value.trim().toUpperCase(),anio:parseInt(document.getElementById('ac-anio').value)||null,motor:document.getElementById('ac-motor').value.trim().toUpperCase(),chasis:document.getElementById('ac-chasis').value.trim().toUpperCase(),proveedor:document.getElementById('ac-prov').value.trim(),precio:parseFloat(document.getElementById('ac-precio').value)||0,moneda:document.getElementById('ac-moneda').value,color:document.getElementById('ac-color').value.trim()};
  if(!v.marca||!v.proveedor){toast('Marca y proveedor son requeridos','err');return}
  try{await api('/api/compras',{method:'POST',body:JSON.stringify(v)});closeOv('add-compra');toast('Compra guardada ');loadCompras();}catch(e){toast('Error: '+e.message,'err')}
}

// -- CLIENTES --
let clPg=1, clData=[];
async function loadClientes(page){
  if(page)clPg=page;
  const PS=50;
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
        <td style="font-weight:600;white-space:nowrap">${esc(cl.nombre||'')}</td>
        <td><span style="background:var(--accl);color:var(--acc);padding:2px 9px;border-radius:20px;font-family:var(--mo);font-size:11px">${esc(cl.doc||'')}</span></td>
        ${celTd(cl.tipo_doc||'--',cl.tipo_doc)}
        ${celTd(cl.pais||'--',cl.pais)}
        ${celTd(cl.tipo_doc||'',cl.tipo_doc)}
        ${celTd(cl.pais||'',cl.pais)}
        
        
        
        
        <td>${nv>0?`<span class="badge" style="background:var(--gnl);color:var(--gn)">${nv} veh.</span>`:'<span style="color:var(--tx3)"></span>'}</td>
        <td><button class="btn sm" onclick="detCliente(${cl.id})">Ver</button></td>
      </tr>`;
    }).join(''):`<tr>
      <td style="padding:6px 8px;border-bottom:1px solid var(--bd)">${bb(v.marca)}</td>
      <td style="padding:6px 8px;max-width:130px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;border-bottom:1px solid var(--bd)">${esc(v.modelo||'')}</td>
      <td style="padding:6px 8px;font-family:var(--mo);font-size:11px;color:var(--acc2);border-bottom:1px solid var(--bd)">${esc(v.chasis||'')}</td>
      <td style="padding:6px 8px;font-family:var(--mo);font-size:12px;color:var(--acc2);border-bottom:1px solid var(--bd)">${fmt(v.precio,v.moneda)}</td>
    </tr>`).join('')}</tbody></table></div>`:''}`;
  openOv('detail');
}
async function saveCliente(){
  const v={nombre:document.getElementById('acl-nombre').value.trim().toUpperCase(),doc:document.getElementById('acl-doc').value.trim(),telefono:document.getElementById('acl-tel').value.trim(),direccion:document.getElementById('acl-dir').value.trim(),ciudad:document.getElementById('acl-ciudad').value.trim().toUpperCase(),mail:document.getElementById('acl-mail').value.trim(),relacion:document.getElementById('acl-rel').value};
  if(!v.nombre){toast('El nombre es requerido','err');return}
  try{await api('/api/clientes',{method:'POST',body:JSON.stringify(v)});closeOv('add-cliente');toast('Cliente guardado ');loadClientes();}catch(e){toast('Error: '+e.message,'err')}
}

// -- NEGOCIOS --
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
      const metodoLabel={'contado':'Contado','financiado':'Financiado','leasing':'Leasing','permuta':'Permuta','credito':'Credito bancario','cuotas':'Cuotas directas'}[n.metodo_pago]||n.metodo_pago||'';
      return`<div class="neg-card" onclick="detNegocio(${n.id})">
        <div class="neg-card-header">
          <div>
            <div class="neg-cliente">${esc(n.cliente_nombre||'')}</div>
            <div class="neg-vehiculo">${esc([n.vehiculo_marca,n.vehiculo_modelo,n.vehiculo_anio].filter(Boolean).join(' '))}</div>
          </div>
          <div style="text-align:right">
            <div class="pr-val">${fmt(n.precio_venta,n.moneda)}</div>
            <div style="font-size:11px;color:var(--tx3);margin-top:2px">${metodoLabel}</div>
          </div>
        </div>
        <div class="neg-metas">
          <span class="neg-meta"> ${fdate(n.fecha_negocio)}</span>
          ${n.vehiculo_chasis?`<span class="neg-meta mo" style="font-size:11px">${esc(n.vehiculo_chasis)}</span>`:''}
          <span class="badge" style="background:${n.estado==='activo'?'var(--gnl)':'var(--bg4)'};color:${n.estado==='activo'?'var(--gn)':'var(--tx3)'}">${n.estado}</span>
          ${n.usuario_nombre?`<span class="neg-meta"> ${esc(n.usuario_nombre)}</span>`:''}
        </div>
        ${tot>0?`<div class="neg-cuotas-bar">
          <div class="neg-cuotas-label"><span>Cuotas</span><span>${tot-pend}/${tot} pagadas</span></div>
          <div class="neg-cuotas-track"><div class="neg-cuotas-fill" style="width:${pct}%"></div></div>
        </div>`:''}
      </div>`;
    }).join(''):`<div class="empty"><div class="empty-icon"></div>Sin negocios registrados</div>`;
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
      ${c.pagada?`<span class="cuota-pagada"> Pagada</span>`:
        c.fecha_vencimiento<hoy?`<span class="cuota-vencida"> Vencida</span><button class="btn sm" onclick="pagarCuota(${c.id},event)">Pagar</button>`:
        `<button class="btn sm" onclick="pagarCuota(${c.id},event)">Pagar</button>`}
    </div>`).join('')}</div>`;
  }
  document.getElementById('detneg-b').innerHTML=[
    ['Cliente',`<strong>${esc(n.cliente_nombre||'')}</strong>`],
    ['Vehiculo',esc([n.vehiculo_marca,n.vehiculo_modelo,n.vehiculo_anio].filter(Boolean).join(' '))],
    ['Chasis',`<span class="mo" style="color:var(--acc2)">${esc(n.vehiculo_chasis||'')}</span>`],
    ['Precio',`<span class="pr-val">${fmt(n.precio_venta,n.moneda)}</span>`],
    ['Metodo',n.metodo_pago||''],['Fecha',fdate(n.fecha_negocio)],
    ['Estado',`<span class="badge" style="background:${n.estado==='activo'?'var(--gnl)':'var(--bg4)'};color:${n.estado==='activo'?'var(--gn)':'var(--tx3)'}">${n.estado}</span>`],
    ['Notas',n.notas||''],
  ].map(([l,v])=>`<div class="dr"><span class="dl">${l}</span><span class="dv">${v}</span></div>`).join('')+cuotasHtml;
  document.getElementById('btn-cerrar-neg').style.display=n.estado==='activo'?'':'none';
  openOv('det-neg');
}

async function pagarCuota(cid,e){
  e.stopPropagation();
  try{await api('/api/cuotas/pagar',{method:'POST',body:JSON.stringify({cuota_id:cid})});toast('Cuota marcada como pagada ');detNegocio(negDetId);}catch(e){toast('Error','err')}
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
  try{await api('/api/negocios',{method:'POST',body:JSON.stringify(v)});closeOv('add-negocio');toast('Negocio guardado ');loadNegocios();}catch(e){toast('Error: '+e.message,'err')}
}

// -- FACTURACION --
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
      <div class="fac-card v"><div class="fc-label">Total Ventas</div><div class="fc-val" style="color:var(--bl)">${fmt(tV,mon)}</div><div class="fc-sub">${ventas.length} vehiculos . ${mon}</div></div>
      <div class="fac-card c"><div class="fc-label">Total Compras</div><div class="fc-val" style="color:var(--acc2)">${fmt(tC,mon)}</div><div class="fc-sub">${compras.length} vehiculos . ${mon}</div></div>
      <div class="fac-card s"><div class="fc-label">Diferencia</div><div class="fc-val" style="color:${saldo>=0?'var(--gn)':'var(--rd)'}">${fmt(Math.abs(saldo),mon)}</div><div class="fc-sub">${saldo>=0?'Resultado positivo':'Resultado negativo'}</div></div>`;
    // Desglose por marca
    const mv={},mc={};
    ventas.forEach(v=>{if(v.marca)mv[v.marca]=(mv[v.marca]||0)+v.precio});
    compras.forEach(c=>{if(c.marca)mc[c.marca]=(mc[c.marca]||0)+c.precio});
    const mkV=Object.entries(mv).sort((a,b)=>b[1]-a[1]);
    const mkC=Object.entries(mc).sort((a,b)=>b[1]-a[1]);
    document.getElementById('fac-desglose').innerHTML=`
      <div style="background:var(--bg2);border:1px solid var(--bd);border-radius:var(--rl);padding:18px 20px">
        <div style="font-family:var(--fh);font-size:11px;font-weight:700;color:var(--tx3);text-transform:uppercase;letter-spacing:1px;margin-bottom:14px">Ventas por marca . ${mon}</div>
        ${mkV.map(([m,v])=>`<div style="display:flex;justify-content:space-between;align-items:center;padding:7px 0;border-bottom:1px solid var(--bd);font-size:13px"><span style="color:var(--tx2)">${esc(m)}</span><span style="font-family:var(--mo);font-weight:600;color:var(--bl)">${fmt(v,mon)}</span></div>`).join('')}
      </div>
      <div style="background:var(--bg2);border:1px solid var(--bd);border-radius:var(--rl);padding:18px 20px">
        <div style="font-family:var(--fh);font-size:11px;font-weight:700;color:var(--tx3);text-transform:uppercase;letter-spacing:1px;margin-bottom:14px">Compras por marca . ${mon}</div>
        ${mkC.map(([m,v])=>`<div style="display:flex;justify-content:space-between;align-items:center;padding:7px 0;border-bottom:1px solid var(--bd);font-size:13px"><span style="color:var(--tx2)">${esc(m)}</span><span style="font-family:var(--mo);font-weight:600;color:var(--acc2)">${fmt(v,mon)}</span></div>`).join('')}
      </div>`;
    // Sin facturar
    const sf=vs.data.filter(v=>!v.comprobante||v.comprobante.trim()==='');
    document.getElementById('fac-sf-cnt').textContent=sf.length+' sin facturar';
    document.getElementById('fac-sf-body').innerHTML=sf.length?sf.map(v=>`<tr>
      <td style="white-space:nowrap;font-family:var(--mo);font-size:12px;color:var(--tx3)">${fdate(v.fecha)}</td>
      ${celTd(v.cliente||'',v.cliente)}<td>${bb(v.marca)}</td>${celTd(v.modelo||'',v.modelo)}
      <td style="font-family:var(--mo);font-size:12px;color:var(--tx3)">${v.anio||''}</td>
      <td class="mo" style="color:var(--acc2)">${esc(v.chasis||'')}</td>
      <td class="pr-val">${fmt(v.precio,v.moneda)}</td>
    </tr>`).join(''):`<tr><td colspan="7"><div class="empty"><div class="empty-icon"></div>Sin vehiculos pendientes</div></td></tr>`;
  }catch(e){toast('Error cargando facturacion','err')}
}

// -- STOCK --
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
        <td class="mo" style="font-size:11px;color:var(--tx3)">${esc(s.codigo||'')}</td>
        ${celTd(s.nombre,'')}<td><span class="badge" style="background:var(--bg4);color:var(--tx2)">${esc(s.categoria||'')}</span></td>
        ${celTd([s.marca_compatible,s.modelo_compatible].filter(Boolean).join(' . '),'')}
        <td><span style="font-family:var(--mo);font-size:13px;font-weight:700;color:${bajo?'var(--rd)':'var(--gn)'}">${s.cantidad}</span></td>
        <td class="pr-val">${fmt(s.precio_costo,s.moneda)}</td>
        <td class="pr-val">${fmt(s.precio_venta,s.moneda)}</td>
        ${celTd(s.ubicacion||'','')}
        <td style="white-space:nowrap"><button class="btn sm" onclick="openMovStock(${s.id})"></button></td>
      </tr>`;
    }).join(''):`<tr><td colspan="9"><div class="empty"><div class="empty-icon"></div>Sin items en stock</div></td></tr>`;
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
  try{await api('/api/stock/movimiento',{method:'POST',body:JSON.stringify(v)});closeOv('mov-stock');toast('Movimiento registrado ');loadStock();}catch(e){toast('Error','err')}
}
async function saveStock(){
  const v={codigo:document.getElementById('as-codigo').value.trim(),nombre:document.getElementById('as-nombre').value.trim(),categoria:document.getElementById('as-cat').value,marca_compatible:document.getElementById('as-marca').value.trim(),modelo_compatible:document.getElementById('as-modelo').value.trim(),cantidad:parseInt(document.getElementById('as-cant').value)||0,precio_costo:parseFloat(document.getElementById('as-costo').value)||0,precio_venta:parseFloat(document.getElementById('as-venta').value)||0,moneda:document.getElementById('as-moneda').value,ubicacion:document.getElementById('as-ubic').value.trim(),notas:document.getElementById('as-notas').value.trim()};
  if(!v.nombre){toast('El nombre es requerido','err');return}
  try{await api('/api/stock',{method:'POST',body:JSON.stringify(v)});closeOv('add-stock');toast('Item guardado ');loadStock();}catch(e){toast('Error: '+e.message,'err')}
}

// -- SYNC eFactura --
function openSync(){
  document.getElementById('sync-log').style.display='none';
  document.getElementById('sync-log').innerHTML='';
  document.getElementById('sync-status').textContent='Listo para sincronizar';
  document.getElementById('sync-prog-fill').style.width='0%';
  document.getElementById('sync-run-btn').disabled=false;
  document.getElementById('sync-run-btn').textContent='Iniciar sincronizacion';
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
  syncLog('Iniciando sincronizacion...');

  // Verificar si eFactura esta abierto en el browser
  try{
    // Intentar leer datos de los JSONs locales (rebuild)
    document.getElementById('sync-status').textContent='Leyendo datos actuales...';
    document.getElementById('sync-prog-fill').style.width='20%';

    // Si tiene acceso a los JSONs locales, reimportar
    // En este contexto el servidor puede leer los JSONs directamente
    const payload={};
    let steps=0, total=(doVentas?1:0)+(doCompras?1:0)+(doClientes?1:0);

    if(doVentas){
      syncLog(' Leyendo ventas_full.json...');
      document.getElementById('sync-prog-fill').style.width=Math.round(20+steps/total*60)+'%';
      payload.tipo='ventas';
      steps++;
    }
    if(doCompras){
      syncLog(' Leyendo compras_full.json...');
      document.getElementById('sync-prog-fill').style.width=Math.round(20+steps/total*60)+'%';
      payload.tipo='compras';
      steps++;
    }
    if(doClientes){
      syncLog(' Leyendo clientes_full.json...');
      document.getElementById('sync-prog-fill').style.width=Math.round(20+steps/total*60)+'%';
      payload.tipo='clientes';
      steps++;
    }

    // Llamar al endpoint de reimport
    payload.tipo='all';
    const res=await api('/api/sync/reimport',{method:'POST',body:JSON.stringify({ventas:doVentas,compras:doCompras,clientes:doClientes})});

    document.getElementById('sync-prog-fill').style.width='100%';
    if(res){
      syncLog(` Ventas: ${res.ventas_nuevas||0} nuevas (${res.ventas_total||0} total)`,'ok');
      syncLog(` Compras: ${res.compras_nuevas||0} nuevas (${res.compras_total||0} total)`,'ok');
      syncLog(` Clientes: ${res.clientes_nuevas||0} nuevos (${res.clientes_total||0} total)`,'ok');
      syncLog(' Sincronizacion completada','ok');
      document.getElementById('sync-status').textContent='Completado';
      toast('Sincronizacion completada ');
      // Actualizar stats
      showApp();
    }
    btn.textContent='Completado';
  }catch(e){
    syncLog(' Error: '+e.message,'err');
    document.getElementById('sync-status').textContent='Error en sincronizacion';
    btn.disabled=false;btn.textContent='Reintentar';
    toast('Error en sincronizacion','err');
  }
}

</script>
</body>
</html>
"""


# -- CONFIG ----------------------------------------------
PORT = int(os.environ.get('PORT', 8765))
_db_dir = '/data' if os.path.isdir('/data') else os.path.join(os.path.dirname(__file__), 'db')
DB_PATH = os.path.join(_db_dir, 'bmw.db')
SECRET_KEY = os.environ.get('SECRET_KEY', 'bmw_punta_del_este_2026_secret_key_mofidec_sa')
TOKEN_EXPIRY_HOURS = 8

# Rate limiting para login
_login_attempts = {}  # ip -> [timestamp, count]

# -- JWT SIMPLE (sin dependencias) -----------------------
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

# -- BASE DE DATOS ----------------------------------------
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
        ('aacosta',    'A. Acosta',    'BMW2026!', 'admin'),
        ('gvillasuso', 'G. Villasuso', 'BMW2026!', 'admin'),
        ('gyozzi',     'G. Yozzi',     'BMW2026!', 'admin'),
    ]
    for username, nombre, pw, rol in usuarios_default:
        try:
            c.execute("INSERT INTO usuarios (username,nombre,password_hash,rol) VALUES (?,?,?,?)",
                     (username, nombre, hash_password(pw), rol))
        except sqlite3.IntegrityError:
            pass

    conn.commit()
    conn.close()
    print(f" Base de datos inicializada: {DB_PATH}")

# -- IMPORTAR DATOS EXISTENTES ----------------------------
def import_json_data():
    base = os.path.dirname(__file__)
    conn = get_db()
    c = conn.cursor()

    # Verificar si ya hay datos
    count = c.execute("SELECT COUNT(*) FROM ventas").fetchone()[0]
    if count > 0:
        print(f" Datos ya importados ({count} ventas)")
        conn.close()
        return

    # Importar ventas
    ventas_path = os.path.join(base, 'ventas_full.json')
    if os.path.exists(ventas_path):
        with open(ventas_path) as f:
            ventas = json.load(f)
        for v in ventas:
            c.execute("""INSERT INTO ventas (comprobante,fecha,marca,modelo,anio,motor,chasis,cliente,cliente_doc,precio,moneda)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (v.get('comprobante'), v.get('fecha'), v.get('marca'), v.get('modelo'),
                 v.get('anio'), v.get('motor'), v.get('chasis'), v.get('cliente'),
                 v.get('cliente_doc'), v.get('precio',0), v.get('moneda','USD')))
        print(f" {len(ventas)} ventas importadas")

    # Importar compras
    compras_path = os.path.join(base, 'compras_full.json')
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
        print(f" {len(compras)} compras importadas")

    # Importar clientes
    clientes_path = os.path.join(base, 'clientes_full.json')
    if os.path.exists(clientes_path):
        with open(clientes_path) as f:
            clientes = json.load(f)
        for cl in clientes:
            c.execute("""INSERT INTO clientes (nombre,doc,telefono,direccion,ciudad,mail,relacion)
                VALUES (?,?,?,?,?,?,?)""",
                (cl.get('nombre'), cl.get('doc'), cl.get('telefono'),
                 cl.get('direccion'), cl.get('ciudad'), cl.get('mail'),
                 cl.get('relacion','Cliente')))
        print(f" {len(clientes)} clientes importados")

    conn.commit()
    conn.close()

# -- SERVIDOR HTTP ----------------------------------------
def json_response(handler, data, status=200):
    body = json.dumps(data, ensure_ascii=False, default=str).encode('utf-8')
    handler.send_response(status)
    handler.send_header('Content-Type', 'application/json; charset=utf-8')
    handler.send_header('Content-Length', len(body))
    handler.send_header('Access-Control-Allow-Origin', '*')
    handler.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    handler.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    handler.send_header('X-Content-Type-Options', 'nosniff')
    handler.send_header('X-Frame-Options', 'DENY')
    handler.end_headers()
    handler.wfile.write(body)

def check_rate_limit(ip):
    now = time.time()
    data = _login_attempts.get(ip, {'count': 0, 'reset': now + 300})
    if now > data['reset']:
        data = {'count': 0, 'reset': now + 300}
    data['count'] += 1
    _login_attempts[ip] = data
    return data['count'] > 10

def clear_rate_limit(ip):
    _login_attempts.pop(ip, None)

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
            json_response(self, {'status': 'ok', 'version': '1.0', 'empresa': 'AutomotoraGV'})

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

        if path == '/api/ping':
            json_response(self, {'ok': True})

        elif path == '/api/login':
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

    # -- AUTH --
    def _login(self):
        body = read_body(self)
        username = body.get('username', '').lower().strip()
        password = body.get('password', '')
        ip = self.client_address[0]

        # Rate limiting
        if check_rate_limit(ip):
            json_response(self, {'error': 'Demasiados intentos. Intenta en 5 minutos.'}, 429)
            return

        conn = get_db()
        row = conn.execute("SELECT * FROM usuarios WHERE username=? AND activo=1", (username,)).fetchone()
        conn.close()

        if not row or not check_password(password, row['password_hash']):
            json_response(self, {'error': 'Usuario o contrasena incorrectos'}, 401)
            return

        clear_rate_limit(ip)
        token = create_token({'id': row['id'], 'username': row['username'],
                               'nombre': row['nombre'], 'rol': row['rol']})
        json_response(self, {'token': token, 'nombre': row['nombre'],
                              'rol': row['rol'], 'username': row['username']})

    def _change_password(self, user):
        body = read_body(self)
        current_pw = body.get('current_password', '')
        new_pw = body.get('new_password', '')

        if not new_pw or len(new_pw) < 6:
            json_response(self, {'error': 'La nueva contrasena debe tener al menos 6 caracteres'}, 400)
            return

        conn = get_db()
        row = conn.execute("SELECT * FROM usuarios WHERE id=?", (user['id'],)).fetchone()
        if not row or not check_password(current_pw, row['password_hash']):
            conn.close()
            json_response(self, {'error': 'Contrasena actual incorrecta'}, 401)
            return

        conn.execute("UPDATE usuarios SET password_hash=? WHERE id=?",
                     (hash_password(new_pw), user['id']))
        conn.commit()
        conn.close()
        json_response(self, {'ok': True, 'message': 'Contrasena actualizada correctamente'})

    # -- VENTAS --
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

    # -- COMPRAS --
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

    # -- CLIENTES --
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

    # -- NEGOCIOS --
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

    # -- STOCK --
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

    # -- STATS --
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

    # -- SYNC --
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

    # -- SERVE FILES --
    def _serve_html(self):
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

# -- MAIN -------------------------------------------------
if __name__ == '__main__':
    print("=" * 50)
    print("  AutomotoraGV - Servidor de Gestion")
    print("=" * 50)

    init_db()
    import_json_data()

    # Copiar index.html al static si existe el build
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    os.makedirs(static_dir, exist_ok=True)

    server = http.server.ThreadingHTTPServer(('0.0.0.0', PORT), BMWHandler)
    print(f"\n Servidor corriendo en puerto {PORT}")
    print(f"  Usuarios: aacosta / gvillasuso / gyozzi")
    print(f"  Contrasena por defecto: BMW2026!")
    print(f"\n  Ctrl+C para detener\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n Servidor detenido")
