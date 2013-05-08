# coding: utf-8

from django.db import models

# # MAGE imports
from ref.models import ComponentInstance



######################################################
## System (VM, LPAR, physical server, ...)
######################################################

class OsServer(ComponentInstance):
    admin_account_login = models.CharField(max_length=100, verbose_name=u'compte d\'administration', null=True, blank=True)
    admin_account_password = models.CharField(max_length=100, verbose_name=u'mot de passe d\'administration', null=True, blank=True)
    admin_account_private_key = models.CharField(max_length=2048, null=True, blank=True)
    os = models.CharField(max_length=10, choices=(('Win2003', 'Windows 2003'), ('RHEL4', 'Red Hat Enterprise Linux 4'), ('RHEL5', 'Red Hat Enterprise Linux 5'), ('SOL10', 'Solaris 10'), ('AIX', 'AIX'), ('Win2008R2', 'Windows 2008 R2'), ('Win2012', 'Windows 2012')))

    restricted_fields = ('admin_account_password',)
    include_in_default_envt_backup = False


class OsAccount(ComponentInstance):
    login = models.CharField(max_length=100, verbose_name=u'login')
    password = models.CharField(max_length=100, verbose_name=u'mot de passe', null=True, blank=True)
    public_key = models.CharField(max_length=2048, null=True, blank=True)
    private_key = models.CharField(max_length=2048, null=True, blank=True)
    
    restricted_fields = ('password', 'private_key',)
    parents = {'server': {'model': 'OsServer', 'cardinality': 1}}
    include_in_default_envt_backup = False


######################################################
## Oracle DB
######################################################

class OracleInstance(ComponentInstance):
    port = models.IntegerField(max_length=6, verbose_name=u"Port d'écoute du listener", default=1521)
    listener = models.CharField(max_length=100, verbose_name=u'Nom du listener', default='LISTENER')
    data_directory = models.CharField(max_length=254, verbose_name=u'répertoire data par défaut', blank=True, null=True)
    
    parents = {'server': {'model': 'OsServer', 'cardinality':1}}
    include_in_default_envt_backup = False
    
    class Meta:
        verbose_name = u'instance Oracle'
        verbose_name_plural = u'instances Oracle'

class OracleSchema(ComponentInstance):
    password = models.CharField(max_length=100, verbose_name=u'Mot de passe')
    service_name_to_use = models.CharField(max_length=30, verbose_name=u'SERVICE_NAME', blank=True, null=True)
    
    def connectString(self):
        if self.service_name_to_use:
            return '%s/%s@%s' % (self.name, self.password, self.service_name_to_use)
        else:
            return '%s/%s@%s' % (self.name, self.password, self.oracle_instance.name)
    connectString.short_description = u"chaîne de connexion"
    connectString.admin_order_field = 'name'
    
    parents = {'oracle_instance': {'model' : 'OracleInstance'}}
    detail_template = 'cpn/ora_schema_table.html'
    key = ('instance_name',)
    restricted_fields = ('password', 'private_key',)
    
    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.oracle_instance)
    
    class Meta:
        verbose_name = u'schéma Oracle'
        verbose_name_plural = u'schémas Oracle'

class OraclePackage(ComponentInstance):
    parents = {'parent_schema': {'model': 'OracleSchema'}}
    
    def __unicode__(self):
        return u'%s' % (self.name,)
    
    class Meta:
        verbose_name = u'package PL/SQL'
        verbose_name_plural = u'packages PL/SQL'



######################################################
# # Websphere AS
######################################################

class WasApplication(ComponentInstance):
    context_root = models.CharField(max_length=50, default='/')
    
    def __unicode__(self):
        return u'Application Java %s' % (self.name,)
    
    parents = {'was_cluster': {'model': 'WasCluster'}}
    include_in_default_envt_backup = False
    
    class Meta:
        verbose_name = u'application déployée sur un WAS'
        verbose_name_plural = u'applications déployées sur un WAS'

class WasCluster(ComponentInstance):
    parents = {'was_cell': {'model': 'WasCell'}}
    admin_user = models.CharField(max_length=50, verbose_name=u'utilisateur admin', blank=True, null=True)
    admin_user_password = models.CharField(max_length=50, verbose_name=u'mot de passe', blank=True, null=True)
    
    def __unicode__(self):
        return u'Cluster WAS %s' % (self.name,)
    
    class Meta:
        verbose_name = u'cluster WAS'
        verbose_name_plural = u'clusters WAS'
        
    detail_template = 'cpn/wascluster_schema_table.html'
    include_in_default_envt_backup = False

class WasCell(ComponentInstance):
    parents = {'manager_server': {'model': 'OsServer'}}
    manager_port = models.IntegerField(default=9060)
    manager_login = models.CharField(max_length=50, default='admin')
    manager_password = models.CharField(max_length=50, default='password')
    
    def __unicode__(self):
        return u'Cellule WAS %s' % (self.name,)
    
    include_in_default_envt_backup = False
    
    class Meta:
        verbose_name = u'cellule WAS'
        verbose_name_plural = u'cellules WAS'

class WasNode(ComponentInstance):
    parents = {'server': {'model': 'OsServer'}, 'was_cell': {'model': 'WasCell'}}
    include_in_default_envt_backup = False
    
    def __unicode__(self):
        return u'Noeud WAS %s' % (self.name,)
    
    class Meta:
        verbose_name = u'noeud WAS'
        verbose_name_plural = u'noeuds WAS'
    
class WasAS(ComponentInstance):
    parents = {'was_node': {'model': 'WasNode'}, 'was_cluster': {'model': 'WasCluster'}, 'server': {'model': 'OsServer'}}
    http_port = models.IntegerField(default=8080)
    https_port = models.IntegerField(default=8081)
    
    def __unicode__(self):
        return u'AS WAS %s' % (self.name,)
    
    class Meta:
        verbose_name = u'JVM WAS'
        verbose_name_plural = u'JVMs WAS'
    
    detail_template = 'cpn/wasas_schema_table.html'
    include_in_default_envt_backup = False
        
class GlassfishAS(ComponentInstance):
    parents = {'server': {'model': 'OsServer'}}
    include_in_default_envt_backup = False
    
    def __unicode__(self):
        return u'Glassfish serveur sur %s' % (self.server.name)
    
    class Meta:
        verbose_name = u'Glassfish AS'
        verbose_name_plural = u'Glassfish ASs'
        


######################################################
# # Websphere MQ (MQ Series)
######################################################

class MqQueueManager(ComponentInstance):
    port = models.IntegerField(max_length=6)
    adminChannel = models.CharField(max_length=100, verbose_name='Canal admin')
    
    parents = {'server': {'model': 'UnixServer'}}
    include_in_default_envt_backup = False
    
    class Meta:
        verbose_name = u'Gestionnaire de files'
        verbose_name_plural = u'Gestionnaires de files'

class MqQueueManagerParams(ComponentInstance):
    parents = {'qm': {'model': 'MqQueueManager'}}
    include_in_default_envt_backup = False
    
    def __unicode__(self):
        return "Params %s sur %s" % (self.instanciates.name, self.qm.name)
    
    class Meta:
        verbose_name = u'Paramétrage MQ Series'
        verbose_name_plural = u'Paramétrages MQ Series'
    
    detail_template = 'cpn/mqp_schema_table.html'
        
    

######################################################
# # Programs (batchs, services...)
######################################################

class ApplicationBinary(ComponentInstance):
    parents = {'server': {'model': 'OsServer'}}
    root_directory = models.CharField(max_length=255, null=True)
    
    def __unicode__(self):
        return "programme(s) sur %s" % (self.server.name)
    
    class Meta:
        verbose_name = u'ensemble de programmes'
        verbose_name_plural = u'ensembles de programmes'
    
