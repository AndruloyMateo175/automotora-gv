import os, csv, io, re, http.cookiejar, urllib.request, urllib.parse

EF_URL = os.environ.get('EFACTURA_URL', 'https://sc.220efactura.info/online')
EF_USER = os.environ.get('EFACTURA_USER', '')
EF_PASS = os.environ.get('EFACTURA_PASS', '')

PROVEEDORES = ['BMW','MINI','MAZDA','LAND ROVER','VOLVO','JEEP','FERRARI','PORSCHE','AUDI','JAGUAR','MOTOR HAUS','GRESMOL']

def get_opener():
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    opener.addheaders = [
        ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'),
        ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
    ]
    return opener

def login(opener):
    # Primero cargar la pagina de login para obtener cookies
    opener.open(EF_URL + '/Login/')
    # Hacer login
    data = urllib.parse.urlencode({'nm_usr': EF_USER, 'nm_pass': EF_PASS, 'login': '1'}).encode()
    r = opener.open(EF_URL + '/Login/', data)
    content = r.read().decode('latin-1', errors='ignore')
    # Verificar que el login fue exitoso
    return 'MenuPrincipal' in content or 'menu' in content.lower()

def fetch_csv(opener, url):
    r = opener.open(url)
    return r.read().decode('latin-1', errors='ignore')

def parse_ventas(csv_text, conn):
    nuevas = 0
    rows = list(csv.reader(io.StringIO(csv_text), delimiter=';'))
    for row in rows[1:]:
        if len(row) < 8: continue
        tipo = row[0].strip().strip('"')
        if tipo not in ('e-Ticket', 'e-Factura'): continue
        numero = row[1].strip().strip('"')
        comprobante = tipo + ' ' + numero
        fecha = row[2].strip().strip('"')
        cliente_raw = row[4].strip().strip('"') if len(row) > 4 else ''
        cm = re.match(r'^(.+?)\s*\([^)]+\)$', cliente_raw)
        cliente = cm.group(1).strip() if cm else cliente_raw
        detalle = row[5].strip().strip('"') if len(row) > 5 else ''
        try: precio = float(row[7].strip().strip('"').replace('.','').replace(',','.'))
        except: precio = 0
        moneda = row[8].strip().strip('"') if len(row) > 8 else 'USD'
        exists = conn.execute('SELECT id FROM ventas WHERE comprobante=?', (comprobante,)).fetchone()
        if not exists:
            conn.execute('INSERT INTO ventas (fecha,cliente,detalle,precio_usd,moneda,comprobante) VALUES (?,?,?,?,?,?)',
                (fecha, cliente, detalle, precio, moneda, comprobante))
            nuevas += 1
    return nuevas

def parse_compras(csv_text, conn):
    nuevas = 0
    rows = list(csv.reader(io.StringIO(csv_text), delimiter=';'))
    for row in rows[1:]:
        if len(row) < 8: continue
        tipo = row[0].strip().strip('"')
        if tipo not in ('e-Ticket', 'e-Factura', 'e-Remito'): continue
        numero = row[1].strip().strip('"')
        comprobante = tipo + ' ' + numero
        fecha = row[2].strip().strip('"')
        proveedor = row[4].strip().strip('"') if len(row) > 4 else ''
        if not any(v in proveedor.upper() for v in PROVEEDORES): continue
        detalle = row[5].strip().strip('"') if len(row) > 5 else ''
        try: precio = float(row[7].strip().strip('"').replace('.','').replace(',','.'))
        except: precio = 0
        moneda = row[8].strip().strip('"') if len(row) > 8 else 'USD'
        exists = conn.execute('SELECT id FROM compras WHERE comprobante=?', (comprobante,)).fetchone()
        if not exists:
            conn.execute('INSERT INTO compras (fecha,proveedor,comprobante,precio_usd,moneda,detalle,marca,modelo,anio,motor,chasis,color) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
                (fecha, proveedor, comprobante, precio, moneda, detalle, '','','','','',''))
            nuevas += 1
    return nuevas

def run_sync(conn):
    if not EF_USER or not EF_PASS:
        return {'ok': False, 'error': 'Credenciales no configuradas'}
    try:
        opener = get_opener()
        ok = login(opener)
        if not ok:
            return {'ok': False, 'error': 'Login fallido en eFactura'}
        csv_v = fetch_csv(opener, EF_URL + '/ListadoComprobantesExcel/ListadoComprobantesExcel_config_csv.php?script_case_init=9170&summary_export_columns=S&password=n&nm_res_cons=n&nm_ini_csv_res=grid&nm_all_modules=grid&nm_delim_line=1&nm_delim_col=1&nm_delim_dados=1&nm_label_csv=N&language=es&origem=cons')
        csv_c = fetch_csv(opener, EF_URL + '/ListadoFacturasCompra/ListadoFacturasCompra_config_csv.php?script_case_init=9170&summary_export_columns=S&password=n&nm_res_cons=n&nm_ini_csv_res=grid&nm_all_modules=grid&nm_delim_line=1&nm_delim_col=1&nm_delim_dados=1&nm_label_csv=N&language=es&origem=cons')
        ventas_nuevas = parse_ventas(csv_v, conn)
        compras_nuevas = parse_compras(csv_c, conn)
        conn.commit()
        return {'ok': True, 'ventas_nuevas': ventas_nuevas, 'compras_nuevas': compras_nuevas}
    except Exception as e:
        return {'ok': False, 'error': str(e)}
