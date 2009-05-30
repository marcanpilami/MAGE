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
from MAGE.srv.models import *
from MAGE.ora.models import *
from MAGE.mqqm.models import *
from MAGE.fif.models import *


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
    
    #######################################
    # Servers
    s1 = Server(instance_name='XGCT1', os='AIX 5.3', comment='créé automatiquement', ip1="1.2.3.4")
    s1.save()
    
    s2 = Server(instance_name='XGCT2', os='AIX 5.3', comment='créé automatiquement', ip1="5.6.7.8")
    s2.save()
    
    #######################################
    # IFPC
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
    
    #######################################
    # MQ
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
    
    # QUA1 envt
    ose3.connectedTo.add(qmp2)
    qmp2.connectedTo.add(qmp4)
    qmp4.connectedTo.add(ifp2)
    
    # DEV1
    ose1.connectedTo.add(qmp1)
    qmp1.connectedTo.add(qmp3)
    qmp3.connectedTo.add(ifp1)


createObjects()
