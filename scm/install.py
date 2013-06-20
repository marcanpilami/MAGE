# coding: utf-8

'''
Created on 17 mars 2013

@author: Marc-Antoine
'''

import warnings
from datetime import datetime

from scm.exceptions import MageScmError, MageScmCallerError,\
    MageScmFailedEnvironmentDependencyCheck
from scm.models import Installation, ComponentInstanceConfiguration



def install_iset_envt(iset, envt, force_prereqs = False, install_date = datetime.now(), ticket = None):
    compos = envt.component_instances.filter(instanciates__isnull=False)
    install_iset(iset, compos, envt, force_prereqs, install_date, ticket)

def install_iset(iset, targets, envt, force_prereqs = False, install_date = datetime.now(), ticket = None, ii_selection = None):
    ## Check arguments
    if ii_selection is None:
        ii_selection = iset.set_content.all()
    for ii in ii_selection:
        if ii.belongs_to_set != iset:
            raise MageScmCallerError('an Installable Item does not belong to the specified set')
    
    ## Check prerequisites
    try:
        iset.check_prerequisites(envt.name, ii_selection)
    except MageScmFailedEnvironmentDependencyCheck, e:
        if force_prereqs:
            warnings.warn('prerequisites are not valid but this is a forced install') # debug info
        else:
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
        
def install_ii_single_target_envt(ii, instance, envt, force_prereqs = False, install_date = datetime.now(), ticket = None, install = None):
    iset = ii.belongs_to_set
    
    ## Check prerequisites
    try:
        iset.check_prerequisites(envt.name, (instance,))
    except MageScmFailedEnvironmentDependencyCheck, e:
        if force_prereqs:
            warnings.warn('prerequisites are not valid but this is a forced install') # debug info
        else:
            raise e

    if install is not None:
        pass
    else:
        install = Installation(installed_set = iset, install_date = install_date, asked_in_ticket = ticket)
        install.save()
    
    cic = ComponentInstanceConfiguration(component_instance = instance, result_of = ii, part_of_installation = install, created_on = install_date)
    cic.save() 
    
    return install
    