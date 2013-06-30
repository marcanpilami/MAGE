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
from scm.models import InstallationMethod
from ref.models import Convention
from ref.conventions import nc_sync_naming_convention
from prm.models import setOrCreateParam

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
        
    ## Create default convention & update existing ones
    if Convention.objects.count() == 0:
        default = Convention(name = 'default convention')
        default.save()
    for c in Convention.objects.all():
        nc_sync_naming_convention(c)
        
    ## Parameters
    setOrCreateParam(key = u'APPLY_MERGE_LIMIT', value = u'60', 
                     default_value = u'60', 
                     description = u'Si deux éléments d\'une même livraison sont appliquées sur un même environnement à moins de n minutes, c\'est une même installation')
        

## Listen to the syncdb signal
post_syncdb.connect(post_syncdb_handler, sender=models)