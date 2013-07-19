# coding: utf-8
'''
    @license: Apache License, Version 2.0
    @copyright: 2007-2013 Marc-Antoine Gouillart
    @author: Marc-Antoine Gouillart
'''

## Python imports

## Django imports
from django.db.models.signals import post_syncdb
from django.contrib.auth.models import Group, User, Permission

## MAGE imports
import models
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
        
    ## Parameters
    setOrCreateParam(key = u'APPLY_MERGE_LIMIT', value = u'60', 
                     default_value = u'60', 
                     description = u'Si deux éléments d\'une même livraison sont appliquées sur un même environnement à moins de n minutes, c\'est une même installation. 0 pour désactiver la fusion.')
    setOrCreateParam(key = u'BACKUP_MERGE_LIMIT', value = u'180', 
                     default_value = u'180', 
                     description = u'Si deux éléments d\'un même environnements sont sauvegardés à moins de n minutes, c\'est un même backupset. 0 pour désactiver la fusion.')
    
    
    setOrCreateParam(key = u'DELIVERY_FORM_DATA_FIELDS', value = u'0', 
                     default_value = u'0', 
                     description = u'nombre de champs data à afficher dans le formulaire de bon de livraison')
        
    setOrCreateParam(key = u'DELIVERY_FORM_DATAFILE_MODE', value = u'ONE_FILE_PER_ITEM', 
                     default_value = u'ONE_FILE_PER_ITEM', 
                     description = u'ONE_FILE_PER_SET, ONE_FILE_PER_ITEM, NO_UPLOAD')
        

## Listen to the syncdb signal
post_syncdb.connect(post_syncdb_handler, sender=models)