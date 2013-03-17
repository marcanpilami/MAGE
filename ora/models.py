# coding: utf-8

from django.db import models

# # MAGE imports
from ref.models import ComponentInstance
from ref.register import MageBehaviour



######################################################
# # System (VM, LPAR, physical server, ...)
######################################################

class UnixServer(ComponentInstance):
    marsu = models.CharField(max_length=100, verbose_name=u'Test field')



######################################################
# # Oracle DB
######################################################

class OracleInstance(ComponentInstance):
    port = models.IntegerField(max_length=6, verbose_name=u"Port d'écoute du listener", default=1521)
    listener = models.CharField(max_length=100, verbose_name=u'Nom du listener', default='LISTENER')
    
    parents = {'base_server':'UnixServer'}
    
    class Meta:
        verbose_name = u'instance de base de données'
        verbose_name_plural = u'instances de base de données'

class OracleSchema(ComponentInstance):
    password = models.CharField(max_length=100, verbose_name=u'Mot de passe')
    service_name_to_use = models.CharField(max_length=30, verbose_name=u'SERVICE_NAME', blank = True, null=True)
    
    def connectString(self):
        if self.service_name_to_use:
            return '%s/%s@%s' % (self.name, self.password, self.service_name_to_use)
        else:
            return '%s/%s@%s' % (self.name, self.password, self.instance_oracle.name)
    connectString.short_description = u"chaîne de connexion"
    connectString.admin_order_field = 'name'
    
    parents = {'instance_oracle':'OracleInstance'}
    detail_template = 'ora/ora_schema_table.html'
    key = ('instance_name',)
    
    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.instance_oracle)
    
    class Meta:
        verbose_name = u'schéma Oracle'
        verbose_name_plural = u'schémas Oracle'

class OraclePackage(ComponentInstance):
    parents = {'parent_schema':'OracleSchema'}
    
    def __unicode__(self):
        return u'Package %s sur %s' % (self.name, self.parent_schema.name)
    
    class Meta:
        verbose_name = u'package PL/SQL'
        verbose_name_plural = u'packages PL/SQL'



######################################################
# # Websphere AS
######################################################

class WasApplication(ComponentInstance):
    parents = {'was_cluster':'WasCluster'}
    
    def __unicode__(self):
        return u'Application Java %s sur cluster WAS %s' % (self.name, self.was_cluster.name)
    
    class Meta:
        verbose_name = u'application déployée sur un WAS'
        verbose_name_plural = u'applications déployées sur un WAS'

class WasCluster(ComponentInstance):
    parents = {'was_cell': 'WasCell'}
    admin_user = models.CharField(max_length=50, verbose_name=u'utilisateur admin', blank = True, null=True)
    admin_user_password = models.CharField(max_length=50, verbose_name=u'mot de passe', blank = True, null=True)
    
    def __unicode__(self):
        return u'Cluster WAS %s de la cellule %s' % (self.name, self.was_cell.name)
    
    class Meta:
        verbose_name = u'cluster WAS'
        verbose_name_plural = u'clusters WAS'
        
    detail_template = 'ora/wascluster_schema_table.html'

class WasCell(ComponentInstance):
    parents = {'manager_server': 'UnixServer'}
    manager_port = models.IntegerField(default=9060)
    manager_login = models.CharField(max_length=50, default='admin')
    manager_password = models.CharField(max_length=50, default='password')
    
    def __unicode__(self):
        return u'Cellule WAS %s - manager sur %s' % (self.name, self.manager_server)
    
    class Meta:
        verbose_name = u'cellule WAS'
        verbose_name_plural = u'cellules WAS'

class WasNode(ComponentInstance):
    parents = {'server': 'UnixServer', 'was_cell': 'WasCell'}
    
    def __unicode__(self):
        return u'Noeud WAS %s de la cellule %s' % (self.name, self.was_cell.name)
    
    class Meta:
        verbose_name = u'noeud WAS'
        verbose_name_plural = u'noeuds WAS'
    
class WasAS(ComponentInstance):
    parents = {'was_node': 'WasNode', 'was_cluster': 'WasCluster', 'server':'UnixServer'}
    
    def __unicode__(self):
        return u'AS WAS %s du cluster %s' % (self.name, self.was_cluster.name)
    
    class Meta:
        verbose_name = u'JVM WAS'
        verbose_name_plural = u'JVMs WAS'
    
    detail_template = 'ora/wasas_schema_table.html'
        
class GlassfishAS(ComponentInstance):
    parents = {'server': 'UnixServer'}
    
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
    
    parents = {'server': 'UnixServer'}
    
    class Meta:
        verbose_name = u'Gestionnaire de files'
        verbose_name_plural = u'Gestionnaires de files'

class MqQueueManagerParams(ComponentInstance):
    parents = {'qm': 'MqQueueManager'}
   
    def __unicode__(self):
        return "Params %s sur %s" % (self.instanciates.name, self.qm.name)
    
    class Meta:
        verbose_name = u'Paramétrage MQ Series'
        verbose_name_plural = u'Paramétrages MQ Series'
    
    detail_template = 'ora/mqp_schema_table.html'
        
    

######################################################
# # Programs (batchs, services...)
######################################################

class ApplicationBinary(ComponentInstance):
    parents = {'server': 'UnixServer'}
    root_directory = models.CharField(max_length=255, null=True)
    
    def __unicode__(self):
        return "programme(s) sur %s" % (self.server.name)
    
    class Meta:
        verbose_name = u'ensemble de programmes'
        verbose_name_plural = u'ensembles de programmes'
    
