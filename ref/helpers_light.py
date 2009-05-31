# -*- coding: utf-8 -*-

"""
    MAGE referential module helper functions.
    
    @deprecated: Replaced by helpers.py file. Will be deleted in v4 final.
    
    @author: Marc-Antoine Gouillart
    @contact: marsu_pilami@msn.com
    @license: GNU GVL v3
"""

## Django imports
from django.db.models.loading import get_apps, get_model

## MAGE imports
from MAGE.ref.models import *
from MAGE.ref.exceptions import *


def getComponent(compo_descr, envt_name = None):
    """
        Finds a component.
        @param compo_descr: the descripton of a component: either its ID, or the object itself, 
            or [name, parentname, ...] (where 'name' is either the class_name or the instance_name)
        @param envt_name: name of the envt to which the component belongs to. (optional)
        
        @return: the desired Component object (if not, raises an exception)
    """
    ## Find the compo object according to the type of the argument
    compo = None
    if isinstance(compo_descr, int) or isinstance(compo_descr, str) or isinstance(compo_descr, unicode):
        ## A PK was given
        try:
            return  Component.objects.get(pk=compo_descr).leaf
        except Component.DoesNotExist:
            raise UnknownComponent(compo_descr)
        except ValueError:
            pass
    if isinstance(compo_descr, Component):
        ## A compo object was directly given
        return compo_descr.leaf
    try:
        if isinstance(compo_descr, list) and compo_descr.__len__() == 1 and int(compo_descr[0]):
            ## A PK was given inside a list
            return Component.objects.get(pk=compo_descr[0]).leaf
    except: pass
    if isinstance(compo_descr, list) and not compo:
        ## A list describing the element was given
        return __getComponentViaParents(compo_descr, envt_name).leaf # can raise custom exceptions
    else:
        raise UnknownComponent(compo_descr)


def __getComponentViaParents(compo_descr, envt_name = None):
    """Finds a component given its instance_name or class_name, and optionaly its parents' names 
    @param compo_descr: an ordered list [name, parent_name, grandparent_name, ...] (where name is either class_name or instance_name)
    @param envt_name: the environment name. Optionnal !
    @return: the component instance if found. (raises an exception if not)
      
    @raise UnknownComponent: if no component can be found with the given component description
    @raise TooManyComponents: if multiple components are returned using the given component description
    @raise UnknownParent: if a specified parent field doesn't exist""" 

    ## First selection : environment, type and compo name
    rs = Component.objects.filter(class_name=compo_descr[0]) | \
                Component.objects.filter(instance_name=compo_descr[0])
    
    if envt_name != None:
        rs = rs.filter(environments__name=envt_name)
    if rs.count() == 0:
        raise UnknownComponent(compo_descr, envt_name)
    if rs.count == 1:
        return rs.all()[0]

    ## Refine the selection with parents' names
    i = 1
    while i < len(compo_descr): #and rs.count() > 1:
        ## Django query construction
        d = {}
        d2 = {}
        papa = ""
        for p in range(0,i):
            papa = papa + "dependsOn__"
        d[papa +'class_name'] = compo_descr[i]
        d2[papa +'instance_name'] = compo_descr[i]
        
        ## Query
        rs = rs.filter(**d) | rs.filter(**d2)
        
        ## Iteration
        i=i+1
 
    ## We are at the end of our knowledge, we have failed if the compo is still unfound
    if rs.count() > 1:
        raise TooManyComponents(compo_descr)
    if rs.count() == 0:
        raise UnknownComponent(compo_descr, envt_name)
    
    ## Return the one and only component
    return rs.all()[0]