"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from gcl.models import InstallableSet
from ref.models import Application, LogicalComponent, \
    ComponentImplementationClass, EnvironmentType, Environment
from ora.models import UnixServer, OracleInstance, OracleSchema


class SimpleTest(TestCase):
    
        
        
        
    def utility_create(self):
        is1 = InstallableSet(name='SYSTEM1_23B2', description='Solves all issues. Ever.')
        is1.save()
        
        
    def test_create(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

