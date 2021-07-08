# coding: utf-8

'''
Created on 11 août 2014

@author: Marc-Antoine
'''

from django.apps import AppConfig

class RefAppConfig(AppConfig):
    name='ref'
    verbose_name = u'Gestion du référentiel'
    
    def ready(self):
        import ref.cache
