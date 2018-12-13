# coding: utf-8

'''
Created on 11 août 2014

@author: Marc-Antoine
'''

from django.apps import AppConfig
from django.db.models.signals import post_migrate


class RefAppConfig(AppConfig):
    name='ref'
    verbose_name = u'Gestion du référentiel'
    
    def ready(self):
        import cache
        from ref.management import post_migrate_handler

        ## Listen to the syncdb signal
        post_migrate.connect(post_migrate_handler, sender=self)
