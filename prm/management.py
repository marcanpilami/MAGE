# coding: utf-8

## Python imports

## Django imports
from django.db.models.signals import post_syncdb

## MAGE imports
import models
from MAGE.prm.models import setParam, getMyParams

def post_syncdb_handler(sender, **kwargs):
    # Create parameters
    if getMyParams().count() == 0:
        setParam(key = u'MARSU1', value = u'VALEUR 1', 
                 default_value = u'VALEUR DEFAUT 1', 
                 description = u'Paramètre d\'essai 1')
        setParam(key = u'MARSU2', value = u'VALEUR 2', 
                 default_value = u'VALEUR DEFAUT 2')
        setParam(key = u'MARSU3', value = u'VALEUR 2')
    
    # Do something else...

## Listen to the syncdb signal
post_syncdb.connect(post_syncdb_handler, sender=models)