# coding: utf-8

"""
    MAGE backup sample module models and helper functions file.
    
    @author: Marc-Antoine Gouillart
    @contact: marsu_pilami@msn.com
    @license: GNU GVL v3
"""

###########################################################
## Sauvegardes
###########################################################

## Python imports
from datetime import date
from time import strftime

## Django imports
from django.db import models
from django.contrib import admin
from django.db import transaction

## Mage imports
from MAGE.gcl.models import InstallableSet, ComponentVersion, ComponentTypeVersion, UndefinedVersion
from MAGE.ref.models import Component
from MAGE.ref.models import Environment


class GroupComponentAssociation(models.Model):
    compo = models.ForeignKey(Component, verbose_name = u'composant à sauvegarder')
    batch = models.ForeignKey('BackupGroup')
    save_children = models.BooleanField(default = True, verbose_name = 'Sauvegarder récursivement les enfants')
    
    class Meta:
        verbose_name = u'contenu du groupe de sauvegarde'
        verbose_name_plural = u'contenu du groupe de sauvegarde'

class BackupGroup(models.Model):
    """ 
        This is a set of objects that is saved.
        It is a helper for save script (hey only have to know which batch they do save, not the componenents)
        
        It is not directly linked to environments, as saves can be server- or IS-wide, therefore
        saving components from many environments.
        
        By default, saving a component saves all its children 
    """
    name = models.CharField(max_length = 50, verbose_name=u'Nom du batch')
    components = models.ManyToManyField(Component, through = GroupComponentAssociation, verbose_name = u'composants sauvegardés')
    
    
    class Meta:
        verbose_name = u'groupe de composants de sauvegarde'
        verbose_name_plural = u'groupes de composants de sauvegarde'
    
    @transaction.commit_on_success
    def register_save(self):
        bs = BackupSet(name='Sauvegarde du groupe ' + self.name + 'le ' + strftime('%y%m%d%H%M%S'))
        bs.save()
        
        for compo in self.components.all():
            add_compo_to_backupset(bs, compo)


class BackupSet(InstallableSet):
    """ The Backup object itself. """
    comment = models.CharField(max_length = 100, verbose_name=u'commentaire')
    erased_on = models.DateField(verbose_name='Date de suppression des fichiers de la sauvegarde', blank=True, null=True)
    
    class Meta:
        verbose_name = 'sauvegarde'
        
    def __unicode__(self):
        return u'Sauvegarde n°%s - le %s (%s composants)' %(    self.pk,
                                                                self.set_date.strftime('%d/%m/%y %H:%M'), 
                                                                self.acts_on.count())

@transaction.commit_on_success
def save_full_environment(envt):
    """
        Create a new BackupSet of a full environment (including every Component)
        @param envt: the Environment object OR the environment name.
        @return: the new BackupSet object
    """
    if not isinstance(envt, Environment):
        envt = Environment.objects.get(name=envt)
    
    sav = BackupSet(name='Sauvegarde FULL de ' + envt.name + ' le ' + strftime('%y%m%d%H%M%S'), is_full=True)
    sav.save()          # Create the PK !
    
    for compo in envt.component_set.all():
        add_compo_to_backupset(sav, compo)
    
    sav.save()
    return sav


def add_compo_to_backupset(saveset, compo):
    """
        Add a component to an existing BackupSet
        @param saveset: the BackupSet object (must already have a PK, i.e. having been saved at least once)
        @param compo: the component object OR the component ID.
        @return: nothing.
    """
    if not isinstance(compo, Component):
        compo = Component.objects.get(pk=compo)
    
    try:    
        current_ctv = compo.latest_ctv
    except UndefinedVersion:
        current_ctv = ComponentTypeVersion(version = 'UNKNOWN - created by backups', model = compo.model, class_name = compo.class_name)
        current_ctv.save()
    
    saveset.acts_on.add(current_ctv)
    saveset.save()
    
    
    