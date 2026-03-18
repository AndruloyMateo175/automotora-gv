import os, csv, io, re, http.cookiejar, urllib.request, urllib.parse, threading

EF_URL = os.environ.get('EFACTURA_URL', 'https://sc.220efactura.info/online')
EF_USER = os.environ.get('EFACTURA_USER', '')
EF_PASS = os.environ.get('EFACTURA_PASS', '')
PROVEEDORES = ['BMW','MINI','MAZDA','LAND ROVER','VOLVO','JEEP','FERRARI','PORSCHE','AUDI','JAGUAR','MOTOR HAUS','GRESMOL']

_last_result = {'ok': False, 'error': 'No sincronizado aun', 'ventas_nuevas': 0, 'compras_nuevas': 0}
_sync_running = False

def _do_sync(get_db_fn):
    global _last_result, _sync_running
    _sync_running = True
    try:
        cj = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0')]
        # Login
        opener.open(EF_URL + '/Login/', timeout=15)
        data = urllib.parse.urlencode({'nm_usr': EF_USER, 'nm_pass': EF_PASS}).encode()
        r = opener.open(EF_URL + '/Login/', data, timeout=15)
        html = r.read().decode('latin-1', errors='ignore')
        if 'MenuPrincipal' not in html and 'menu' not in html.lower():
            _last_result = {'ok': False, 'error': 'Login fallido'}
            return
        # CSV ventas
        url_v = EF_URL + '/ListadoComprobantesExcel/ListadoComprobantesExcel_config_csv.php?script_case_init=9170&summary_export_columns=S&password=n&nm_res_cons=n&nm_ini_csv_res=grid&nm_all_modules=grid&nm_delim_line=1&nm_delim_col=1&nm_delim_dados=1&nm_label_csv=N&language=es&origem=cons'
        url_c = EF_URL + '/ListadoFacturasCompra/ListadoFacturasCompra_config_csv.php?script_case_init=9170&summary_export_columns=S&password=n&nm_res_cons=n&nm_ini_csv_res=grid&nm_all_modules=grid&nm_delim_line=1&nm_delim_col=1&nm_delim_dados=1&nm_label_csv=N&language=es&origem=cons'
        csv_v = opener.open(url_v, timeout=30).read().decode('latin-1', errors='ignore')
        csv_c = opener.open(url_c, timeout=30).read().decode('latin-1', errors='ignore')
        conn = get_db_fn()
        vn = _parse_ventas(csv_v, conn)
        cn = _parse_compras(csv_c, conn)
        conn.commit(); conn.close()
        _last_result = {'ok': True, 'ventas_nuevas': vn, 'compras_nuevas': cn}
    except Exception as e:
        _last_result = {'ok': False, 'error': str(e)}
    finally:
        _sync_running = False

def _parse_ventas(text, conn):
    n = 0
    for row in list(csv.reader(io.StringIO(text), delimiter=';'))[1:]:
        if len(row) < 8: continue
        tipo = row[0].strip().strip('"')
        if tipo not in ('e-Ticket','e-Factura'): continue
        comp = tipo + ' ' + row[1].strip().strip('"')
        if conn.execute('SELECT id FROM ventas WHERE comprobante=?',(comp,)).fetchone(): continue
        fecha = row[2].strip().strip('"')
        cli_raw = row[4].strip().strip('"') if len(row)>4 else ''
        m = re.match(r'^(.+?)\s*\([^)]+\)$', cli_raw)
        cli = m.group(1).strip() if m else cli_raw
        det = row[5].strip().strip('"') if len(row)>5 else ''
        try: precio = float(row[7].strip().strip('"').replace('.','').replace(',','.'))
        except: precio = 0
        mon = row[8].strip().strip('"') if len(row)>8 else 'USD'
        conn.execute('INSERT INTO ventas (fecha,cliente,detalle,precio_usd,moneda,comprobante) VALUES (?,?,?,?,?,?)',
            (fecha,cli,det,precio,mon,comp))
        n += 1
    return n

def _parse_compras(text, conn):
    n = 0
    for row in list(csv.reader(io.StringIO(text), delimiter=';'))[1:]:
        if len(row) < 8: continue
        tipo = row[0].strip().strip('"')
        if tipo not in ('e-Ticket','e-Factura','e-Remito'): continue
        comp = tipo + ' ' + row[1].strip().strip('"')
        prov = row[4].strip().strip('"') if len(row)>4 else ''
        if not any(v in prov.upper() for v in PROVEEDORES): continue
        if conn.execute('SELECT id FROM compras WHERE comprobante=?',(comp,)).fetchone(): continue
        fecha = row[2].strip().strip('"')
        det = row[5].strip().strip('"') if len(row)>5 else ''
        try: precio = float(row[7].strip().strip('"').replace('.','').replace(',','.'))
        except: precio = 0
        mon = row[8].strip().strip('"') if len(row)>8 else 'USD'
        conn.execute('INSERT INTO compras (fecha,proveedor,comprobante,precio_usd,moneda,detalle,marca,modelo,anio,motor,chasis,color) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
            (fecha,prov,comp,precio,mon,det,'','','','','',''))
        n += 1
    return n

def run_sync(get_db_fn):
    global _sync_running
    if not EF_USER or not EF_PASS:
        return {'ok': False, 'error': 'Credenciales no configuradas'}
    if _sync_running:
        return {'ok': False, 'error': 'Sync ya en progreso'}
    t = threading.Thread(target=_do_sync, args=(get_db_fn,), daemon=True)
    t.start()
    return {'ok': True, 'status': 'iniciado', 'ventas_nuevas': 0, 'compras_nuevas': 0}

def get_last_result():
    return _last_result
