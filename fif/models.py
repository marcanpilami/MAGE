# coding: utf-8

###########################################################
## Informatica folder
###########################################################

from django.db import models
from MAGE.ref.models import *
from django.contrib import admin

class IFPCFolder(Composant):
    #name = models.CharField(max_length=100)
    #if_project = models.ForeignKey(IFPC_Project)  ## No : should be a dependsOn relationship
    detail_template = 'mqqm/details.html'
    
    def __unicode__(self):
        return u'%s' %(self.name) 

admin.site.register(IFPCFolder)