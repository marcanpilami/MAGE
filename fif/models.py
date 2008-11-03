# coding: utf-8

###########################################################
## Informatica folder
###########################################################

#TODO: the IFPC components are not defined yet, those are just here for referential engine debug purposes

from django.db import models
from MAGE.ref.models import *
from django.contrib import admin

class IFPCFolder(Component):
    def _getProject(self):
        return self.dependsOn.get(model__model='oracleschema').leaf
    ifpc_project = property(_getProject) 
    
    detail_template = 'fif_folder_details.html'
    parents = {'ifpc_project':'IFPCProject'}
    
    def __unicode__(self):
        return u'%s' %(self.class_name) 

admin.site.register(IFPCFolder)

class IFPCProject(Component):
    pass