# coding: utf-8

from MAGE.liv.models import *
from MAGE.ref.models import *
from MAGE.gcl.models import *
from MAGE.mqqm.models import *
from MAGE.fif.models import *
from MAGE.srv.models import *
from datetime import date

#### Model types
c = MageModelType(name = 'Folder Informatica générique', description = '.', model = 'ifpcfolder')
c.save()
c = MageModelType(name = 'MQSeries Queue Manager', description = '.', model = 'queuemanager')
c.save()
c = MageModelType(name = 'Serveur', description = '.', model = 'server')
c.save()


e = Environment(name='ENVT1', buildDate=date.today(), destructionDate=date.today(), description='envt de test 1')
e.save()
e2 = Environment(name='ENVT2', buildDate=date.today(), destructionDate=date.today(), description='envt de test 2')
e2.save()
e2 = Environment(name='ENVT3', buildDate=date.today(), destructionDate=date.today(), description='envt de test 3')
e2.save()

s = Server(name='MACHIN', os='AIX 5.3', comment='créé automatiquement', ip="1.2.3.4")
s.save()

f = IFPCFolder(name='folder1')
f.save()
f.environments.add(e)
f.dependsOn.add(s)
f.save()

qm = QueueManager(name = 'QM1' , port=1414, adminChannel = 'CANAL_HISTORIQUE')
qm.save()
qm.environments.add(e)
qm.environments.add(e2)
qm.dependsOn.add(s)
qm.save()

qm = QueueManager(name = 'QM2' , port=1415, adminChannel = 'CANAL_HISTORIQUE_NATIONAL')
qm.save()
qm.dependsOn.add(s)
qm.save()

