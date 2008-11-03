# coding: utf-8

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


class SaveSet(InstallableSet):
    """ The Save object itself. It is not named "Save" due to a Django limitation"""
    unversioned_components = models.ManyToManyField(Component, verbose_name='Composants sauvegardés')
    versioned_components = models.ManyToManyField(ComponentVersion, verbose_name='Composants sauvegardés avec version (inclus dans unversioned_components')
    from_envt = models.ForeignKey(Environment)
    erased_on = models.DateField(verbose_name='Date de suppression des fichiers de la sauvegarde', blank=True, null=True)
    
    def __unicode__(self):
        return u'Sauvegarde n°%s de %s le %s (%s composants)' %(self.pk,
                                                                self.from_envt.name, 
                                                                self.set_date.strftime('%d/%m/%y %H:%M'), 
                                                                self.unversioned_components.count())

@transaction.commit_on_success
def save_full_environment(envt):
    """
    Create a new SaveSet of a full environment (including every Component)
    @param envt: the Environment object OR the environment name.
    @return: the new Save object
    """
    if not isinstance(envt, Environment):
        envt = Environment.objects.get(name=envt)
    
    sav = SaveSet(from_envt=envt, name='Sauvegarde FULL de ' + envt.name + 'le ' + strftime('%y%m%d%H%M%S'), is_full=True)
    sav.save()          # Create the PK !
    
    for compo in envt.component_set.all():
        add_compo_to_save(sav, compo)
    
    sav.save()
    return sav


def save_components(envt_name, compo_id_tuple):
    """
    Create a new SaveSet object containing the given Component objects.
    @return: the new SaveSet object
    """
    #TODO: write the function
    pass

def add_compo_to_save(saveset, compo):
    """
    Add a component to an existing SaveSet
    @param saveset: the SaveSet object (must already have a PK, i.e. having been saved at least once)
    @param compo: the component object OR the component ID.
    @return: nothing.
    """
    if not isinstance(compo, Component):
        compo = Component.objects.get(pk=compo)
    
    ## Register the saved component
    saveset.unversioned_components.add(compo)
    saveset.save()
    
    ## try to register the versioned component and subsequently build the InstallableSet
    try:    
        current_cv = compo.latest_cv
    except UndefinedVersion:
        # No version is defined => this component type and version won't be registered as installable parts of the IS.
        return
    
    saveset.acts_on.add(current_cv.version)
    saveset.versioned_components.add(current_cv)
    saveset.save()
    
    
    