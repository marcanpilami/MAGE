#!/bin/python
# -*- coding: utf-8 -*-

"""
    Test file for the GCL application
    Uses objects from populate.py
    It is an independant script, called without any arguments.

    @author: mag
"""

## Setup django envt
from django.core.management import setup_environ
import settings
setup_environ(settings)
from django.db import models
models.get_apps()
from django.db import transaction
from django.contrib.contenttypes.models import ContentType

## Python imports
from datetime import date

## MAGE imports
from MAGE.gcl.models import InstallableSet, ComponentTypeVersion, Dependency
from MAGE.ref.models import Environment



#############################################################################
## Clear remains of previous runs.
#############################################################################

@transaction.commit_manually
def clearGarbage():
    print u'Destruction des IS de test'
    for ins in InstallableSet.objects.filter(name__startswith='TEST_CTV_IS_'):
        ins.delete()
    print u'\nDestruction des CTV de test'
    for ctv in ComponentTypeVersion.objects.filter(class_name__startswith='MACHIN'):
        ctv.delete()
    transaction.commit()

clearGarbage()


#############################################################################
## Create objects.
#############################################################################
    
@transaction.commit_manually
def createTestObjects():
    print u'\nCréation des IS/CTV/Dep de test'
    oraclemodel = ContentType.objects.get(model='oraclepackage')
    
    ## Full delivery of version A of folder MACHIN
    l1 = InstallableSet(name='TEST_CTV_IS_A', is_full=True)
    l1.save()
    ctv_a = ComponentTypeVersion(version = 'A', 
                                model = oraclemodel, 
                                class_name = 'MACHIN')
    ctv_a.save()
    l1.acts_on.add(ctv_a)
    
    
    ## Version B, B needs == A
    l2 = InstallableSet(name='TEST_CTV_IS_B', is_full=False)
    l2.save()
    ctv_b = ComponentTypeVersion(version = 'B', 
                                model = oraclemodel, 
                                class_name = 'MACHIN')
    ctv_b.save()
    l2.acts_on.add(ctv_b)
    d2 = Dependency(installable_set = l2, type_version = ctv_a, operator='==')
    d2.save()
    
    
    ## Version C, C needs == B
    l3 = InstallableSet(name='TEST_CTV_IS_C', is_full=False)
    l3.save()
    ctv_c = ComponentTypeVersion(version = 'C', 
                                model = oraclemodel, 
                                class_name = 'MACHIN')
    ctv_c.save()
    l3.acts_on.add(ctv_c)
    d3 = Dependency(installable_set = l3, type_version = ctv_b, operator='==')
    d3.save()
    
    
    ## Version D, D needs == C
    l4 = InstallableSet(name='TEST_CTV_IS_D', is_full=False)
    l4.save()
    ctv_d = ComponentTypeVersion(version = 'D', 
                                model = oraclemodel, 
                                class_name = 'MACHIN')
    ctv_d.save()
    l4.acts_on.add(ctv_d)
    d4 = Dependency(installable_set = l4, type_version = ctv_c, operator='==')
    d4.save()
    
    
    ## Version E, E needs >= D
    l5 = InstallableSet(name='TEST_CTV_IS_E', is_full=False)
    l5.save()
    ctv_e = ComponentTypeVersion(version = 'E', 
                                model = oraclemodel, 
                                class_name = 'MACHIN')
    ctv_e.save()
    l5.acts_on.add(ctv_e)
    d5 = Dependency(installable_set = l5, type_version = ctv_d, operator='>=')
    d5.save()
    
    ## Version ALPHA, ALPHA needs >= A and <= C
    l6 = InstallableSet(name='TEST_CTV_IS_ALPHA', is_full=True)
    l6.save()
    ctv_alpha = ComponentTypeVersion(version = 'ALPHA', 
                                model = oraclemodel, 
                                class_name = 'MACHIN')
    ctv_alpha.save()
    l6.acts_on.add(ctv_alpha)
    d6 = Dependency(installable_set = l6, type_version = ctv_a, operator='>=')
    d6.save()
    d6_2 = Dependency(installable_set = l6, type_version = ctv_c, operator='<=')
    d6_2.save()
    
    ## Version F, F needs nothing (FULL)
    l7 = InstallableSet(name='TEST_CTV_IS_F', is_full=True)
    l7.save()
    ctv_f = ComponentTypeVersion(version = 'F', 
                                model = oraclemodel, 
                                class_name = 'MACHIN')
    ctv_f.save()
    l7.acts_on.add(ctv_f)
    
    ## Version G, G needs == F
    l8 = InstallableSet(name='TEST_CTV_IS_G', is_full=False)
    l8.save()
    ctv_g = ComponentTypeVersion(version = 'G', 
                                model = oraclemodel, 
                                class_name = 'MACHIN')
    ctv_g.save()
    l8.acts_on.add(ctv_g)
    d8 = Dependency(installable_set = l8, type_version = ctv_f, operator='==')
    d8.save()
    
    transaction.commit()

createTestObjects()

ctv_a = ComponentTypeVersion.objects.get(version = 'A', class_name = 'MACHIN')
ctv_b = ComponentTypeVersion.objects.get(version = 'B', class_name = 'MACHIN')
ctv_c = ComponentTypeVersion.objects.get(version = 'C', class_name = 'MACHIN')
ctv_d = ComponentTypeVersion.objects.get(version = 'D', class_name = 'MACHIN')
ctv_e = ComponentTypeVersion.objects.get(version = 'E', class_name = 'MACHIN')
ctv_f = ComponentTypeVersion.objects.get(version = 'F', class_name = 'MACHIN')
ctv_g = ComponentTypeVersion.objects.get(version = 'G', class_name = 'MACHIN')
ctv_alpha = ComponentTypeVersion.objects.get(version = 'ALPHA', class_name = 'MACHIN')



#############################################################################
## Sort (visual test)
#############################################################################

### Try a sort !
res1 = [ i for i in ComponentTypeVersion.objects.filter(class_name = 'MACHIN')] 
res1.sort(cmp = ComponentTypeVersion.compare)
print u'\n\nTest : liste triée dans l\'ordre naturel'
print res1
print u'\nTest : liste triée dans l\'ordre naturel inverse'
res1.sort(cmp = ComponentTypeVersion.compare, reverse=True)
print res1
print '\n\n'



#############################################################################
## Test run
#############################################################################

print u'Tests de comparaisons unitaires\n'
print u'A <  B [TRUE]  : %s' %(ctv_a.compare(ctv_b) == -1)
print u'A >  B [FALSE] : %s' %(ctv_a.compare(ctv_b) ==  1)
print u'A == B [FALSE] : %s' %(ctv_a.compare(ctv_b) ==  0)

print ''
print u'A <  C [TRUE]  : %s' %(ctv_a.compare(ctv_c) == -1)
print u'A >  C [FALSE] : %s' %(ctv_a.compare(ctv_c) ==  1)
print u'A == C [FALSE] : %s' %(ctv_a.compare(ctv_c) ==  0)

print ''
print u'A <  D [TRUE]  : %s' %(ctv_a.compare(ctv_d) == -1)
print u'A >  D [FALSE] : %s' %(ctv_a.compare(ctv_d) ==  1)
print u'A == D [FALSE] : %s' %(ctv_a.compare(ctv_d) ==  0)

print ''
print u'A <  E [TRUE]  : %s' %(ctv_a.compare(ctv_e) == -1)
print u'A >  E [FALSE] : %s' %(ctv_a.compare(ctv_e) ==  1)
print u'A == E [FALSE] : %s' %(ctv_a.compare(ctv_e) ==  0)

print ''
print u'B <  E [TRUE]  : %s' %(ctv_b.compare(ctv_e) == -1)
print u'B >  E [FALSE] : %s' %(ctv_b.compare(ctv_e) ==  1)
print u'B == E [FALSE] : %s' %(ctv_b.compare(ctv_e) ==  0)

print ''
print u'B <  C [TRUE]  : %s' %(ctv_b.compare(ctv_c) == -1)
print u'B >  C [FALSE] : %s' %(ctv_b.compare(ctv_c) ==  1)
print u'B == C [FALSE] : %s' %(ctv_b.compare(ctv_c) ==  0)



print '\n'
print u'A <  ALPHA [TRUE]  : %s' %(ctv_a.compare(ctv_alpha) == -1)
print u'A >  ALPHA [FALSE] : %s' %(ctv_a.compare(ctv_alpha) ==  1)
print u'A == ALPHA [FALSE] : %s' %(ctv_a.compare(ctv_alpha) ==  0)

print ''
print u'B <  ALPHA [FALSE] : %s' %(ctv_b.compare(ctv_alpha) == -1)
print u'B >  ALPHA [FALSE] : %s' %(ctv_b.compare(ctv_alpha) ==  1)
print u'B == ALPHA [TRUE]  : %s' %(ctv_b.compare(ctv_alpha) ==  0)

print ''
print u'C <  ALPHA [FALSE] : %s' %(ctv_c.compare(ctv_alpha) == -1)
print u'C >  ALPHA [FALSE] : %s' %(ctv_c.compare(ctv_alpha) ==  1)
print u'C == ALPHA [TRUE]  : %s' %(ctv_c.compare(ctv_alpha) ==  0)

print ''
print u'ALPHA <  C [FALSE] : %s' %(ctv_alpha.compare(ctv_c) == -1)
print u'ALPHA >  C [FALSE] : %s' %(ctv_alpha.compare(ctv_c) ==  1)
print u'ALPHA == C [TRUE]  : %s' %(ctv_alpha.compare(ctv_c) ==  0)

print ''
print u'D <  ALPHA [FALSE] : %s' %(ctv_d.compare(ctv_alpha) == -1)
print u'D >  ALPHA [TRUE]  : %s' %(ctv_d.compare(ctv_alpha) ==  1)
print u'D == ALPHA [FALSE] : %s' %(ctv_d.compare(ctv_alpha) ==  0)

print ''
print u'ALPHA <  D [TRUE]  : %s' %(ctv_alpha.compare(ctv_d) == -1)
print u'ALPHA >  D [FALSE] : %s' %(ctv_alpha.compare(ctv_d) ==  1)
print u'ALPHA == D [FALSE] : %s' %(ctv_alpha.compare(ctv_d) ==  0)

print ''
print u'E <  ALPHA [FALSE] : %s' %(ctv_e.compare(ctv_alpha) == -1)
print u'E >  ALPHA [TRUE]  : %s' %(ctv_e.compare(ctv_alpha) ==  1)
print u'E == ALPHA [FALSE] : %s' %(ctv_e.compare(ctv_alpha) ==  0)

print ''
print u'ALPHA <  ALPHA [FALSE] : %s' %(ctv_alpha.compare(ctv_alpha) == -1)
print u'ALPHA >  ALPHA [FALSE] : %s' %(ctv_alpha.compare(ctv_alpha) ==  1)
print u'ALPHA == ALPHA [TRUE]  : %s' %(ctv_alpha.compare(ctv_alpha) ==  0)

print ''
print ctv_f.compare(ctv_e)