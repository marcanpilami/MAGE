# coding: utf-8
'''
    @license: Apache License, Version 2.0
    @copyright: 2007-2013 Marc-Antoine Gouillart
    @author: Marc-Antoine Gouillart
'''

## Python imports
import importlib

## Django imports
from django.db.models.signals import post_syncdb

## MAGE imports
import models
from scm.models import PackageCheckerBaseImpl, __package_checker_handler

def post_syncdb_handler(sender, **kwargs):
    ## Load all checkers
    from MAGE.settings import INSTALLED_APPS
    for app in [ i for i in INSTALLED_APPS if not i.startswith('django.')]:
        try:
            module = importlib.import_module(app + '.checkers')
            for value in module.__dict__.values():
                try:
                    if value.__class__ is type and value.__base__ is PackageCheckerBaseImpl:
                        __package_checker_handler.register(value)
                except AttributeError:
                    continue
        except ImportError:
            continue
    __package_checker_handler.end_sync()


## Listen to the syncdb signal
post_syncdb.connect(post_syncdb_handler, sender=models)
