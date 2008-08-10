from django.db import models


from MAGE.ref.models import Composant
from MAGE.ref.models import MageModelType

class OracleInstance(Composant):
    port = models.IntegerField(max_length=6)
    listener = models.CharField(max_length=100)
    
    def _getServer(self):
        return self.dependsOn.get(type=MageModelType.objects.get(model='server')).leaf
    server = property(_getServer)


class OracleSchema(Composant):
    login = models.CharField(max_length=100)
    
    def _getInstance(self):
        return self.dependsOn.get(type=MageModelType.objects.get(model='oracleinstance')).leaf
    instance = property(_getInstance)
    def _getConnectString(self):
        return u'%s/%s@%s' %(self.login, self.login, self.instance.name)
    connectString = property(_getConnectString)
    parents = {'instance':'OracleInstance'}

class OracleMPD(Composant):
    def _getSchema(self):
        return self.dependsOn.get(type=MageModelType.objects.get(model='oracleschema')).leaf
    schema = property(_getSchema) 

class OraclePackage(Composant):
    def _getSchema(self):
        return self.dependsOn.get(type=MageModelType.objects.get(model='oracleschema')).leaf
    schema = property(_getSchema) 
    parents = {'schema':'OracleSchema'}

