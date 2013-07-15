# coding: utf-8
'''
Created on 10 mars 2013

@author: Marc-Antoine
'''

## Python imports

## Django imports
from django.db.models.signals import post_syncdb

## MAGE imports
import models
from ref.models import Convention
from ref.conventions import nc_sync_naming_convention

def post_syncdb_handler(sender, **kwargs):
    ## Create default convention & update existing ones
    if Convention.objects.count() == 0:
        default = Convention(name = 'default convention')
        default.save()
    for c in Convention.objects.all():
        nc_sync_naming_convention(c)

## Listen to the syncdb signal
post_syncdb.connect(post_syncdb_handler, sender=models)