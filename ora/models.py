from django.db import models
from django.contrib import admin

from MAGE.ref.models import Component
from MAGE.ref.models import MageModelType

class OracleInstance(Component):
    port = models.IntegerField(max_length=6)
    listener = models.CharField(max_length=100)
    
    def _getServer(self):
        return self.dependsOn.get(model__model='server').leaf
    server = property(_getServer)
    parents = {'server':'Server'}

class OracleSchema(Component):
    login = models.CharField(max_length=100)
    
    def _getInstance(self):
        return self.dependsOn.get(model__model='oracleinstance').leaf
    instance = property(_getInstance)
    def _getConnectString(self):
        return u'%s/%s@%s' %(self.login, self.login, self.instance.name)
    connectString = property(_getConnectString)
    
    parents = {'instance':'OracleInstance'}
    detail_template = 'ora_schema_details.html'

class OracleMPD(Component):
    def _getSchema(self):
        return self.dependsOn.get(model__model='oracleschema').leaf
    schema = property(_getSchema) 

class OraclePackage(Component):
    def _getSchema(self):
        return self.dependsOn.get(model__model='oracleschema').leaf
    schema = property(_getSchema) 
    parents = {'schema':'OracleSchema'}
    
    def __unicode__(self):
        return u'Package %s sur %s' %(self.class_name, self.schema.instance_name)

class OraclePackageAdmin(admin.ModelAdmin):
    list_display = ('class_name', 'schema') 
admin.site.register(OraclePackage, OraclePackageAdmin)
admin.site.register(OracleInstance)
