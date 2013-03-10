'''
Created on 6 mars 2013

@author: Marc-Antoine
'''
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.contenttypes.models import ContentType

from ref.models import ComponentInstance
from ref.models import Application, LogicalComponent, \
    ComponentImplementationClass, EnvironmentType, Environment
from ora.models import UnixServer, OracleInstance, OracleSchema


def utility_create_test_min_envt(i):
    a1 = Application(name='application %s' % i)
    a1.save()
    
    l1 = LogicalComponent(name='RDBMS container for module 1', application = a1)
    l1.save()
    
    et1 = EnvironmentType(name='production', short_name='PRD')
    et1.save()
 
    impl_1_1 = ComponentImplementationClass(name='Oracle schema for module 1', description='Oracle schema in a mutualized instance', implements=l1, python_model_to_use=ContentType.objects.get_for_model(OracleSchema))
    impl_1_1.save()
    
    et1.implementation_patterns.add(impl_1_1)
    
    e1 = Environment(name='PRD1', typology=et1, description = 'production envt')
    e1.save()
   
    us1 = UnixServer(name='server1')
    us1.save()
    
    return a1

def utility_create_test_envt(i):
    a1 = Application(name='application %s' % i)
    a1.save()
    
    l1 = LogicalComponent(name='RDBMS container for module 1', application = a1)
    l1.save()
    l2 = LogicalComponent(name='RDBMS container for module 2', application = a1)
    l2.save()
    
    et1 = EnvironmentType(name='production', short_name='PRD')
    et2 = EnvironmentType(name='functional conformity', short_name='FCF')
    et3 = EnvironmentType(name='technical conformity', short_name='TCF')
    et4 = EnvironmentType(name='integration tests', short_name='INT')
    et5 = EnvironmentType(name='development', short_name='DEV')
    et1.save()
    et2.save()
    et3.save()
    et4.save()
    et5.save()
    
    impl_1_1 = ComponentImplementationClass(name='Oracle schema for module 1', description='Oracle schema in a mutualized instance', implements=l1, python_model_to_use=ContentType.objects.get_for_model(OracleSchema))
    impl_1_2 = ComponentImplementationClass(name='PostgresQL database for module 1', description='Dedicated database', implements=l1, python_model_to_use=ContentType.objects.get_for_model(OracleSchema))
    impl_2_1 = ComponentImplementationClass(name='Oracle schema for module 2', description='Oracle schema in a mutualized instance', implements=l2, python_model_to_use=ContentType.objects.get_for_model(OracleSchema))
    impl_1_1.save()
    impl_1_2.save()
    impl_2_1.save()
    
    et1.implementation_patterns.add(impl_1_1, impl_2_1)
    et5.implementation_patterns.add(impl_1_2, impl_2_1) ## DEV has a dedicated db so they can destroy it.
    
    e1 = Environment(name='PRD1', typology=et1, description = 'production envt')
    e1.save()
    e2 = Environment(name='DEV1', typology=et5, description = 'development environment for editor teams')
    e2.save()
    e3 = Environment(name='DEV2', typology=et5, description = 'development environment for integrator teams')
    e3.save()
    e4= Environment(name='TEC1', typology=et3, description = 'technical team\'s sandbox')
    e4.save()
    e5= Environment(name='TEC2', typology=et5, description = 'for packaging tests')
    e5.save()
    e6= Environment(name='TEC3', typology=et5, description = 'staging environment used for request fulfillment - partial restoration, parameter test...')
    e6.save()
    
    us1 = UnixServer(name='server1')
    us1.save()
    us2 = UnixServer(name='server2')
    us2.save()
    
    oi1 = OracleInstance(name='ORAINST1')
    oi1.save()
    oi1.dependsOn.add(us1)
    
    os1 = OracleSchema(name='schema_compo_1', instanciates=impl_1_1)
    os1.save()
    os2 = OracleSchema(name='schema compo 2', instanciates=impl_2_1)
    os2.save()
    os1.environments.add(e1)
    os2.environments.add(e1)
    os1.dependsOn.add(oi1)
    os2.dependsOn.add(oi1)
    
    return a1


class SimpleTest(TestCase):
    def test_creation(self):
        """
        Tests that it is possible to create an instance
        """
        i = OracleInstance(port=123, listener="LISTENER")
        
        self.assertEqual(i.port, 123)
    
    def test_parents_and_polymorphism(self):
        """
        Tests that it is possible to access the auto fields from an instance
        """
        i = OracleInstance(port=123, listener="LISTENER")
        d = UnixServer(marsu='test')
        i.save()
        d.save()
        
        i.dependsOn.add(d)
        i.save()
        
        self.assertEqual(i.port, 123)
        self.assertNotEqual(i.base_server, None)
        self.assertEqual(i.base_server.marsu, 'test')      
        
        r = ComponentInstance.objects.get(pk=i.pk)
        self.assertNotEqual(r.leaf, None)
        self.assertEqual(r.leaf.base_server.marsu, 'test') 

    def test_description(self):
        i = OracleInstance(name='SUPERINSTANCE', port=123, listener="LISTENER")
        self.assertEqual(i.__unicode__(), 'SUPERINSTANCE')
        
    def test_fullapp(self):
        utility_create_test_envt(1)
