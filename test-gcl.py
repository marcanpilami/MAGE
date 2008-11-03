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
#models.get_apps()

## Python imports
from datetime import date

## MAGE imports
from MAGE.gcl.models import InstallableSet
from MAGE.gcl.helpers import arePrerequisitesVerified
from MAGE.ref.models import Environment



#############################################
## Tests arePrerequisitesVerified
#############################################

## Tests on a delta patch
i2=InstallableSet.objects.get(name='HF_@TRUC_1_1')
e1 = Environment.objects.get(name='DEV1')
#arePrerequisitesVerified(e1.name, i2)



#############################################
## Test ordre
#############################################


#############################################
## IS objects
i1=InstallableSet.objects.get(name='@TRUC_1_0')
i2=InstallableSet.objects.get(name='HF_@TRUC_1_1')
i3=InstallableSet.objects.get(name='INSTALL_IFPC_TAG_1_0')
i4=InstallableSet.objects.get(name='HF_@TRUC_1_2')
i5=InstallableSet.objects.get(name='HF_@TRUC_1_3')
i6=InstallableSet.objects.get(name='HF_@TRUC_1_4')
i7=InstallableSet.objects.get(name='PATAPOUF_1_0')
i8=InstallableSet.objects.get(name='PATAPOUF_1_1')
i9=InstallableSet.objects.get(name='PATAPOUF_1_2')
i10=InstallableSet.objects.get(name='PATAPOUF_B')


#############################################
## == dependencies

## i2 > i1
print u'001 ( 1) : %s\n' %i2.installation_order(i1)
print u'002 (-1) : %s\n' %i1.installation_order(i2)

## i3 (no installation order) i2
print u'003 ( 0) : %s\n' %i3.installation_order(i2)
print u'004 ( 0) : %s\n' %i2.installation_order(i3)

## i3 > i1
print u'005 ( 1) : %s\n' %i3.installation_order(i1)
print u'006 (-1) : %s\n' %i1.installation_order(i3)

## i5 > i1
print u'007 ( 1) : %s\n' %i5.installation_order(i1)
print u'008 (-1) : %s\n' %i1.installation_order(i5)

## i6 > i1
print u'009 ( 1) : %s\n' %i6.installation_order(i1)
print u'010 (-1) : %s\n' %i1.installation_order(i6)

## i6 > i4
print u'011 ( 1) : %s\n' %i6.installation_order(i4)
print u'012 (-1) : %s\n' %i4.installation_order(i6)

## i6 > i3 (*2)
print u'013 ( 1) : %s\n' %i6.installation_order(i3)
print u'014 (-1) : %s\n' %i3.installation_order(i6)


#############################################
## other dependencies

## 8 > 7 (==)
print u'015 ( 1) : %s\n' %i8.installation_order(i7)

## 9 ? 8 (i9 needs >= 1.0) (i8 is : 1.1, with 8 needing == 1.0)
print u'016 ( ?) : %s\n' %i9.installation_order(i8)     # 0, else it could be to be installed after itself ?

## 10 < 9 (i10 needs <= 1.2, i9 is 1.2). After 9 is installed, 10 cannot be installed anymore => install 10 before 9
print u'017 (-1) : %s\n' %i10.installation_order(i9)

## 10 ? 8 (i10 needs <= 1.2, i8 is 1.1 with i8 needing == 1.0)
print u'018 ( ?) : %s\n' %i10.installation_order(i8)    # Must be consistent with case 16