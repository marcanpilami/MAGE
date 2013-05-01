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
        res = parser.get_components('((S,name="waPRDINT2"))')
        self.assertEqual(1, len(res))
        
        # Only a type
        res = parser.get_components('((T,wascluster))')
        self.assertEqual(4, len(res))
        
        # A type and a name
        res = parser.get_components('((T,wascluster)(S,name="wcluPRDUSR"))')
        self.assertEqual(1, len(res))

    def test_mcl_with_nothing(self):
        utility_create_test_envt(1)
        
        # Nothing at all - no filter means returning everything!
        res = parser.get_components('()')
        self.assertEqual(ComponentInstance.objects.count(), len(res))
        
    def test_mcl_with_one_simple_relation(self):
        utility_create_test_envt(1)
        
        # One parent specified by name (P)
        res = parser.get_components('((P,((S,name="wcluPRDUSR"))))')
        self.assertEqual(3, len(res))
        
        # One parent specified by model and name (P)
        res = parser.get_components('((P,((T,wascluster)(S,name="wcluPRDUSR"))))')
        self.assertEqual(3, len(res))
        
        # One connected partner specified by model and name (C)
        res = parser.get_components('((C,((T,oracleschema)(S,name="prd_int"))))')
        self.assertEqual(2, len(res))
        
    def test_mcl_with_one_complex_relation(self):
        utility_create_test_envt(1)
        
        # P -> P
        res = parser.get_components('((P,((T,wascluster)(S,name="wcluPRDUSR")(P,((S,name="wcellPRD"))))))')
        self.assertEqual(3, len(res))
        
        # C -> P
        res = parser.get_components('((C,((T,oracleschema)(S,name="prd_user")(P,((S,name="ORAINST3"))))))')
        self.assertEqual(1, len(res))
        
    def test_mcl_with_multiple_relations(self):
        utility_create_test_envt(1)
        
        # One P, one C
        res = parser.get_components('((P,((S,name="wcluPRDUSR")))(C,((S,name="prd_user"))))')
        self.assertEqual(1, len(res))
        
        res = parser.get_components('((T,wasapplication)(S,name="integration", name="integration")(C,((T,oracleschema)(S,name="prd_int")))(P,was_cluster,((T,wascluster)(P,((T,wascell)(S,name="wcellPRD")))))))')
        self.assertEqual(1, len(res))
        
        # With a mistake in relationship name
        res = parser.get_components('((T,wasapplication)(S,name="integration", name="integration")(C,((T,oracleschema)(S,name="prd_int")))(P,was_clusterZ,((T,wascluster)(P,((T,wascell)(S,name="wcellPRD")))))))')
        self.assertEqual(0, len(res))
        
        # With a mistake in C name
        res = parser.get_components('((T,wasapplication)(S,name="integration", name="integration")(C,((T,oracleschema)(S,name="prd_intZ")))(P,was_cluster,((T,wascluster)(P,((T,wascell)(S,name="wcellPRD")))))))')
        self.assertEqual(0, len(res))
        
        
        
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
        
        ## Add a parameter
        t2_1.extParams['houba'] = 'meuh'
        self.assertEqual(len(t2_1.extParams), 1)
        t2_1.extParams['houba2'] = 'meuh2'
        self.assertEqual(len(t2_1.extParams), 2)
        del t2_1.extParams['houba2']
        self.assertEqual(len(t2_1.extParams), 1)
        
        
    def test_nc(self):
        #utility_create_test_envt(1)
        
        et1 = EnvironmentType(name='production', short_name='PRD')
        et1.save()
        e1 = Environment(name='PRD1', typology=et1, description='production envt')
        e1.save()
        e2 = Environment(name='PRD2', typology=et1, description='production envt 2')
        e2.save()
        
    
        nc1 = naming.nc_create_naming_convention('genius convention')
        nb = nc1.fields.count()
        self.assertLess(10, nb)
        
        # A sync should not modify the convention
        naming.nc_sync_naming_convention(nc1)
        self.assertEqual(nb, nc1.fields.count())
        
        # Set a field
        nc1.set_field('test2', 'name', 'TEST2_%E%')
        nc1.set_field('test1', 'name', 'TEST1_%E%')
        t1 = Test1()
        t1.save()
        t1.environments.add(e1)
        
        t3 = Test1()
        t3.save()
        t3.environments.add(e2)
        
        t2 = Test2()
        t2.save()
        nc1.value_instance(t2)
        t2.save()
        
        self.assertEqual('TEST2_NOENVIRONMENT', t2.name)
        
        # Without force, name should not change
        t2.environments.add(e2)
        nc1.value_instance(t2)
        t2.save()
        self.assertEqual('TEST2_NOENVIRONMENT', t2.name)
        
        # With force, it should
        nc1.value_instance(t2, force = True)
        self.assertEqual('TEST2_PRD2', t2.name)
        
        ## Counters/sequences: global
        nc1.set_field('test2', 'name', 'TEST2_%cg%')
        nc1.value_instance(t2, force = True)
        self.assertEqual('TEST2_1', t2.name)
        
        nc1.value_instance(t2, force = True)
        self.assertEqual('TEST2_2', t2.name)
        
        # other models in other envt should also use the same counter
        nc1.set_field('test1', 'name', 'TEST1_%cg%')
        nc1.value_instance(t1)
        self.assertEqual('TEST1_3', t1.name)
        
        ## Counters: by environment
        nc1.set_field('test2', 'name', 'TEST2_%ce%')
        nc1.value_instance(t2, force = True)
        self.assertEqual('TEST2_1', t2.name)
        
        nc1.value_instance(t2, force = True)
        self.assertEqual('TEST2_2', t2.name)
        
        nc1.set_field('test1', 'name', 'TEST1_%ce%')
        nc1.value_instance(t1, force = True)
        self.assertEqual('TEST1_1', t1.name)
        
        ## Counters: by envt and model type
        nc1.set_field('test2', 'name', 'TEST2_%cem%')
        nc1.value_instance(t2, force = True)
        self.assertEqual('TEST2_1', t2.name)
        nc1.value_instance(t2, force = True)
        self.assertEqual('TEST2_2', t2.name)
        nc1.value_instance(t2, force = True)
        self.assertEqual('TEST2_3', t2.name)
        
        nc1.set_field('test1', 'name', 'TEST1_%cem%')
        nc1.value_instance(t3, force = True)
        self.assertEqual('TEST1_1', t3.name)
        nc1.value_instance(t3, force = True)
        self.assertEqual('TEST1_2', t3.name)