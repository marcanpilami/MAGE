# coding: utf-8

'''
Created on 17 mars 2013

@author: Marc-Antoine
'''

from dependencies import are_prerequisites_respected
from exceptions import MageScmError
import warnings
from scm.models import Installation, ComponentInstanceConfiguration
from datetime import datetime


def install_iset_envt(iset, envt, force_prereqs = False, install_date = datetime.now(), ticket = None):
    compos = envt.component_instances.filter(instanciates__isnull=False)
    install_iset(iset, compos, force_prereqs, install_date, ticket)

def install_iset(iset, targets, force_prereqs = False, install_date = datetime.now(), ticket = None):
    if not are_prerequisites_respected(iset, targets) and not force_prereqs:
        raise MageScmError('prerequisites are not valid')
    elif not are_prerequisites_respected(iset, targets) and force_prereqs:
        warnings.warn('prerequisites are not valid but this is a forced install') # debug info
        
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
            
    # Registration
    i = Installation(installed_set = iset, install_date = install_date, asked_in_ticket = ticket)
    i.save()
    
    for duet in install_detail:
        compo = duet[0]
        ii = duet[1]
        cic = ComponentInstanceConfiguration(component_instance = compo, result_of = ii, part_of_installation = i, created_on = install_date)
        cic.save() 
