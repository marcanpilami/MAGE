"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from ora.tests import utility_create_test_envt
from ref.mcl import get_components 

class SimpleTest(TestCase):
    def test_mcl1(self):
        utility_create_test_envt()
        
        mcl1 = '(S,name="srv_prd_oracle")'
        res1 = get_components(mcl1)
        self.assertEqual(1, len(res1))
        
        mcl2 = '(S,name="as_name")(P,name="cluster_name"|P,name="cell_name")(P,name="server_name")(T,"wasas")'