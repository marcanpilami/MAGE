"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from gcl.models import InstallableSet, InstallableItem
from ref.models import Application, LogicalComponent, \
    ComponentImplementationClass, EnvironmentType, Environment
from ora.models import UnixServer, OracleInstance, OracleSchema
from ora.tests import TestHelper, utility_create_test_envt 


class SimpleTest(TestCase):
    
    def utility_create(self):
        utility_create_test_envt(1)
        ref = TestHelper()
        is1 = InstallableSet(name='SYSTEM1_23B2', description='Solves all issues. Ever.')
        is1.save()
        
        ii1_1 = InstallableItem(what_is_installed = ref.l)
        
        
        
    def test_create(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

