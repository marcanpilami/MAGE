# coding: utf-8
from django.test import TestCase
from ref.naming_language import resolve

class NLTestCase(TestCase):
    def setUp(self):
        pass

    def test_parsing_navigation_simple(self):
        pattern = '%client_url'
        resolve(pattern)
        
        
    def test_parsing_navigation_dotted(self):
        pattern = '%group.domain.name'
        resolve(pattern)
        
        
    def test_parsing_string(self):
        pattern = '"houba"'
        resolve(pattern)
        
    def test_parsing_operation_simple(self):
        pattern = '12+98'
        resolve(pattern)
    
    def test_parsing_operation_subexpr(self):
        pattern = '%port+98'
        resolve(pattern)    
        
    def test_alternative(self):
        resolve('"r"?("y"?"z")')
        
    def test_alternative_double_no_protection(self):
        resolve('"r"|"y"?"z"')
        
    def test_parsing_n(self):
        pattern = '%client_url?("http://"|%group.dns_to_use?%group.domain.name|":"|"123")'
        resolve(pattern)
