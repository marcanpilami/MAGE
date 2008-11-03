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

## MAGE imports
from MAGE.ref.models import *
from MAGE.liv.models import *
from MAGE.gcl.models import *
from MAGE.mqqm.models import *
from MAGE.fif.models import *
from MAGE.srv.models import *
from MAGE.ora.models import *



#################################################################################################
## Metadata
#################################################################################################

########################################
## Model types
# IFPC
MageModelType(name = 'Folder Informatica', description = '.', model = 'ifpcfolder').save()
MageModelType(name = 'Projet Informatica', description = '.', model = 'ifpcproject').save()
# MQ
MageModelType(name = 'MQSeries Queue Manager', description = '.', model = 'queuemanager').save()
MageModelType(name = u'Paramétrage MQSeries', description = '.', model = 'queuemanagerparams').save()
# Servers
MageModelType(name = 'Serveur', description = '.', model = 'server').save()
# Oracle
MageModelType(name = 'Instance Oracle', description = '.', model = 'oracleinstance').save()
MageModelType(name = u'Schéma Oracle', description = '.', model = 'oracleschema').save()
MageModelType(name = 'MPD Oracle', description = '.', model = 'oraclempd').save()
MageModelType(name = 'Package Oracle', description = '.', model = 'oraclepackage').save()


@transaction.commit_on_success
def createObjects():
    """In a function so as to control transactions manually"""
    #################################################################################################
    ## Environments
    #################################################################################################
    
    e1 = Environment(name='DEV1', buildDate=date.today(), destructionDate=date.today(), description='envt de dev 1')
    e1.save()
    e2 = Environment(name='DEV2', buildDate=date.today(), destructionDate=date.today(), description='envt de dev 2')
    e2.save()
    e3 = Environment(name='REC1', buildDate=date.today(), destructionDate=date.today(), description='envt de recette 1')
    e3.save()
    e4 = Environment(name='REC2', buildDate=date.today(), destructionDate=date.today(), description='envt de recette 2')
    e4.save()
    e5 = Environment(name='QUA1', buildDate=date.today(), destructionDate=date.today(), description='envt de qualif 1')
    e5.save()
    
    
    
    #################################################################################################
    ## Components
    #################################################################################################
    
    ########################################
    ## Servers
    s1 = Server(instance_name='XGCT1', os='AIX 5.3', comment='créé automatiquement', ip="1.2.3.4")
    s1.save()
    
    s2 = Server(instance_name='XGCT2', os='AIX 5.3', comment='créé automatiquement', ip="5.6.7.8")
    s2.save()
    
    ########################################
    ## IFPC
    ifp1 = IFPCProject(instance_name='GESCO_DEV')
    ifp1.save()
    ifp1.environments.add(e1)
    ifp1.dependsOn = [s2]
    ifp1.save()
    
    ifp2 = IFPCProject(instance_name='GESCO_QUAL')
    ifp2.save()
    ifp2.environments.add(e5)
    ifp2.dependsOn = [s2]
    ifp2.save()
    
    f1 = IFPCFolder(class_name='@TRUC')
    f1.save()
    f1.environments = [e1]
    f1.dependsOn = [ifp1]
    f1.save()
    
    f2 = IFPCFolder(class_name='@MACHIN')
    f2.save()
    f2.environments = [e1]
    f2.dependsOn.add(ifp1)
    f2.save()
    
    f3 = IFPCFolder(class_name='@TRUC')
    f3.save()
    f3.environments = [e5]
    f3.dependsOn = [ifp2]
    f3.save()
    
    f4 = IFPCFolder(class_name='@MACHIN')
    f4.save()
    f4.environments = [e5]
    f4.dependsOn.add(ifp2)
    f4.save()
    
    ########################################
    ## MQ
    qm1 = QueueManager(instance_name = 'QM.GSC.DEV1' , port=1414, adminChannel = 'CANAL_HISTORIQUE')
    qm1.save()
    qm1.environments= [e1]
    qm1.dependsOn.add(s1)
    qm1.save()
    
    qmp1 = QueueManagerParams(class_name = u'QM Gold')
    qmp1.save()
    qmp1.environments= [e1]
    qmp1.dependsOn.add(qm1)
    qmp1.save()
    
    qm2 = QueueManager(instance_name = 'QM.GSC.QUA1' , port=1415, adminChannel = 'CANAL_HISTORIQUE')
    qm2.save()
    qm2.environments= [e5]
    qm2.dependsOn.add(s1)
    qm2.save()
    
    qmp2 = QueueManagerParams(class_name = u'QM Gold')
    qmp2.save()
    qmp2.environments= [e5]
    qmp2.dependsOn.add(qm2)
    qmp2.save()
    
    qm3 = QueueManager(instance_name = 'QM.IFPC.DEV1' , port=1414, adminChannel = 'CANAL_PREHISTORIQUE')
    qm3.save()
    qm3.dependsOn.add(s2)
    qm3.save()
    
    qmp3 = QueueManagerParams(class_name = u'QM IFPC pour Gold')
    qmp3.save()
    qmp3.environments= [e1]
    qmp3.dependsOn.add(qm3)
    qmp3.save()
    
    qmp4 = QueueManagerParams(class_name = 'QM IFPC pour Gold')
    qmp4.save()
    qmp4.environments= [e5]
    qmp4.dependsOn.add(qm3)
    qmp4.save()
    
    ########################################
    ## Oracle
    oi1 = OracleInstance(instance_name='GCDEV', port=1521, listener='BIDON')
    oi1.save()
    oi1.dependsOn = [s1]
    oi1.save()
    
    ose1 = OracleSchema(class_name='Schema Gold Events', instance_name='dev1evt')
    ose1.save()
    ose1.dependsOn = [oi1]
    ose1.environments = [e1]
    ose1.save()
    
    ose2 = OracleSchema(class_name='Schema Gold Events', instance_name='rec2evt')
    ose2.save()
    ose2.dependsOn = [oi1]
    ose2.environments = [e2]
    ose2.save()
    
    ose3 = OracleSchema(class_name='Schema Gold Central', instance_name='qua1cen')
    ose3.save()
    ose3.dependsOn = [oi1]
    ose3.environments = [e5]
    ose3.save()
    
    op1 = OraclePackage(class_name='P1')
    op1.save()
    op1.dependsOn = [ose1]
    op1.environments.add(e1)
    op1.save()
    
    op2 = OraclePackage(class_name='P2')
    op2.save()
    op2.dependsOn = [ose1]
    op2.environments.add(e1)
    op2.save()
    
    op3 = OraclePackage(class_name='P1')
    op3.save()
    op3.dependsOn = [ose2]
    op3.environments.add(e2)
    op3.save()
    
    op4 = OraclePackage(class_name='P2')
    op4.save()
    op4.dependsOn = [ose2]
    op4.environments.add(e2)
    op4.save()
    
    
    
    #################################################################################################
    ## Compo connections
    #################################################################################################
    
    ## QUA1 envt
    ose3.connectedTo.add(qmp2)
    qmp2.connectedTo.add(qmp4)
    qmp4.connectedTo.add(ifp2)
    
    ## DEV1
    ose1.connectedTo.add(qmp1)
    qmp1.connectedTo.add(qmp3)
    qmp3.connectedTo.add(ifp1)
    
    
    
    #################################################################################################
    ## GCL entries
    #################################################################################################
    
    ########################################
    ## Full delivery of a single IFPC folder
    l1 = Delivery(release_notes='Install initiale folder IF @TRUC', name='@TRUC_1_0', is_full=True)
    l1.save()
    ctv1 = ComponentTypeVersion(version='1.0', 
                                model=MageModelType.objects.get(model='ifpcfolder'), 
                                class_name='@TRUC')
    ctv1.save()
    l1.acts_on.add(ctv1)
    l1.save()
    
    ########################################
    ## Incremental patch of a single IFPC folder
    l2 = Delivery(release_notes='Mise a jour incrementielle folder IF @TRUC', name='HF_@TRUC_1_1', is_full=False)
    l2.save()
    ctv2 = ComponentTypeVersion(version='1.1', 
                                model=MageModelType.objects.get(model='ifpcfolder'), 
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
                                model=MageModelType.objects.get(model='ifpcfolder'), 
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
                                model=MageModelType.objects.get(model='ifpcfolder'), 
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
                                model=MageModelType.objects.get(model='ifpcfolder'), 
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
                                model=MageModelType.objects.get(model='ifpcfolder'), 
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
                                model=MageModelType.objects.get(model='ifpcfolder'), 
                                class_name='PATAPOUF')
    ctv9.save()
    l9.acts_on.add(ctv9)
    l9.save()
    
    ########################################
    ## Incremental patch of a single IFPC folder (== dependency)
    l10 = Delivery(release_notes='Mise a jour incrementielle folder IF PATAPOUF', name='PATAPOUF_1_1', is_full=False)
    l10.save()
    ctv10 = ComponentTypeVersion(version='1.1', 
                                model=MageModelType.objects.get(model='ifpcfolder'), 
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
                                model=MageModelType.objects.get(model='ifpcfolder'), 
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
                                model=MageModelType.objects.get(model='ifpcfolder'), 
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
                                model=MageModelType.objects.get(model='oraclepackage'), 
                                class_name='P1')
    ctv4.save()
    l4.acts_on.add(ctv4)
    l4.save()
    
    ########################################
    ## Delta delivery of a single Oracle Package (idiotic : packages cannot be delta delivered, but anyway)
    l5 = Delivery(release_notes='Patch package P1', name='P1_1_1', is_full=False)
    l5.save()
    ctv5 = ComponentTypeVersion(version='1.1', 
                                model=MageModelType.objects.get(model='oraclepackage'),
                                class_name='P1')
    ctv5.save()
    d5 = Dependency(installable_set = l5, type_version = ctv4, operator='==')
    d5.save()
    l5.acts_on.add(ctv5)
    l5.save()
    
    #transaction.commit()




createObjects()
