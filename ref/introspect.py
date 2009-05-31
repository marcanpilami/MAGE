# -*- coding: utf-8 -*-

""" 
    CSV referential access
    
    @author: Marc-Antoine Gouillart
    @contact: marsu_pilami@msn.com
    @license: GNU GVL v3
"""

#TODO: rename this file...

## Django imports
from django.db.models.loading import get_apps, get_model

## MAGE imports
from MAGE.ref.models import Component
from MAGE.ref.exceptions import *
from MAGE.ref.helpers_light import getComponent


def get_components_csv(compo_descr, envt_name = None, display_titles = False):
    """
        Builds a CSV from the content of the fields of some components.
        This function accepts three different descriptions for the components to describe, which can be mixed.
        It is posible to require components of different models or classes at a time.
        Fields are always returned in the same deterministic order.
        The separator is ';' 
         
        @param compo_descr: a list of components : either [ID1, ID2], 
            or [CompoObject1, CompoObject2, ...], or [[instance_name|class_name, parentname, ...], ...], or any mix.
        @param envt_name: name of the envt to which all components belong to. (optional)
        @param display_titles: true if you want each line to be preceded by the name of each field.
        
        @return: the csv in an unicode string
    """
    res = u""
    for element in compo_descr: 
        ## Retrieve the component
        compo = getComponent(element, envt_name)
        
        ## We have the component: analyse it.
        keys = compo.__dict__.keys()        
        keys.remove('id');keys.remove('class_name');keys.remove('instance_name');keys.remove('model_id')
        keys.sort()
        value_line = unicode(compo.__dict__['id']) + u';' + unicode(compo.model.model) + u';' + \
                    unicode(compo.__dict__['class_name']) + u';' + unicode(compo.__dict__['instance_name']) + u';'
        title_line = u'id;model;class_name;instance_name;'
        for key in keys:
            if key[0:1] == '_':
                ## Internal protected or private field, following usual Python conventions => don't return it.
                continue
                
            value_line += unicode(compo.__dict__[key]) + u';'
            title_line += key + u';'
        
        if display_titles:
            res += title_line + u'\n'
        res += value_line + u'\n'   
        
    return res