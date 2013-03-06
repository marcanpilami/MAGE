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
from ora.models import OracleInstance, DebugServer
from ref.models import ComponentInstance


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
        d = DebugServer(marsu='test')
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