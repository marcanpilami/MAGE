# coding: utf-8
'''
    @license: Apache License, Version 2.0
    @copyright: 2007-2013 Marc-Antoine Gouillart
    @author: Marc-Antoine Gouillart
'''

# Django imports
from django.db import models

# # MAGE imports
from ref.models import ComponentInstance


######################################################
# # System (VM, LPAR, physical server, ...)
######################################################

class OsServer(ComponentInstance):
    admin_account_login = models.CharField(max_length=100, verbose_name=u'compte d\'administration', null=True, blank=True)
    admin_account_password = models.CharField(max_length=100, verbose_name=u'mot de passe d\'administration', null=True, blank=True)
    admin_account_private_key = models.CharField(max_length=2048, null=True, blank=True)
    os = models.CharField(max_length=10, choices=(('Win2003', 'Windows 2003'), ('RHEL4', 'Red Hat Enterprise Linux 4'), ('RHEL5', 'Red Hat Enterprise Linux 5'), ('SOL10', 'Solaris 10'), ('AIX', 'AIX'), ('Win2008R2', 'Windows 2008 R2'), ('Win2012', 'Windows 2012')))

    restricted_fields = ('admin_account_password',)
    include_in_default_envt_backup = False
    
    class Meta:
        verbose_name = 'serveur'


class OsAccount(ComponentInstance):
    password = models.CharField(max_length=100, verbose_name=u'mot de passe', null=True, blank=True)
    public_key = models.CharField(max_length=2048, null=True, blank=True)
    private_key = models.CharField(max_length=2048, null=True, blank=True)
    
    restricted_fields = ('password', 'private_key',)
    parents = {'server': {'model': 'OsServer', 'cardinality': 1}}
    include_in_default_envt_backup = False
    
    def __unicode__(self):
        return "%s on %s" % (self.name, self.server.name if self.server else 'no server')
    
    class Meta:
        verbose_name = u'compte OS'
        verbose_name_plural = u'comptes OS'


######################################################
# # Oracle DB
######################################################

class OracleInstance(ComponentInstance):
    port = models.IntegerField(max_length=6, verbose_name=u"Port d'écoute du listener", default=1521)
    listener = models.CharField(max_length=100, verbose_name=u'Nom du listener', default='LISTENER')
    data_directory = models.CharField(max_length=254, verbose_name=u'répertoire data par défaut', blank=True, null=True)
    dba_acount = models.CharField(max_length=20, verbose_name=u'compte DBA', default='system', blank=True, null=True)
    dba_password = models.CharField(max_length=100, verbose_name=u'mot de passe compte DBA', blank=True, null=True)
    
    parents = {'server': {'model': 'OsServer', 'cardinality':1}}
    include_in_default_envt_backup = False
    
    class Meta:
        verbose_name = u'instance Oracle'
        verbose_name_plural = u'instances Oracle'

class OracleSchema(ComponentInstance):
    password = models.CharField(max_length=100, verbose_name=u'mot de passe')
    service_name_to_use = models.CharField(max_length=30, verbose_name=u'SERVICE_NAME', blank=True, null=True)
    dns_to_use = models.CharField(max_length=100, verbose_name=u'database DNS', blank=True, null=True)
    
    def connectString(self):
        if self.service_name_to_use:
            return '%s/%s@%s' % (self.name, self.password, self.service_name_to_use)
        else:
            return '%s/%s@%s' % (self.name, self.password, self.oracle_instance.name)
    connectString.short_description = u"chaîne de connexion"
    connectString.admin_order_field = 'name'
    connection_string = property(connectString)
    
    def jdbcString(self):
        if self.service_name_to_use and self.dns_to_use:
            return 'jdbc:oracle:thin:@%s:%s/%s' % (self.dns_to_use, self.oracle_instance.port, self.service_name_to_use)
        elif self.service_name_to_use:
            return 'jdbc:oracle:thin:@%s:%s/%s' % (self.oracle_instance.server.name, self.oracle_instance.port, self.service_name_to_use)
        elif self.dns_to_use:
            return 'jdbc:oracle:thin:@%s:%s:%s' % (self.dns_to_use, self.oracle_instance.port, self.oracle_instance.name)
        else:
            return 'jdbc:oracle:thin:@%s:%s:%s' % (self.oracle_instance.server.name, self.oracle_instance.port, self.oracle_instance.name)
    jdbcString.short_description = u"chaîne JDBC"
    jdbcString.admin_order_field = 'name'
    
    parents = {'oracle_instance': {'model' : 'OracleInstance'}}
    detail_template = 'cpn/ora_schema_table.html'
    key = ('instance_name',)
    restricted_fields = ('password', 'private_key', 'connection_string')
    
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
    context_root = models.CharField(max_length=50, default='/', null=False)
    client_url = models.CharField(max_length=100, verbose_name=u'access URL', blank=True, null=True)
    
    def __unicode__(self):
        return u'Application Java %s' % (self.name,)
    
    def url(self):
        if self.client_url:
            return self.client_url
        elif self.was_cluster.subscribers.filter(model__model='wasas')[0].leaf.dns_to_use:
            return 'http://%s:%s%s' % (self.was_cluster.subscribers.filter(model__model='wasas')[0].leaf.dns_to_use,
                                        self.was_cluster.subscribers.filter(model__model='wasas')[0].leaf.http_port,
                                        self.context_root)
        else:
            return 'http://%s:%s%s' % (self.was_cluster.subscribers.filter(model__model='wasas')[0].leaf.was_node.server.name,
                                       self.was_cluster.subscribers.filter(model__model='wasas')[0].leaf.http_port,
                                       self.context_root)
    url.short_description = u"adresse de l'application"
    url.admin_order_field = 'name'
    
    parents = {'was_cluster': {'model': 'WasCluster'}}
    include_in_default_envt_backup = False
    detail_template = 'cpn/wasapp_table.html'
    
    class Meta:
        verbose_name = u'application sur un WAS'
        verbose_name_plural = u'applications sur un WAS'

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
    parents = {'was_node': {'model': 'WasNode'}, 'was_cluster': {'model': 'WasCluster'}}
    http_port = models.IntegerField(default=9080)
    https_port = models.IntegerField(default=8081)
    dns_to_use = models.CharField(max_length=100, verbose_name=u'DNS alias', blank=True, null=True)
    
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
    
    parents = {'server': {'model': 'OsServer'}}
    include_in_default_envt_backup = False
    
    class Meta:
        verbose_name = u'Gestionnaire de files'
        verbose_name_plural = u'Gestionnaires de files'
        
    detail_template = 'cpn/mqm_table.html'

class MqQueueManagerParams(ComponentInstance):
    parents = {'qm': {'model': 'MqQueueManager'}}
    include_in_default_envt_backup = False
    
    def __unicode__(self):
        if self.instanciates and self.qm:
            return "files %s" % (self.instanciates.name, self.qm.name)
        else:
            return "files"
    
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


class JqmCluster(ComponentInstance):
    parents = {'schema': {'model': 'OracleSchema'} }
    
    class Meta:
        verbose_name = u'cluster JQM'
        verbose_name_plural = u'clusters JQM'    

class JqmEngine(ComponentInstance):
    parents = {'cluster': {'model': 'JqmCluster'}, 'server':{'model': 'OsServer'} }
    port = models.IntegerField(max_length = 6, null = False, default = 1789)
    dl_repo = models.CharField(max_length=255, null=True, blank=True)
    job_repo = models.CharField(max_length=255, null=True, blank=True)
    
    class Meta:
        verbose_name = u'moteur JQM'
        verbose_name_plural = u'moteurs JQM'
    
class JqmBatch(ComponentInstance):
    parents = {'cluster': {'model': 'JqmCluster'} }
    
    class Meta:
        verbose_name = u'batch tournant dans JQM'
        verbose_name_plural = u'batchs tournant dans JQM'

