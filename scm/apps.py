# coding: utf-8

from django.apps import AppConfig
from django.db.models.signals import post_migrate


class ScmAppConfig(AppConfig):
    name='scm'
    verbose_name = u'Gestion de Configuration Logicielle'

    def ready(self):
        from scm.management import post_migrate_handler
        post_migrate.connect(post_migrate_handler, sender=self)
