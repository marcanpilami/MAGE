# coding: utf-8

from django.db import models
from django.contrib import admin

from MAGE.ref.models import Component
from MAGE.ref.models import MageModelType


#########################
## Instance      
#########################
class OracleInstance(Component):
    port = models.IntegerField(max_length=6, verbose_name=u'Port d\'écoute du listener')
    listener = models.CharField(max_length=100, verbose_name=u'Nom du listener')
    
    def _getServer(self):
        return self.dependsOn.get(model__model='server').leaf
    server = property(_getServer)
    parents = {'server':'Server'}
    
    class Meta():
        verbose_name = u'Instance de base de données'
        verbose_name_plural = u'Instances de base de données'


class OracleInstanceAdmin(admin.ModelAdmin):
    ordering = ('instance_name',)
    list_display = ('instance_name', 'server',)
    search_fields = ('instance_name',)
    fieldsets = [
        ('Informations génériques',  {'fields': ['instance_name', 'dependsOn']}),
    ]



#########################
## Schema      
#########################
class OracleSchema(Component):
    password = models.CharField(max_length=100, verbose_name=u'Mot de passe')
    
    def _getInstance(self):
        return self.dependsOn.get(model__model='oracleinstance').leaf
    instance = property(_getInstance)
    def _getConnectString(self):
        return u'%s/%s@%s' %(self.instance_name, self.instance_name, self.instance.name)
    connectString = property(_getConnectString)
    
    parents = {'instance':'OracleInstance'}
    detail_template = 'ora_schema_details.html'
    
    class Meta():
        verbose_name = u'Schéma'

class OracleSchemaAdmin(admin.ModelAdmin):
    ordering = ('instance_name',)
    list_display = ('instance_name', 'instance',)
    search_fields = ('instance_name',)
    fieldsets = [
        ('Informations génériques',  {'fields': ['instance_name', 'class_name', 'environments', 'dependsOn']}),
    ]



#########################
## PDM      
#########################
class OracleMPD(Component):
    def _getSchema(self):
        return self.dependsOn.get(model__model='oracleschema').leaf
    schema = property(_getSchema) 
    
    class Meta():
        verbose_name = u'Modèle Physique de Données'
        verbose_name_plural = u'Modèles Physique de Données'



#########################
## Package      
#########################
class OraclePackage(Component):
    def _getSchema(self):
        return self.dependsOn.get(model__model='oracleschema').leaf
    schema = property(_getSchema) 
    parents = {'schema':'OracleSchema'}
    
    def __unicode__(self):
        return u'Package %s sur %s' %(self.class_name, self.schema.instance_name)
    
    class Meta():
        verbose_name = u'Package PL/SQL'
        verbose_name_plural = u'Packages PL/SQL'

class OraclePackageAdmin(admin.ModelAdmin):
    list_display = ('class_name', 'schema') 
    search_fields = ('class_name','dependsOn__name')
    fieldsets = [
        ('Informations génériques',  {'fields': ['class_name', 'environments', 'dependsOn']}),
    ]
    
    
    
#########################
## Registrations      
#########################
admin.site.register(OraclePackage, OraclePackageAdmin)
admin.site.register(OracleInstance, OracleInstanceAdmin)
admin.site.register(OracleSchema, OracleSchemaAdmin)
