
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
        c = conn.cursor()
        for r in data:
            c.execute('INSERT INTO compras (fecha,proveedor,comprobante,marca,modelo,chasis,motor,precio_usd,precio_uyu) VALUES (?,?,?,?,?,?,?,?,?)',
                (r.get('fecha',''), r.get('proveedor',''), r.get('comprobante',''),
                 '', '', '', '', float(r.get('precio_usd',0)), 0))
        conn.commit()
        conn.close()
        print('Auto-import: ' + str(len(data)) + ' compras')
    except Exception as e:
        print('Auto-import error: ' + str(e))

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
