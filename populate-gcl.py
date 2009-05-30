#!/bin/python
# -*- coding: utf-8 -*-

## Setup django envt
from django.core.management import setup_environ
import settings
setup_environ(settings)
from django.db import transaction
from django.db import models
models.get_apps()

## Python imports
from datetime import date

## Django imports
from django.contrib.contenttypes.models import ContentType

## MAGE imports
from MAGE.liv.models import *
from MAGE.gcl.models import *


## Cleanup
for l in Delivery.objects.all():
    l.delete()
for ctv in ComponentTypeVersion.objects.all():
    ctv.delete()
    

#################################################################################################
## GCL entries
#################################################################################################

########################################
## Full delivery of a single IFPC folder
l1 = Delivery(release_notes='Install initiale folder IF @TRUC', name='@TRUC_1_0', is_full=True)
l1.save()
ctv1 = ComponentTypeVersion(version='1.0', 
                            model=ContentType.objects.get(model=u'ifpcfolder'), 
                            class_name='@TRUC')
ctv1.save()
l1.acts_on.add(ctv1)
l1.save()

########################################
## Incremental patch of a single IFPC folder
l2 = Delivery(release_notes='Mise a jour incrementielle folder IF @TRUC', name='HF_@TRUC_1_1', is_full=False)
l2.save()
ctv2 = ComponentTypeVersion(version='1.1', 
                            model=ContentType.objects.get(model=u'ifpcfolder'), 
                            class_name='@TRUC')
ctv2.save()
d2 = Dependency(installable_set = l2, type_version = ctv1, operator='==')
d2.save()
l2.acts_on.add(ctv2)
l2.save()

########################################
## Incremental patch of a single IFPC folder
l6 = Delivery(release_notes='Mise a jour incrementielle folder IF @TRUC', name='HF_@TRUC_1_2', is_full=False)
l6.save()
ctv6 = ComponentTypeVersion(version='1.2', 
                            model=ContentType.objects.get(model=u'ifpcfolder'), 
                            class_name='@TRUC')
ctv6.save()
d6 = Dependency(installable_set = l6, type_version = ctv2, operator='==')
d6.save()
l6.acts_on.add(ctv6)
l6.save()

########################################
## Incremental patch of a single IFPC folder
l7 = Delivery(release_notes='Mise a jour incrementielle folder IF @TRUC', name='HF_@TRUC_1_3', is_full=False)
l7.save()
ctv7 = ComponentTypeVersion(version='1.3', 
                            model=ContentType.objects.get(model=u'ifpcfolder'), 
                            class_name='@TRUC')
ctv7.save()
d7 = Dependency(installable_set = l7, type_version = ctv6, operator='==')
d7.save()
l7.acts_on.add(ctv7)
l7.save()

########################################
## Full delivery of two distinct IFPC folders
l3 = Delivery(release_notes='Livraison de deux folders IFPC (@TRUC en v1.1, @MACHIN en v1.0)', 
              name='INSTALL_IFPC_TAG_1_0', is_full=True)
l3.save()
ctv3 = ComponentTypeVersion(version='1.0', 
                            model=ContentType.objects.get(model=u'ifpcfolder'), 
                            class_name='@MACHIN')
ctv3.save()
d3 = Dependency(installable_set = l3, type_version = ctv1, operator='==') ## >= @TRUC v1.0
d3.save()
l3.acts_on.add(ctv2)
l3.acts_on.add(ctv3)
l3.save()

########################################
## Incremental patch of a single IFPC folder, double dep with >=
l8 = Delivery(release_notes='Mise a jour incrementielle folder IF @TRUC', name='HF_@TRUC_1_4', is_full=False)
l8.save()
ctv8 = ComponentTypeVersion(version='1.4', 
                            model=ContentType.objects.get(model=u'ifpcfolder'), 
                            class_name='@TRUC')
ctv8.save()
d8 = Dependency(installable_set = l8, type_version = ctv7, operator='==')   ## == @TRUC 1.3
d8_2 = Dependency(installable_set = l8, type_version = ctv3, operator='>=') ## >= @MACHIN 1.0
d8.save()
d8_2.save()
l8.acts_on.add(ctv8)
l8.save()

########################################
## Full delivery of a single IFPC folder
l9 = Delivery(release_notes='Livraison folder IF PATAPOUF', name='PATAPOUF_1_0', is_full=True)
l9.save()
ctv9 = ComponentTypeVersion(version='1.0', 
                            model=ContentType.objects.get(model=u'ifpcfolder'), 
                            class_name='PATAPOUF')
ctv9.save()
l9.acts_on.add(ctv9)
l9.save()

########################################
## Incremental patch of a single IFPC folder (== dependency)
l10 = Delivery(release_notes='Mise a jour incrementielle folder IF PATAPOUF', name='PATAPOUF_1_1', is_full=False)
l10.save()
ctv10 = ComponentTypeVersion(version='1.1', 
                            model=ContentType.objects.get(model=u'ifpcfolder'), 
                            class_name='PATAPOUF')
ctv10.save()
d10 = Dependency(installable_set = l10, type_version = ctv9, operator='==') # applies on folders PATAPOUF v1.0 only
d10.save()
l10.acts_on.add(ctv10)
l10.save()

########################################
## Incremental patch of a single IFPC folder (>= dependency)
l11 = Delivery(release_notes='Mise a jour incrementielle folder IF PATAPOUF', name='PATAPOUF_1_2', is_full=False)
l11.save()
ctv11 = ComponentTypeVersion(version='1.2', 
                            model=ContentType.objects.get(model=u'ifpcfolder'), 
                            class_name='PATAPOUF')
ctv11.save()
d11 = Dependency(installable_set = l11, type_version = ctv9, operator='>=') # applies on PATAPOUF folders >= v1.0
d11.save()
l11.acts_on.add(ctv11)
l11.save()

########################################
## Incremental patch of a single IFPC folder (<= dependency)
l12 = Delivery(release_notes='Mise a jour incrementielle folder IF PATAPOUF', name='PATAPOUF_B', is_full=False)
l12.save()
ctv12 = ComponentTypeVersion(version='B', 
                            model=ContentType.objects.get(model=u'ifpcfolder'), 
                            class_name='PATAPOUF')
ctv12.save()
d12 = Dependency(installable_set = l12, type_version = ctv11, operator='<=') # applies on any PATAPOUF folder of version <= v1.2
d12.save()
l12.acts_on.add(ctv12)
l12.save()

########################################
## Full delivery of a single Oracle Package
l4 = Delivery(release_notes='Install initiale package P1', name='P1_1_0', is_full=True)
l4.save()
ctv4 = ComponentTypeVersion(version='1.0', 
                            model=ContentType.objects.get(model=u'oraclepackage'), 
                            class_name='P1')
ctv4.save()
l4.acts_on.add(ctv4)
l4.save()

########################################
## Delta delivery of a single Oracle Package (idiotic : packages cannot be delta delivered, but anyway)
l5 = Delivery(release_notes='Patch package P1', name='P1_1_1', is_full=False)
l5.save()
ctv5 = ComponentTypeVersion(version='1.1', 
                            model=ContentType.objects.get(model=u'oraclepackage'),
                            class_name='P1')
ctv5.save()
d5 = Dependency(installable_set = l5, type_version = ctv4, operator='==')
d5.save()
l5.acts_on.add(ctv5)
l5.save()
