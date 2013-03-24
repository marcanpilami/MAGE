# coding: utf-8
'''
Created on 17 mars 2013

@author: Marc-Antoine
'''

from django.contrib import admin
from ref.admin import ComponentInstanceAdmin
from cpn.models import OracleInstance, OracleSchema, OraclePackage, \
    WasApplication, WasCluster, WasCell, WasNode, WasAS, MqQueueManagerParams, \
    MqQueueManager, ApplicationBinary

## Oracle
class OracleInstanceAdmin(ComponentInstanceAdmin):
    list_display = ('name',)
    fieldsets = ComponentInstanceAdmin.fieldsets_generic + [('Spécifique instance Oracle', {'fields': ['port', 'listener', ]})]
admin.site.register(OracleInstance, OracleInstanceAdmin)

class OracleSchemaAdmin(ComponentInstanceAdmin):
    list_display = ('name', 'instanciates', 'oracle_instance', 'connectString')
    fieldsets = ComponentInstanceAdmin.fieldsets_generic + [('Spécifique schéma', {'fields': ['password', 'service_name_to_use', ]})]
admin.site.register(OracleSchema, OracleSchemaAdmin)

admin.site.register(OraclePackage, ComponentInstanceAdmin)

## WAS
admin.site.register(WasApplication, ComponentInstanceAdmin)
admin.site.register(WasNode, ComponentInstanceAdmin)
admin.site.register(WasAS, ComponentInstanceAdmin)

class WasClusterAdmin(ComponentInstanceAdmin):
    list_display = ('name', 'was_cell')
    fieldsets = ComponentInstanceAdmin.fieldsets_generic + [('Spécifique WAS', {'fields': ['admin_user', 'admin_user_password', ]})]
admin.site.register(WasCluster, WasClusterAdmin)

class WasCellAdmin(ComponentInstanceAdmin):
    list_display = ('name',)
    fieldsets = ComponentInstanceAdmin.fieldsets_generic + [('Spécifique WAS', {'fields': ['manager_login', 'manager_password', 'manager_port', ]})]
admin.site.register(WasCell, WasCellAdmin)

## MQ Series
admin.site.register(MqQueueManagerParams, ComponentInstanceAdmin)

class MqQueueManagerAdmin(ComponentInstanceAdmin):
    list_display = ('name', 'port', 'adminChannel',)
    fieldsets = ComponentInstanceAdmin.fieldsets_generic + [('Spécifique MQ', {'fields': ['adminChannel', 'port', ]})]
admin.site.register(MqQueueManager, MqQueueManagerAdmin)

## Batch
class ApplicationBinaryAdmin(ComponentInstanceAdmin):
    list_display = ('name', 'root_directory', 'server',)
    fieldsets = ComponentInstanceAdmin.fieldsets_generic + [('Spécifique binaires', {'fields': ['root_directory', ]})]
admin.site.register(ApplicationBinary, ApplicationBinaryAdmin)
