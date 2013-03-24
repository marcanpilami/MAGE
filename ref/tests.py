"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from cpn.tests import utility_create_test_envt
from ref.mcl import parser 
from ref.models import ComponentInstance, Environment, Test1, EnvironmentType,\
    Test2
import naming
from MAGE.exceptions import MageError

class SimpleTest(TestCase):
    def test_mcl_without_relations(self):
        utility_create_test_envt(1)
        
        # Only a name.
        res = parser.get_components('(S,name="waPRDINT2")')
        self.assertEqual(1, len(res))
        
        # Only a type
        res = parser.get_components('(T,"wascluster")')
        self.assertEqual(4, len(res))
        
        # A type and a name
        res = parser.get_components('(T,"wascluster")(S,name="wcluPRDUSR")')
        self.assertEqual(1, len(res))

    def test_mcl_with_nothing(self):
        utility_create_test_envt(1)
        
        # Nothing at all - no filter means returning everything!
        res = parser.get_components('')
        self.assertEqual(ComponentInstance.objects.count(), len(res))
        
    def test_mcl_with_one_simple_relation(self):
        utility_create_test_envt(1)
        
        # One parent specified by name (P)
        res = parser.get_components('(P,name="wcluPRDUSR")')
        self.assertEqual(3, len(res))
        
        # One parent specified by model and name (P)
        res = parser.get_components('(P,model="wascluster",name="wcluPRDUSR")')
        self.assertEqual(3, len(res))
        
        # One connected partner specified by model and name (C)
        res = parser.get_components('(C,model="oracleschema",name="prd_int")')
        self.assertEqual(2, len(res))
        
    def test_mcl_with_one_complex_relation(self):
        utility_create_test_envt(1)
        
        # P,P
        res = parser.get_components('(P,model="wascluster",name="wcluPRDUSR"|P,name="wcellPRD")')
        self.assertEqual(3, len(res))
        
        # C,P
        res = parser.get_components('(C,model="oracleschema",name="prd_user"|P,name="ORAINST3")')
        self.assertEqual(1, len(res))
        
    def test_mcl_with_multiple_relations(self):
        utility_create_test_envt(1)
        
        # One P, one C
        res = parser.get_components('(P,name="wcluPRDUSR")(C,name="prd_user")')
        self.assertEqual(1, len(res))
        
    def test_nc(self):
        utility_create_test_envt(1)
        
        nc1 = naming.nc_create_naming_convention('genius convention')
        nb = nc1.fields.count()
        self.assertLess(10, nb)
        
        # A sync should not modify the convention
        naming.nc_sync_naming_convention(nc1)
        self.assertEqual(nb, nc1.fields.count())
    
    def test_base(self):
        et1 = EnvironmentType(name='production', short_name='PRD')
        et1.save()
        
        e = Environment(name = 'marsu', typology = et1)
        e.save()
        
        t1_1 = Test1(name = 't1_1', raccoon = 'pouet')
        t1_1.save()
        t1_1.environments.add(e)
        
        t1_2 = Test1(name = 't1_2', raccoon = 'pouet')
        t1_2.save()
        t1_2.environments.add(e)
        
        t2_1 = Test2(name = 't2_1')
        t2_1.save()
        
        t2_2 = Test2(name = 't2_2')
        t2_2.save()
        t2_2.daddies_add(t1_1)
        t2_2.daddies_add(t1_2)
        
        t2_1.daddy = t1_1
        
        self.assertEqual(len(t2_1.dependsOn.all()), 1)
        
        # change the relation
        t2_1.daddy = t1_2
        self.assertEqual(len(t2_1.dependsOn.all()), 1)
        self.assertEqual(t2_1.daddy, t1_2)
        
        ## M2M
        with self.assertRaises(AttributeError):
            t2_1.daddies = t1_2
            
        t2_1.daddies_add(t1_2)
        self.assertEqual(t2_1.daddies.count(), 1)
        t2_1.daddies_add(t1_1)
        self.assertEqual(t2_1.daddies.count(), 2)
        
        with self.assertRaises(MageError):
            t2_1.daddies_add(t1_1)
        self.assertEqual(t2_1.daddies.count(), 2)
        
        t2_1.daddies_delete(t1_2)
        self.assertEqual(t2_1.daddies.count(), 1)
        
        self.assertEqual(t2_1.daddies[0], t1_1)
        