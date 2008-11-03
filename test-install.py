#!/bin/python
# -*- coding: utf-8 -*-

"""
    Test file for the install.py script.
    It relies on objects from populate.py
    It is an independant script, no need to run it from "manage.py shell"
    
    Note: it tests only calls from outside MAGE, hence the os.system calls.
    
    @author: mag
"""



####################################################################
## Imports & MAGE envt
####################################################################

## Python imports
import os

## Setup django envt & django imports
from django.core.management import setup_environ
import settings
setup_environ(settings)
from django.db import transaction

## MAGE imports
from MAGE.ref.models import *
from MAGE.gcl.models import *
from MAGE.liv.models import *
from MAGE.sav.models import *
from MAGE.fif.models import *
from MAGE.srv.models import *
from MAGE.mqqm.models import *



####################################################################
## Retrieve some objects
####################################################################


dev1 = Environment.objects.get(name='DEV1')
qua1 = Environment.objects.get(name='QUA1')

xgct1 = Server.objects.get(instance_name='XGCT1')
xgct2 = Server.objects.get(instance_name='XGCT2')

qm1 = QueueManager.objects.get(instance_name = 'QM.GSC.DEV1')
qm2 = QueueManager.objects.get(instance_name = 'QM.IFPC.DEV1')




####################################################################
## Clean up
####################################################################

@transaction.commit_manually
def cleanInstalls():
    for ins in Installation.objects.filter(target_components__class_name__in=['@TRUC','@MACHIN', 'PATAPOUF', 'P1']):
        ins.delete()
    transaction.commit()
cleanInstalls()


####################################################################
## Tests
####################################################################

print u'\n\nDébut des tests'
# Test 0 : IS full à un seul élément, le composant existe déjà
print '\nInstallation @TRUC_1_0'
os.system('python install.py -eDEV1 -i@TRUC_1_0 -c"ifpcfolder=@TRUC,ifpc_project=GESCO_DEV"')
f1 = IFPCFolder.objects.get(class_name='@TRUC', environments__name='DEV1', dependsOn__instance_name='GESCO_DEV')
print u'Version @TRUC [1.0] : %s' %f1.version

# Test 1 : mise à jour d'un composant, IS à un seul élément, le composant existe déjà.
print ''
os.system('python install.py -eDEV1 -iHF_@TRUC_1_1 -c"ifpcfolder=@TRUC,ifpc_project=GESCO_DEV" -f')
print u'Version @TRUC [1.1] : %s' %f1.version

# Test 2 : IS full avec deux éléments, les composants existent déjà.
print '\nInstallation INSTALL_IFPC_TAG_1_0 sur un seul composant'
os.system('python install.py -eDEV1 -iINSTALL_IFPC_TAG_1_0 -c"ifpcfolder=@TRUC,ifpc_project=GESCO_DEV" -f')
print u'Version @TRUC   [1.1] : %s' %f1.version
#print u'Version @MACHIN [inc] : %s' %f2.version

print '\nInstallation INSTALL_IFPC_TAG_1_0 sur deux composants de classes différentes'
os.system('python install.py -eDEV1 -iINSTALL_IFPC_TAG_1_0 -c"ifpcfolder=@TRUC,ifpc_project=GESCO_DEV" \
    -c"ifpcfolder=@MACHIN,ifpc_project=GESCO_DEV" -f')
f2 = IFPCFolder.objects.get(class_name='@MACHIN', environments__name='DEV1', dependsOn__instance_name='GESCO_DEV')
print u'Version @TRUC   [1.1] : %s' %f1.version
print u'Version @MACHIN [1.0] : %s' %f2.version

# Test 3 : IS à un élément, le composant n'existe pas encore. IS Full.
print '\nInstallation PATAPOUF_1_0'
os.system('python install.py -eDEV1 -iPATAPOUF_1_0 -c"ifpcfolder=PATAPOUF,ifpc_project=GESCO_DEV"')
patapouf = IFPCFolder.objects.get(class_name='PATAPOUF')
print u'Version @PATAPOUF [1.0] : %s' %patapouf.version
print u'PK de PATAPOUF : %s' %patapouf.pk
patapouf.delete()

# Test 4 : IS à un élément, le composant n'existe pas encore. IS incrémentiel (doit échouer)
print '\nInstallation PATAPOUF_1_1 (incrément, alors que le folder n\'existe pas)'
os.system('python install.py -eDEV1 -iPATAPOUF_1_1 -c"ifpcfolder=PATAPOUF,ifpc_project=GESCO_DEV"')
#patapouf = IFPCFolder.objects.get(class_name='PATAPOUF')

# Test 5 : IS à deux éléments, les composants n'existent pas. IS Full.
f1.delete()
f2.delete()
print '\nInstallation INSTALL_IFPC_TAG_1_0 sur deux composants de classes différentes'
os.system('python install.py -eDEV1 -iINSTALL_IFPC_TAG_1_0 -c"ifpcfolder=@TRUC,ifpc_project=GESCO_DEV" \
    -c"ifpcfolder=@MACHIN,ifpc_project=GESCO_DEV" -f')
f1 = IFPCFolder.objects.get(class_name='@TRUC', environments__name='DEV1', dependsOn__instance_name='GESCO_DEV')
f2 = IFPCFolder.objects.get(class_name='@MACHIN', environments__name='DEV1', dependsOn__instance_name='GESCO_DEV')



# Test 6 : IS à deux éléments, un seul composant existe. IS Full.

print u'Numéro ID de %s : %s' %(f1, f1.pk)
print u'Numéro ID de %s : %s' %(f2, f2.pk)


# Test 3bis : IS à un élément, le composant n'existe pas encore. IS Full.
print '\nInstallation PATAPOUF_1_0'
os.system('python install.py -eDEV1 -iPATAPOUF_1_0 -c"ifpcfolder=PATAPOUF,ifpc_project=GESCO_DEV"')
patapouf = IFPCFolder.objects.get(class_name='PATAPOUF')
print u'Version @PATAPOUF [1.0] : %s' %patapouf.version
print u'PK de PATAPOUF : %s' %patapouf.pk