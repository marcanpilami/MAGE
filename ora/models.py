# coding: utf-8

from django.db import models

## MAGE imports
from ref.models import ComponentInstance
from ref.register import MageBehaviour

class UnixServer(ComponentInstance):
    marsu = models.CharField(max_length=100, verbose_name=u'Test field')

class OracleInstance(ComponentInstance):
    port = models.IntegerField(max_length=6, verbose_name=u"Port d'écoute du listener", default=1521)
    listener = models.CharField(max_length=100, verbose_name=u'Nom du listener', default='LISTENER')
    
    parents = {'base_server':'UnixServer'}
    
    class Meta:
        verbose_name = u'instance de base de données'
        verbose_name_plural = u'instances de base de données'



class OracleSchema(ComponentInstance):
    password = models.CharField(max_length=100, verbose_name=u'Mot de passe')
    
    def connectString(self):
        return '%s/%s@%s' % (self.name, self.password, self.instance_oracle.name)
    connectString.short_description = u"chaîne de connexion"
    connectString.admin_order_field = 'instance_name'
    
    parents = {'instance_oracle':'OracleInstance'}
    detail_template = 'ora/ora_schema_table.html'
    key = ('instance_name',)
    
    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.instance_oracle)
    
    class Meta:
        verbose_name = u'schéma Oracle'
        verbose_name_plural = u'schémas Oracle'
        

class OracleSchemaMage(MageBehaviour):
    pass

class OraclePackage(ComponentInstance):
    parents = {'parent_schema':'OracleSchema'}
    
    def __unicode__(self):
        return u'Package %s sur %s' % (self.class_name, self.parent_schema.name)
    
    class Meta:
        verbose_name = u'package PL/SQL'
        verbose_name_plural = u'packages PL/SQL'
