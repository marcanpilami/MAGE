# coding: utf-8

###########################################################
## Informatica folder
###########################################################

from django.db import models
from MAGE.ref.models import *


class IFPCFolder(Composant):
    #name = models.CharField(max_length=100)
    #if_project = models.ForeignKey(IFPC_Project)  ## No : should be a dependsOn relationship
    detail_template = 'mqqm/details.html'
     

