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
from ref.models import Convention
from ref.conventions import nc_sync_naming_convention
from scm.models import PackageCheckerBaseImpl, __package_checker_handler

def post_syncdb_handler(sender, **kwargs):
    ## Create default convention & update existing ones
    if Convention.objects.count() == 0:
        default = Convention(name = 'default convention')
        default.save()
    for c in Convention.objects.all():
        nc_sync_naming_convention(c)
        
    ## Load all checkers        
    from MAGE.settings import INSTALLED_APPS
    for app in [ i for i in INSTALLED_APPS if not i.startswith('django.')]:
        try:
            module = importlib.import_module(app + '.models')
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