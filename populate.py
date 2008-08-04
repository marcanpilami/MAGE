# coding: utf-8

from MAGE.liv.models import *
from MAGE.ref.models import *
from MAGE.gcl.models import *
from MAGE.mqqm.models import *
from MAGE.fif.models import *
from MAGE.srv.models import *
from datetime import date


#### Model types
c1 = MageModelType(name = 'Folder Informatica', description = '.', model = 'ifpcfolder')
c1.save()
c = MageModelType(name = 'MQSeries Queue Manager', description = '.', model = 'queuemanager')
c.save()
c = MageModelType(name = 'Serveur', description = '.', model = 'server')
c.save()


## Some environments...
e = Environment(name='ENVT1', buildDate=date.today(), destructionDate=date.today(), description='envt de test 1')
e.save()
e2 = Environment(name='ENVT2', buildDate=date.today(), destructionDate=date.today(), description='envt de test 2')
e2.save()
e2 = Environment(name='ENVT3', buildDate=date.today(), destructionDate=date.today(), description='envt de test 3')
e2.save()


## Some components...
s = Server(name='MACHIN', os='AIX 5.3', comment='créé automatiquement', ip="1.2.3.4")
s.save()

f1 = IFPCFolder(name='@TRUC')
f1.save()
f1.environments.add(e)
f1.dependsOn.add(s)
f1.save()

f2 = IFPCFolder(name='@MACHIN')
f2.save()
f2.environments.add(e)
f2.dependsOn.add(s)
f2.save()

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


## Some deliveries...

# Full delivery of a single IFPC folder
l1 = Delivery(release_notes='Install initiale folder IF @TRUC', name='@TRUC_1_0', is_full=True)
l1.save()
ctv1 = ComponentTypeVersion(version='1.0', component_type=c1, component_name='@TRUC')
ctv1.save()
l1.acts_on.add(ctv1)
l1.save()

# Incremental patch of a single IFPC folder
l2 = Delivery(release_notes='Mise a jour incrementielle folder IF @TRUC', name='HF_@TRUC_1_1', is_full=False)
l2.save()
ctv2 = ComponentTypeVersion(version='1.1', component_type=c1, component_name='@TRUC')
ctv2.save()
l2.acts_on.add(ctv2)
l2.save()

# Full delivery of two distinct IFPC folders
l3 = Delivery(release_notes='Livraison de deux folders IFPC', name='INSTALL_IFPC_TAG_1_0', is_full=True)
l3.save()
l3.acts_on.add(ctv2)
ctv3 = ComponentTypeVersion(version='1.0', component_type=c1, component_name='@MACHIN')
ctv3.save()
l3.acts_on.add(ctv3)
l3.save()

