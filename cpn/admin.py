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
    MqQueueManager, ApplicationBinary, OsServer, OsAccount, GlassfishAS, \
    JqmCluster, JqmEngine, JqmBatch, JBossHost, JBossAS, JBossApplication, \
    JBossGroup, JBossDomain

# # Server
class OsServerAdmin(ComponentInstanceAdmin):
    list_display = ('name', 'admin_account_login', 'os')
    fieldsets = ComponentInstanceAdmin.fieldsets_generic + [('Spécifique serveur', {'fields': ['admin_account_login', 'admin_account_password', 'admin_account_private_key', 'os' ]})]
admin.site.register(OsServer, OsServerAdmin)

class OsAccountAdmin(ComponentInstanceAdmin):
    list_display = ('name', 'server')
admin.site.register(OsAccount, OsAccountAdmin)

# # Oracle
class OracleInstanceAdmin(ComponentInstanceAdmin):
    list_display = ('name', 'server', 'port')
    fieldsets = ComponentInstanceAdmin.fieldsets_generic + [('Spécifique instance Oracle', {'fields': ['port', 'listener', 'dba_acount', 'dba_password' ]})]
admin.site.register(OracleInstance, OracleInstanceAdmin)

class OracleSchemaAdmin(ComponentInstanceAdmin):
    list_display = ('name', 'instanciates', 'oracle_instance', 'connectString')
    fieldsets = ComponentInstanceAdmin.fieldsets_generic + [('Spécifique schéma', {'fields': ['password', 'service_name_to_use', 'dns_to_use' ]})]
admin.site.register(OracleSchema, OracleSchemaAdmin)

admin.site.register(OraclePackage, ComponentInstanceAdmin)

# # WAS
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
    list_display = ('name', 'admin_url')
    fieldsets = ComponentInstanceAdmin.fieldsets_generic + [('Spécifique WAS', {'fields': ['manager_login', 'manager_password', 'manager_port', ]})]
admin.site.register(WasCell, WasCellAdmin)

# # MQ Series
admin.site.register(MqQueueManagerParams, ComponentInstanceAdmin)

class MqQueueManagerAdmin(ComponentInstanceAdmin):
    list_display = ('name', 'port', 'adminChannel', 'first_environment')
    fieldsets = ComponentInstanceAdmin.fieldsets_generic + [('Spécifique MQ', {'fields': ['adminChannel', 'port', ]})]
admin.site.register(MqQueueManager, MqQueueManagerAdmin)

# # Batch
class ApplicationBinaryAdmin(ComponentInstanceAdmin):
    list_display = ('name', 'root_directory', 'server',)
    fieldsets = ComponentInstanceAdmin.fieldsets_generic + [('Spécifique binaires', {'fields': ['root_directory', ]})]
admin.site.register(ApplicationBinary, ApplicationBinaryAdmin)

class JqmClusterAdmin(ComponentInstanceAdmin):
    list_display = ('name', 'schema', 'deleted')
    fieldsets = ComponentInstanceAdmin.fieldsets_generic
admin.site.register(JqmCluster, JqmClusterAdmin)

class JqmEngineAdmin(ComponentInstanceAdmin):
    list_display = ('name', 'port', 'jmx_registry_port', 'cluster', 'server', 'deleted')
    fieldsets = ComponentInstanceAdmin.fieldsets_generic + [('Spécifique JQM', {'fields': ['port', 'jmx_registry_port', 'jmx_server_port', 'job_repo', 'dl_repo' ]})]
admin.site.register(JqmEngine, JqmEngineAdmin)

class JqmBatchAdmin(ComponentInstanceAdmin):
    list_display = ('name', 'cluster', 'deleted')
    fieldsets = ComponentInstanceAdmin.fieldsets_generic
admin.site.register(JqmBatch, JqmBatchAdmin)


# # JBoss
class JBossHostAdmin(ComponentInstanceAdmin):
    list_display = ('name', 'server', 'jboss_domain', 'deleted')
    fieldsets = ComponentInstanceAdmin.fieldsets_generic
admin.site.register(JBossHost, JBossHostAdmin)

class JBossASAdmin(ComponentInstanceAdmin):
    list_display = ('name', 'jboss_group', 'jboss_host', 'port_shift', 'http_port', 'deleted')
    fieldsets = ComponentInstanceAdmin.fieldsets_generic + [('Spécifique JBoss', {'fields': ['port_shift', 'dns_to_use' ]})]
admin.site.register(JBossAS, JBossASAdmin)

class JBossApplicationAdmin(ComponentInstanceAdmin):
    list_display = ('name', 'instanciates', 'url', 'jboss_group', 'deleted',)
    fieldsets = ComponentInstanceAdmin.fieldsets_generic + [('Spécifique JBoss', {'fields': ['context_root', 'client_url', ]})]
admin.site.register(JBossApplication, JBossApplicationAdmin)

class JBossGroupAdmin(ComponentInstanceAdmin):
    list_display = ('name', 'profile', 'resolved_admin_login')
    fieldsets = ComponentInstanceAdmin.fieldsets_generic + [('Spécifique JBoss', {'fields': ['admin_login', 'admin_password', 'profile', ]})]
admin.site.register(JBossGroup, JBossGroupAdmin)

class JBossDomainAdmin(ComponentInstanceAdmin):
    list_display = ('name', 'base_http_port', 'base_native_admin_port', 'admin_user', 'domain_controller')
    fieldsets = ComponentInstanceAdmin.fieldsets_generic + [('Spécifique JBoss', {'fields': ['admin_user', 'admin_password', 'base_http_port', 'base_https_port', 'base_web_admin_port', 'base_native_admin_port']})]
admin.site.register(JBossDomain, JBossDomainAdmin)

# # Misc
admin.site.register(GlassfishAS)
