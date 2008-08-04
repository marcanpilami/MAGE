# coding: utf-8

###########################################################
## Sauvegardes
###########################################################

from django.db import models
from MAGE.gcl.models import InstallableSet
from MAGE.gcl.models import ComponentVersion
from MAGE.ref.models import Composant
from MAGE.ref.models import Environment
from django.contrib import admin

class Sauvegarde(InstallableSet):
    components = models.ManyToManyField(ComponentVersion, verbose_name='Composants sauvegardés et version')
    from_envt = models.ForeignKey(Environment)
    erased_on = models.DateField(verbose_name='Date de suppression des fichiers de la sauvegarde')