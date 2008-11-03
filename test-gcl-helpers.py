#!/usr/bin/env python
# -*- coding: utf-8 -*-

## Setup django envt & django imports
from django.core.management import setup_environ
import settings
setup_environ(settings)

## MAGE imports
from MAGE.ref.helpers import *
from MAGE.gcl.helpers import *
from MAGE.gcl.models import *

ctv1 = ComponentTypeVersion.objects.get(class_name='@TRUC', version='1.0')
ctv2 = ComponentTypeVersion.objects.get(class_name='@TRUC', version='1.4')
ctv3 = ComponentTypeVersion.objects.get(class_name='P1', version='1.0')
ctv4 = ComponentTypeVersion.objects.get(class_name='P1', version='1.1')

ctv_a = ComponentTypeVersion.objects.get(version = 'A', class_name = 'MACHIN')
ctv_b = ComponentTypeVersion.objects.get(version = 'B', class_name = 'MACHIN')
ctv_c = ComponentTypeVersion.objects.get(version = 'C', class_name = 'MACHIN')
ctv_d = ComponentTypeVersion.objects.get(version = 'D', class_name = 'MACHIN')
ctv_e = ComponentTypeVersion.objects.get(version = 'E', class_name = 'MACHIN')
ctv_alpha = ComponentTypeVersion.objects.get(version = 'ALPHA', class_name = 'MACHIN')

l_a = InstallableSet.objects.get(name='TEST_CTV_IS_A')
l_b = InstallableSet.objects.get(name='TEST_CTV_IS_B')
l_c = InstallableSet.objects.get(name='TEST_CTV_IS_C')
l_d = InstallableSet.objects.get(name='TEST_CTV_IS_D')
l_e = InstallableSet.objects.get(name='TEST_CTV_IS_E')
l_alpha = InstallableSet.objects.get(name='TEST_CTV_IS_ALPHA')


print u'**************************************************\n** Test goToVersionThroughDeliveries'
print u'**************************************************'
print u'\nTest Truc 1.0 -> Truc 1.4'
print goToVersionThroughDeliveries(ctv1, ctv2)

print u'\nTest P1 1.0 -> P1 1.1'
print goToVersionThroughDeliveries(ctv3, ctv4)

print u'\nTest Inconnu -> Truc 1.4'
print goToVersionThroughDeliveries(None, ctv2)

print u'\nTest Inconnu -> MACHIN ALPHA'
print goToVersionThroughDeliveries(None, ctv_alpha)

print u'\nTest P1 1.1 -> P1 1.0'
try:
    print goToVersionThroughDeliveries(ctv4, ctv3)
except InverseOrder:
    print 'exception OK : InverseOrder'
    
print u'\nTest Truc 1.0 -> Truc 1.0'
try:
    print goToVersionThroughDeliveries(ctv1, ctv1)
except SameCTV:
    print 'exception OK : SameCTV'


print u'\n\n**************************************************\n** Test check_is_chain_consistent'
print u'**************************************************'
print u'\nTest cohérence chaine trouvée pour Truc 1.0 -> Truc 1.4'
chain = goToVersionThroughDeliveries(ctv1, ctv2)
chain.reverse()
print u'Chaine à analyser : %s' %(chain)
print u'Cohérence [True] : %s' %(check_is_chain_consistent(chain))

print u'\nTest cohérence chaine 2'
chain = [l_a, l_b, l_c, l_d, l_e]
print u'Chaine à analyser : %s' %(chain)
print u'Cohérence [True] : %s' %(check_is_chain_consistent(chain))

print u'\nTest cohérence chaine 3'
chain = [l_a, l_alpha]
print u'Chaine à analyser : %s' %(chain)
print u'Cohérence [True] : %s' %(check_is_chain_consistent(chain))

print u'\nTest cohérence chaine 4'
chain = [l_a, l_alpha, l_b]
print u'Chaine à analyser : %s' %(chain)
print u'Cohérence [False] : %s' %(check_is_chain_consistent(chain))

print u'\nTest cohérence chaine 5'
chain = [l_a, l_b, l_alpha]
print u'Chaine à analyser : %s' %(chain)
print u'Cohérence [True] : %s' %(check_is_chain_consistent(chain))

print u'\nTest cohérence chaine 6'
chain = [l_a, l_b, l_c, l_alpha]
print u'Chaine à analyser : %s' %(chain)
print u'Cohérence [True] : %s' %(check_is_chain_consistent(chain))

print u'\nTest cohérence chaine 7'
chain = [l_a, l_b, l_c, l_d, l_alpha]
print u'Chaine à analyser : %s' %(chain)
print u'Cohérence [False] : %s' %(check_is_chain_consistent(chain))


print u'\n\n**************************************************\n** Test check_impact_on_component'
print u'**************************************************'


print u'\n\n**************************************************\n** Test goToTagThroughDeliveries'
print u'**************************************************'
if Tag.objects.filter(name='TAG1').count() == 0:
    snapshot('TAG1', 'DEV1')
print goToTagThroughDeliveries('DEV2', 'TAG1')
