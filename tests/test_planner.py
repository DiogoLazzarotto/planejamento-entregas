import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from planner import *
class PlannerTests(unittest.TestCase):
 def setUp(self):self.c=connect(':memory:');initialize(self.c)
 def tearDown(self):self.c.close()
 def trip(self):return create_trip(self.c,{'vehicle_id':1,'day':'2026-09-30'})
 def test_capacity_atomic(self):
  tid=self.trip();assign(self.c,{'order_id':1,'trip_id':tid});assign(self.c,{'order_id':2,'trip_id':tid})
  with self.assertRaisesRegex(ValueError,'capacidade'):assign(self.c,{'order_id':3,'trip_id':tid})
  self.assertEqual(snapshot(self.c)['trips'][0]['load'],14000);self.assertEqual(snapshot(self.c)['orders'][2]['status'],'pendente')
 def test_date(self):
  tid=create_trip(self.c,{'vehicle_id':1,'day':'2026-10-01'})
  with self.assertRaisesRegex(ValueError,'mesma data'):assign(self.c,{'order_id':1,'trip_id':tid})
 def test_transitions(self):
  with self.assertRaises(ValueError):change_status(self.c,{'order_id':1,'status':'entregue'})
  tid=self.trip();assign(self.c,{'order_id':1,'trip_id':tid});change_status(self.c,{'order_id':1,'status':'entregue'})
  self.assertEqual(snapshot(self.c)['trips'][0]['load'],6000)
  with self.assertRaises(ValueError):change_status(self.c,{'order_id':1,'status':'cancelado'})
 def test_cancel_releases_capacity(self):
  tid=self.trip();assign(self.c,{'order_id':1,'trip_id':tid});change_status(self.c,{'order_id':1,'status':'cancelado'})
  self.assertEqual(snapshot(self.c)['trips'][0]['load'],0)
 def test_unplan(self):
  tid=self.trip();assign(self.c,{'order_id':1,'trip_id':tid});change_status(self.c,{'order_id':1,'status':'pendente'})
  self.assertIsNone(snapshot(self.c)['orders'][0]['trip_id'])
 def test_validation(self):
  for kg in [0,-1,1.2,True,None,'NaN']:
   with self.subTest(kg=kg),self.assertRaises(ValueError):create_order(self.c,{'producer':'A','product':'B','day':'2026-09-30','kg':kg})
  with self.assertRaises(ValueError):create_order(self.c,{'producer':'A','product':'B','day':'2026-02-30','kg':10})
 def test_duplicate_trip_and_assignment(self):
  tid=self.trip()
  with self.assertRaises(ValueError):self.trip()
  assign(self.c,{'order_id':1,'trip_id':tid})
  with self.assertRaises(ValueError):assign(self.c,{'order_id':1,'trip_id':tid})
if __name__=='__main__':unittest.main()
