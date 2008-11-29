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
        setParam(key = u'IMAGE_TYPE', value = u'png', 
                 default_value = u'png', 
                 description = u'Type d\'image des graphes générés (png, jpg, svg,...)')
        setParam(key = u'GRAPHVIZ_PRG', value = u'dot', 
                 default_value = u'dot', 
                 description = u'Programme graphviz utilisé pour générer les graphes (dot, neato, ...)')

        
        setParam(key = u'node_shape', value = 'ellipse', 
                 default_value = 'ellipse', 
                 description = u'valeur par défaut pour la forme des composants sur les graphes',
                 axis1 = 'presentation default')
        setParam(key = u'node_style', value = 'filled', 
                 default_value = 'filled', 
                 description = u'valeur par défaut pour le style des composants sur les graphes',
                 axis1 = 'presentation default')

## Listen to the syncdb signal
post_syncdb.connect(post_syncdb_handler, sender=models)