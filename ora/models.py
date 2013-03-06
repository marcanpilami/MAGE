# coding: utf-8

from django.db import models

## MAGE imports
from ref.models import ComponentInstance

class DebugServer(ComponentInstance):
    marsu = models.CharField(max_length=100, verbose_name=u'Test field')

class OracleInstance(ComponentInstance):
    port = models.IntegerField(max_length=6, verbose_name=u"Port d'écoute du listener")
    listener = models.CharField(max_length=100, verbose_name=u'Nom du listener')
    
    parents = {'base_server':'DebugServer'}
    
    class Meta:
        verbose_name = u'instance de base de données'
        verbose_name_plural = u'instances de base de données'

