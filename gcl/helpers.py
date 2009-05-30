# coding: utf-8

## Python imports

## Django imports
from django.db import transaction

## MAGE imports
from MAGE.ref.models import Component, Environment
from MAGE.gcl.models import ComponentTypeVersion, InstallableSet, Tag, getComponentVersion
from MAGE.gcl.exceptions import *
from exceptions import MissingComponentException, FailedDependenciesCheckException, UndefinedVersion


##########################################################################################
## Installation functions
##########################################################################################

def arePrerequisitesVerified(envt_name, is_tocheck):
    for dep in is_tocheck.dependency_set.all():
        rs = Component.objects.filter(environments__name=envt_name, 
                                      class_name=dep.type_version.class_name, 
                                      model=dep.type_version.model)
        if rs.count() == 0:
            raise MissingComponentException(is_tocheck, dep.type_version, envt_name)
        
        for compo in rs.all():
            ## Retrieve current version
            try:
                ver = compo.latest_ctv
            except UndefinedVersion:
                raise FailedDependenciesCheckException(compo, dep.type_version) # No version = dep can't be verified!
            
            ## Check current version vs dependency
            if dep.operator == '==' and ver.compare(dep.type_version) != 0:
                raise FailedDependenciesCheckException(compo, dep.type_version)
            
            if dep.operator == '>=' and ver.compare(dep.type_version) < 0:
                raise FailedDependenciesCheckException(compo, dep.type_version)
            
            if dep.operator == '<=' and ver.compare(dep.type_version) > 0:
                raise FailedDependenciesCheckException(compo, dep.type_version)
    return True


def goToVersionThroughDeliveries(init_ctv, target_ctv):
    """
    Tries to build a Delivery chain between two given versions.
    The result chain may have side effects on all components of other types if applied globally.
    One of the shortest possible chain is returned. It is not guaranteed to be the optimal choice among them.
    
    @param init_ctv: Current version
    @param target_ctv: Version to reach
    
    @return: an ordered list of Delivery objects to apply.
    """   
    #print u'Aller de %s à %s' %(init_ctv, target_ctv)
    ## Test the consistency of arguments
    if init_ctv:   
        if init_ctv.model != target_ctv.model or init_ctv.class_name != target_ctv.class_name:
            raise Exception('Il est impossible d\'upgrader un composant vers un autre type !')
        
        comp = init_ctv.compare(target_ctv)
        if comp == 1:
            ## init should be installed after target
            raise InverseOrder()
     
        if comp == 0:
            if init_ctv.version == target_ctv.version:
                raise SameCTV()
            # If here : no chain can be built from init to target, let's hope FULL ISs will make it.
            
        ## If here : comp = -1, ie. Init should be installed before target : OK.
    
    class_name = target_ctv.class_name
    model = target_ctv.model
    
    ######################
    ## Loop : from the target ctv, we'll try to find the init ctv
    rs = InstallableSet.objects.filter(acts_on__class_name=class_name, 
                                       acts_on__model=model, 
                                       acts_on__version=target_ctv.version)
    
    ## Loop on all IS installing the target version
    potential_chains = []                    # This list will contain all potential chains, we'll return the shortest one
    for inst_set in rs:
        res_chain = [inst_set]
        if inst_set.is_full:
            ## A full IS is able to install the target version ! It takes precedence over every other IS.
            #print res_chain
            return res_chain
        
        ## Loop on all the requirements of this IS installing target (we try to reach init) 
        for ctv in inst_set.requirements.filter(class_name=class_name, model=model):
            ## Loop on all requirements (same type), try to recurse until we find init_ctv (or a full IS)
            if init_ctv and ctv.version == init_ctv.version:
                ## We've found our goal, stop !
                #print res_chain
                return res_chain
            
            ## If here : we haven't finished the recursion.
            if init_ctv and ctv.compare(init_ctv) != 1:
                ## Dead end
                continue
            
            ## If here : there is a possible chain between the 2 CTV => recurse
            new_chain = goToVersionThroughDeliveries(init_ctv, ctv)
            new_chain.insert(0, inst_set)
            potential_chains.append(new_chain)
    
    if potential_chains.__len__() == 0:
        raise Exception('pas trouve de chaine entre les 2 ! Un patch indispensable n\'a sans doutes pas ete reference.')       
    
    ##################
    ## Return the shortest chain found
    tmp = potential_chains[0]
    for chain in potential_chains:
        if chain.__len__() < tmp.__len__(): tmp = chain
    #print tmp
    return tmp



##########################################################################################
## Tag functions
##########################################################################################

@transaction.commit_on_success
def snapshot(tag_name, envt):
    if not isinstance(envt, Environment): envt = Environment.objects.get(name=envt)
    compos = envt.component_set.all()
    t = Tag(name=tag_name, from_envt = envt)
    t.save()    # Create PK
    
    for compo in compos:
        try:
            print compo
            ctv = getComponentVersion(compo)
        except UndefinedVersion:
            ## Version is undefined: this component type won't be referenced in the tag.
            ##   (would be useless to reference an unknown version in a tag...)
            continue
        if ctv not in t.versions.all(): t.versions.add(ctv)
    t.save()
    return t
    
#TODO: finish function (list fusion is too basic) => to be done when IS.compare(IS) is done
def goToTagThroughDeliveries(envt, tag):
    """
       Creates a list of deliveries to install on an environment so as to reach a certain tag conf level.
       @param envt: name of the environment, OR the envt object
       @param tag:  name of the tag, or the Tag object.
       @return: an ordered list of IS to apply.
    """
    if not isinstance(envt, Environment):
        envt = Environment.objects.get(name=envt)
    if not isinstance(tag, Tag):
        tag = Tag.objects.get(name=tag)
    
    is_list = []
      
    for target_ctv in tag.versions.all():
        is_tmp_list = []
        compos_to_upgrade = envt.component_set.filter(model = target_ctv.model, class_name = target_ctv.class_name)
        
        if compos_to_upgrade.count() == 0:
            is_tmp_list = goToVersionThroughDeliveries(None, target_ctv)
        
        for compo in compos_to_upgrade:
            try:
                init_ctv = compo.latest_ctv
            except UndefinedVersion:
                init_ctv = None
            is_tmp_list = goToVersionThroughDeliveries(init_ctv, target_ctv)
            
        for i_set in is_tmp_list:
            if i_set not in is_list:
                is_list.append(i_set)
    
    return is_list    



##########################################################################################
## Consistency check functions
##########################################################################################

def check_impact_on_component(compo_tocheck, is_chain):
    """This function returns the final version of a component that would result from the application 
    of the given IS string.
    It is not restricted to Deliveries or SaveSets
    It will not test the consistency of the chain.
    
    @param compo_tocheck: the component that will be checked
    @param is_chain: the ordered list of IS to virtually apply on this component. (The first IS to apply is 
    the 1st element of the list.)
    
    @return: the final CTV.
    """ 
    cn = compo_tocheck.class_name
    m = compo_tocheck.model
    
    for inst_set in is_chain:
        try:
            return inst_set.acts_on.get(class_name=cn, model=m).version
        except ComponentTypeVersion.DoesNotExist:
            continue
    
    ## If here : the chain does not affet the component.
    return compo_tocheck.version


def check_is_chain_consistent(is_chain, cur_envt = None):
    """
    Checks whether a given IS suite respects internal dependencies.
    It verifies that every change induced by an IS is compatible with the following IS.
    
    @param is_chain: the ordered list of IS to apply. (First element is applied first)
    @return: True if the chain is internally consistent, False otherwise.
    """
    cur_is = is_chain[0]
    is_result_ctv = cur_is.acts_on.all()
    if not cur_envt: cur_envt = []
    #print u'Analyse compatibilité entre l\'IS %s et l\'envt virtuel %s' %(cur_is, cur_envt)
    
    ## Check the internal consistancy of the IS
    model_class = []
    for ctv in is_result_ctv:
        str = ctv.class_name + ctv.model.model
        if str in model_class:
            raise InconsitantIS(cur_is)
        model_class.append(str)
    
    ## Dependency check
    for dep in cur_is.dependency_set.all():
        dep_ctv = dep.type_version
        dep_type = dep.operator
        
        ## Look for a ctv of the same model and class in the virtual envt.
        ##    If there are none, as the virtual envt is incomplete, no pbs.
        ##    If there is one (always only one thanks to the previous test), check its version
        for virtual_ctv in cur_envt:
            if virtual_ctv.class_name == dep_ctv.class_name and virtual_ctv.model == dep_ctv.model:
                if dep_type == '==' and virtual_ctv.version != dep_ctv.version:
                    return False
                if dep_type == '>=' and virtual_ctv.compare(dep_ctv) < 0:
                    return False
                if dep_type == '<=' and virtual_ctv.compare(dep_ctv) > 0:
                    return False
    
    ## Update the virtual envt with the new versions
    for ctv in is_result_ctv:        
        for ctv_old in cur_envt:
            if ctv_old.class_name == ctv.class_name and ctv_old.model == ctv.model:
                # This is an update of a compo that was already present in the virtual envt
                if ctv_old.compare(ctv) > 0:
                    return False
                    #raise Exception('Situation impossible. Bateau, hein ?')
                cur_envt.remove(ctv_old)
            
        ## Insert the new ctv in the virtual envt (if existing, the old one has been deleted)
        cur_envt.append(ctv)
    
    ## Recurse & terminaison 
    #print u'Environnement virtuel : %s' %(cur_envt) 
    if is_chain.__len__() > 1:      
        return check_is_chain_consistent(is_chain[1:], cur_envt)
    else:
        return True  
