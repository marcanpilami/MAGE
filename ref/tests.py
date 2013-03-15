"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from ora.tests import utility_create_test_envt
from ref.mcl import parser 
from ref.models import ComponentInstance

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
        