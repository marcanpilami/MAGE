# coding: utf-8
'''
Created on 10 mars 2013

@author: Marc-Antoine
'''

## Python imports

## Django imports
from django.db.models.signals import post_syncdb
from django.contrib.auth.models import Group, User, Permission

## MAGE imports
import models

def post_syncdb_handler(sender, **kwargs):
    ## Create DEV group & first user
    if not Group.objects.filter(name='DEV').exists():
        devgroup = Group(name='DEV')
        devgroup.save()
        p = Permission.objects.get(content_type__app_label = 'scm', codename = 'add_delivery')
        devgroup.permissions.add(p)
        
        dev = User.objects.create_user(username = 'dev', email = None, password = 'dev')
        dev.save()
        
        dev.groups.add(devgroup)
        

## Listen to the syncdb signal
post_syncdb.connect(post_syncdb_handler, sender=models)