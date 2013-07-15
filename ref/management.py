# coding: utf-8
'''
    @license: Apache License, Version 2.0
    @copyright: 2007-2013 Marc-Antoine Gouillart
    @author: Marc-Antoine Gouillart
'''

## Python imports

## Django imports
from django.db.models.signals import post_syncdb

## MAGE imports
import models
from prm.models import setOrCreateParam

def post_syncdb_handler(sender, **kwargs):
    ## Create or update parameters
    
    ## General parameters that should never be removed...
    setOrCreateParam(key=u'LINK_COLORS', value=u'#004D60,#1B58B8,#DE4AAD,#D39D09,#AD103C,#180052',
             default_value=u'#004D60,#1B58B8,#DE4AAD',
             description=u'Couleurs des cases de la page d\'accueil')
    
    setOrCreateParam(key=u'MODERN_COLORS', value=u'#004A00,#61292B,#180052,#AD103C,#004D60,#1B58B8,#DE4AAD',
             default_value=u'#004A00,#61292B,#180052,#AD103C,#004D60,#1B58B8,#DE4AAD',
             description=u'Couleurs des cases de la page d\'accueil')

    
    
## Listen to the syncdb signal
post_syncdb.connect(post_syncdb_handler, sender=models)
