# coding: utf-8

## Django imports
from django.db import models
from django.contrib import admin

## MAGE imports
from MAGE.ref.models import Component
from MAGE.ref.admin import ComponentAdmin


#########################
## Instance      
#########################
class OracleInstance(Component):
    port = models.IntegerField(max_length=6, verbose_name=u"Port d'écoute du listener")
    listener = models.CharField(max_length=100, verbose_name=u'Nom du listener')
    
    parents = {'base_server':'Server'}
    
    class Meta:
        verbose_name = u'instance de base de données'
        verbose_name_plural = u'instances de base de données'


class OracleInstanceAdmin(ComponentAdmin):
    ordering = ('instance_name',)
    list_display = ('instance_name',)# 'server',)
    search_fields = ('instance_name',)
    fieldsets = [
        ('Informations génériques',  {'fields': ['instance_name', 'dependsOn']}),
        ('Informations Oracle',  {'fields': ['port', 'listener']}),
    ]



#########################
## Schema      
#########################
class OracleSchema(Component):
    password = models.CharField(max_length=100, verbose_name=u'Mot de passe')
    
    def connectString(self):
        return '%s/%s@%s' %(self.instance_name, self.password, self.instance_oracle.instance_name)
    connectString.short_description = u"chaîne de connexion"
    connectString.admin_order_field = 'instance_name'
    
    parents = {'instance_oracle':'OracleInstance'}
    detail_template = 'ora_schema_details.html'
    
    def __unicode__(self):
        return u"%s (%s sur %s)" %(self.instance_name, self.instance_oracle, self.instance_oracle.base_server)
    
    class Meta:
        verbose_name = u'schéma Oracle'
        verbose_name_plural = u'schémas Oracle'

class OracleSchemaAdmin(ComponentAdmin):
    list_display = ('instance_name','class_name', 'instance_oracle','connectString')
    fieldsets = ComponentAdmin.fieldsets_generic + [('Spécifique schéma', {'fields': ['password',]})]



#########################
## PDM      
#########################
class OracleMPD(Component):
    def _getSchema(self):
        return self.dependsOn.get(model__model='oracleschema').leaf
    schema = property(_getSchema) 
    
    class Meta:
        verbose_name = u'Modèle Physique de Données'
        verbose_name_plural = u'Modèles Physique de Données'



#########################
## Package      
#########################
class OraclePackage(Component):
    parents = {'parent_schema':'OracleSchema'}
    
    def __unicode__(self):
        return u'Package %s sur %s' %(self.class_name, self.parent_schema.instance_name)
    
    class Meta:
        verbose_name = u'package PL/SQL'
        verbose_name_plural = u'packages PL/SQL'

class OraclePackageAdmin(ComponentAdmin):
    list_display = ('class_name','parent_schema',) 
    fieldsets = [ ('Informations génériques',  {'fields': ['class_name', 'environments', 'dependsOn',]}),  ]
    
    
#########################
## Registrations      
#########################
admin.site.register(OraclePackage, OraclePackageAdmin)
admin.site.register(OracleInstance, OracleInstanceAdmin)
admin.site.register(OracleSchema, OracleSchemaAdmin)
