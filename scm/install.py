# coding: utf-8
'''
    @license: Apache License, Version 2.0
    @copyright: 2007-2013 Marc-Antoine Gouillart
    @author: Marc-Antoine Gouillart
'''

## Python imports
from datetime import timedelta

## Django imports
from django.utils.timezone import now

## MAGE imports
from scm.exceptions import MageScmError, MageScmCallerError,\
    MageScmFailedEnvironmentDependencyCheck
from scm.models import Installation, ComponentInstanceConfiguration
from prm.models import getParam


def install_iset_envt(iset, envt, force_prereqs = False, install_date = now(), ticket = None):
    compos = envt.component_instances.filter(instanciates__isnull=False)
    install_iset(iset, compos, envt, force_prereqs, install_date, ticket)

def install_iset(iset, targets, envt, force_prereqs = False, install_date = None, ticket = None, ii_selection = None):
    ## Check arguments
    if ii_selection is None:
        ii_selection = iset.set_content.all()
    for ii in ii_selection:
        if ii.belongs_to_set != iset:
            raise MageScmCallerError('an Installable Item does not belong to the specified set')
    if install_date is None:
        install_date = now()
    
    ## Check prerequisites
    try:
        iset.check_prerequisites(envt.name, ii_selection)
    except MageScmFailedEnvironmentDependencyCheck, e:
        if not force_prereqs:
            raise e
    
    ## Select targets
    install_detail = []
    for compo in targets:
        ## Is the compo patchable?
        if not compo.instanciates:
            raise MageScmError('a given component\'s configuration cannot be managed as it has no implementation class')
        
        ## Is there a corresponding element in the IS? (same CIC (through IM))
        ii_list = iset.set_content.filter(how_to_install__method_compatible_with=compo.instanciates).filter(what_is_installed__logical_component = compo.instanciates.implements).order_by('pk') # sort PK: gives patch order
        if ii_list.count() == 0:
            continue  
    
        ## If here, there are IS concerning the component. Mark them for install.
        for ii in ii_list:
            install_detail.append((compo, ii))
            
    ## Registration
    i = Installation(installed_set = iset, install_date = install_date, asked_in_ticket = ticket)
    i.save()
    
    for duet in install_detail:
        compo = duet[0]
        ii = duet[1]
        cic = ComponentInstanceConfiguration(component_instance = compo, result_of = ii, part_of_installation = i, created_on = install_date)
        cic.save() 
        
def install_ii_single_target_envt(ii, instance, envt, force_prereqs = False, install_date = now(), ticket = None, install = None):
    iset = ii.belongs_to_set
    
    ## Check prerequisites
    try:
        iset.check_prerequisites(envt.name)
    except MageScmFailedEnvironmentDependencyCheck, e:
        if not force_prereqs:
            raise e

    if install is None:
        ## Check if an install is in progress
        limit = int(getParam('APPLY_MERGE_LIMIT'))
        tlimit1 = install_date - timedelta(minutes=limit)
        tlimit2 = install_date + timedelta(minutes=limit)
        installs = Installation.objects.filter(installed_set = iset, modified_components__component_instance__environments = envt, 
                                               install_date__lte = tlimit2, install_date__gte = tlimit1)
        if limit != 0 and installs.count() > 0:
            ## If here, there are installs running on the same environment on the same ISET. Check the II is not already installed.
            for ins in installs:
                if not ii.id in [i.result_of_id for i in ins.modified_components.all()]:
                    install = ins
                    break

    if install is None:
        install = Installation(installed_set = iset, install_date = install_date, asked_in_ticket = ticket)
        install.save()
    
    cic = ComponentInstanceConfiguration(component_instance = instance, result_of = ii, part_of_installation = install, created_on = install_date)
    cic.save() 
    
    return install
    