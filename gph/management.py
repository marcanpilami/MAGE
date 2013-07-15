# coding: utf-8

"""
    Graph module initialisation file.
    It creates some parameters on initialisation.
    
    @license: Apache License, Version 2.0
    @copyright: 2007-2013 Marc-Antoine Gouillart
    @author: Marc-Antoine Gouillart
"""

## Python imports

## Django imports
from django.db.models.signals import post_syncdb

## MAGE imports
import models
from prm.models import setOrCreateParam

def post_syncdb_handler(sender, **kwargs):
    # Create parameters
    setOrCreateParam(key = u'IMAGE_TYPE', value = u'png', 
             default_value = u'png', 
             description = u'Type d\'image des graphes générés (png, jpg, svg,...)')
    setOrCreateParam(key = u'GRAPHVIZ_PRG', value = u'dot', 
             default_value = u'dot', 
             description = u'Programme graphviz utilisé pour générer les graphes (dot, neato, ...)')
    
    setOrCreateParam(key = u'node_shape', value = 'ellipse', 
             default_value = 'ellipse', 
             description = u'valeur par défaut pour la forme des composants sur les graphes',
             axis1 = 'presentation default')
    setOrCreateParam(key = u'node_style', value = 'filled', 
             default_value = 'filled', 
             description = u'valeur par défaut pour le style des composants sur les graphes',
             axis1 = 'presentation default')

## Listen to the syncdb signal
post_syncdb.connect(post_syncdb_handler, sender=models)
