# coding: utf-8

from MAGE.ref.models import *
from MAGE.gcl.models import *
from MAGE.liv.models import *
from MAGE.sav.models import *
from MAGE.fif.models import *

f1 = IFPCFolder.objects.get(name='@TRUC')
f2 = IFPCFolder.objects.get(name='@MACHIN')

e = Environment.objects.get(name='ENVT1')

# Test 0 : IS full à un seul élément, le composant existe déjà
l1 = Delivery.objects.all()[0]
l1.installOn([f1,], e)

# Test 1 : mise à jour d'un composant, IS à un seul élément, le composant existe déjà.
l2 = Delivery.objects.get(name='HF_@TRUC_1_1')
l2.installOn([f1], e)

# Test 2 : IS full avec deux éléments, les composants existent déjà.
l3 = Delivery.objects.get(name='INSTALL_IFPC_TAG_1_0')
l3.installOn([f1, f2], e)

# Test 3 : IS à un élément, le composant n'existe pas encore. IS Full.
l1.installOn([('@TRUC', IFPCFolder, {}),], e)

# Test 4 : IS à un élément, le composant n'existe pas encore. IS incrémentiel (doit échouer)

# Test 5 : IS à deux éléments, les composants n'existent pas. IS Full.

# Test 6 : IS à deux éléments, un seul composant existe. IS Full.