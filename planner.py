"""Regras transacionais do planejador demonstrativo."""
import sqlite3
from datetime import date

SCHEMA = """
CREATE TABLE IF NOT EXISTS vehicle(id INTEGER PRIMARY KEY,name TEXT NOT NULL,capacity INTEGER NOT NULL CHECK(capacity>0));
CREATE TABLE IF NOT EXISTS trip(id INTEGER PRIMARY KEY,vehicle_id INTEGER NOT NULL REFERENCES vehicle(id),day TEXT NOT NULL,UNIQUE(vehicle_id,day));
CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY,producer TEXT NOT NULL,product TEXT NOT NULL,day TEXT NOT NULL,kg INTEGER NOT NULL CHECK(kg>0),status TEXT NOT NULL DEFAULT 'pendente' CHECK(status IN ('pendente','planejado','entregue','cancelado')),trip_id INTEGER REFERENCES trip(id));
"""

def connect(path):
    c=sqlite3.connect(path,timeout=10);c.row_factory=sqlite3.Row
    c.execute('PRAGMA foreign_keys=ON');return c

def initialize(c):
    c.executescript(SCHEMA)
    with c:
        if not c.execute('SELECT COUNT(*) FROM vehicle').fetchone()[0]:
            c.executemany('INSERT INTO vehicle(name,capacity) VALUES(?,?)',[('Caminhão A',16000),('Caminhão B',18000),('Caminhão C',11000)])
            c.executemany('INSERT INTO orders(producer,product,day,kg) VALUES(?,?,?,?)',[
                ('Produtor Alfa','Alojamento 1','2026-09-30',6000),('Produtor Beta','Crescimento 1','2026-09-30',8000),('Produtor Gama','Terminação 2A','2026-09-30',10000)])

def integer(v,field):
    if isinstance(v,bool):raise ValueError(f'{field} inválido')
    try:
        n=int(v)
        if str(n)!=str(v) or n<=0:raise ValueError()
        return n
    except (TypeError,ValueError):raise ValueError(f'{field} deve ser inteiro positivo') from None

def iso(v):
    if not isinstance(v,str):raise ValueError('Data inválida')
    try:
        d=date.fromisoformat(v)
        if d.isoformat()!=v:raise ValueError()
    except ValueError:raise ValueError('Data deve usar AAAA-MM-DD') from None
    return v

def create_order(c,data):
    producer=data.get('producer','');product=data.get('product','')
    if not all(isinstance(x,str) and 1<=len(x.strip())<=100 for x in (producer,product)):
        raise ValueError('Produtor e produto devem ter de 1 a 100 caracteres')
    kg=integer(data.get('kg'),'Peso');day=iso(data.get('day'))
    if kg>1000000:raise ValueError('Peso máximo por pedido: 1.000.000 kg')
    with c:
        cursor=c.execute('INSERT INTO orders(producer,product,day,kg) VALUES(?,?,?,?)',(producer.strip(),product.strip(),day,kg))
    return cursor.lastrowid

def create_trip(c,data):
    vehicle_id=integer(data.get('vehicle_id'),'Veículo');day=iso(data.get('day'))
    if not c.execute('SELECT 1 FROM vehicle WHERE id=?',(vehicle_id,)).fetchone():raise ValueError('Veículo inexistente')
    try:
        with c:return c.execute('INSERT INTO trip(vehicle_id,day) VALUES(?,?)',(vehicle_id,day)).lastrowid
    except sqlite3.IntegrityError:raise ValueError('Já existe uma viagem para esse veículo nessa data') from None

def assign(c,data):
    oid=integer(data.get('order_id'),'Pedido');tid=integer(data.get('trip_id'),'Viagem')
    # Lock antes de ler a carga para serializar duas atribuições concorrentes.
    with c:
        c.execute('BEGIN IMMEDIATE')
        order=c.execute('SELECT * FROM orders WHERE id=?',(oid,)).fetchone()
        trip=c.execute('SELECT t.*,v.capacity FROM trip t JOIN vehicle v ON v.id=t.vehicle_id WHERE t.id=?',(tid,)).fetchone()
        if not order or not trip:raise ValueError('Pedido ou viagem inexistente')
        if order['status']!='pendente':raise ValueError('Somente pedidos pendentes podem ser planejados')
        if order['day']!=trip['day']:raise ValueError('Pedido e viagem precisam ter a mesma data')
        load=c.execute("SELECT COALESCE(SUM(kg),0) FROM orders WHERE trip_id=? AND status IN ('planejado','entregue')",(tid,)).fetchone()[0]
        if load+order['kg']>trip['capacity']:raise ValueError('Carga excede a capacidade do veículo')
        c.execute("UPDATE orders SET status='planejado',trip_id=? WHERE id=?",(tid,oid))

def change_status(c,data):
    oid=integer(data.get('order_id'),'Pedido');status=data.get('status')
    if status not in ('entregue','cancelado','pendente'):raise ValueError('Ação inválida')
    with c:
        c.execute('BEGIN IMMEDIATE')
        order=c.execute('SELECT * FROM orders WHERE id=?',(oid,)).fetchone()
        if not order:raise ValueError('Pedido inexistente')
        allowed={'entregue':('planejado',),'cancelado':('pendente','planejado'),'pendente':('planejado',)}
        if order['status'] not in allowed[status]:raise ValueError('Transição de status não permitida')
        trip_id=order['trip_id'] if status=='entregue' else None
        c.execute('UPDATE orders SET status=?,trip_id=? WHERE id=?',(status,trip_id,oid))

def snapshot(c):
    return {
        'vehicles':[dict(x) for x in c.execute('SELECT * FROM vehicle ORDER BY id')],
        'orders':[dict(x) for x in c.execute('SELECT * FROM orders ORDER BY day,id')],
        'trips':[dict(x) for x in c.execute("SELECT t.id,t.day,v.name,v.capacity,COALESCE(SUM(CASE WHEN o.status IN ('planejado','entregue') THEN o.kg ELSE 0 END),0) AS load FROM trip t JOIN vehicle v ON v.id=t.vehicle_id LEFT JOIN orders o ON o.trip_id=t.id GROUP BY t.id ORDER BY t.day,t.id")]
    }
