"""Executa o cenário fictício em memória e gera sua prévia SVG."""
import sys
from pathlib import Path
from preview_utils import preview
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from planner import connect,initialize,create_trip,assign,snapshot

def main():
    con=connect(':memory:')
    try:
        initialize(con)
        trip_a=create_trip(con,{'vehicle_id':1,'day':'2026-09-30'})
        for order in [1,2]:assign(con,{'order_id':order,'trip_id':trip_a})
        try:assign(con,{'order_id':3,'trip_id':trip_a})
        except ValueError as error:rejection=str(error)
        else:raise AssertionError('Excesso de capacidade não rejeitado')
        trip_b=create_trip(con,{'vehicle_id':2,'day':'2026-09-30'})
        assign(con,{'order_id':3,'trip_id':trip_b})
        state=snapshot(con)
        fmt=lambda n:format(n,',').replace(',','.')
        trips=[(t['name'],f"{fmt(t['load'])} / {fmt(t['capacity'])} kg") for t in state['trips']]
        preview('Planejamento de entregas','Cenário executado: Alfa e Beta no A; Gama no B após rejeição de excesso',
                [('Pedidos planejados',len(state['orders'])),('Viagens',len(state['trips'])),('Carga planejada',f"{fmt(sum(t['load'] for t in state['trips']))} kg")],
                [('Viagens e capacidade',trips),('Regra demonstrada',[('Gama no Caminhão A',rejection),('Alfa + Beta no Caminhão A','87,5% de ocupação'),('Gama no Caminhão B','Pedido planejado')])],ROOT/'docs/assets/preview.svg')
    finally:con.close()
if __name__=='__main__':main()
