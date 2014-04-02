# coding: utf-8
'''
    @license: Apache License, Version 2.0
    @copyright: 2007-2013 Marc-Antoine Gouillart
    @author: Marc-Antoine Gouillart
'''

# MAGE imports
from ref import admin
from ref.admin import ComponentInstanceAdmin
from cpn.models import OracleInstance, OracleSchema, OraclePackage, \
    WasApplication, WasCluster, WasCell, WasNode, WasAS, MqQueueManagerParams, \
    MqQueueManager, ApplicationBinary, OsServer, OsAccount, GlassfishAS,\
    JqmCluster, JqmEngine, JqmBatch

## Server
class OsServerAdmin(ComponentInstanceAdmin):
    list_display = ('name', 'admin_account_login', 'os')
admin.site.register(OsServer, OsServerAdmin)

class OsAccountAdmin(ComponentInstanceAdmin):
    list_display = ('name', 'server')
admin.site.register(OsAccount, OsAccountAdmin)

## Oracle
class OracleInstanceAdmin(ComponentInstanceAdmin):
    list_display = ('name',)
    fieldsets = ComponentInstanceAdmin.fieldsets_generic + [('Spécifique instance Oracle', {'fields': ['port', 'listener', 'dba_acount', 'dba_password' ]})]
admin.site.register(OracleInstance, OracleInstanceAdmin)

class OracleSchemaAdmin(ComponentInstanceAdmin):
    list_display = ('name', 'instanciates', 'oracle_instance', 'connectString')
    fieldsets = ComponentInstanceAdmin.fieldsets_generic + [('Spécifique schéma', {'fields': ['password', 'service_name_to_use', 'dns_to_use' ]})]
admin.site.register(OracleSchema, OracleSchemaAdmin)

admin.site.register(OraclePackage, ComponentInstanceAdmin)

## WAS
admin.site.register(WasNode, ComponentInstanceAdmin)

class WasASAdmin(ComponentInstanceAdmin):
    list_display = ('name', 'http_port', 'https_port', 'deleted')
    fieldsets = ComponentInstanceAdmin.fieldsets_generic + [('Spécifique WAS', {'fields': ['http_port', 'https_port', 'dns_to_use' ]})]
admin.site.register(WasAS, WasASAdmin)


class WasApplicationAdmin(ComponentInstanceAdmin):
    fieldsets = ComponentInstanceAdmin.fieldsets_generic + [('Spécifique WAS', {'fields': ['context_root', 'client_url', ]})]
admin.site.register(WasApplication, WasApplicationAdmin)

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

admin.site.register(JqmCluster, ComponentInstanceAdmin)

class JqmEngineAdmin(ComponentInstanceAdmin):
    list_display = ('name', 'port',)
    fieldsets = ComponentInstanceAdmin.fieldsets_generic + [('Spécifique JQM', {'fields': ['port', 'jmx_registry_port','jmx_server_port', 'job_repo', 'dl_repo' ]})]
admin.site.register(JqmEngine, JqmEngineAdmin)

#class JqmBatchAdmin(ComponentInstanceAdmin):
    #list_display = ('name', 'port',)
    #fieldsets = ComponentInstanceAdmin.fieldsets_generic + [('Spécifique JQM', {'fields': ['port', 'job_repo', 'dl_repo' ]})]
admin.site.register(JqmBatch, ComponentInstanceAdmin)



## Misc
admin.site.register(GlassfishAS)
