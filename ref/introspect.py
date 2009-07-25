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
from MAGE.ref.helpers import filterMCL


def get_components_csv(compo_descr, display_titles = False, separator = ";"):
    """
        Builds a CSV from the content of the fields of some components.
        This function accepts three different descriptions for the components to describe, which can be mixed.
        It is posible to require components of different models or classes at a time.
        Fields are always returned in the same deterministic order.
        The separator is ';' by default 
         
        @param compo_descr: a list of components : either [ID1, ID2], 
            or [CompoObject1, CompoObject2, ...], or [[instance_name|class_name, parentname, ...], ...], or any mix.
        @param envt_name: name of the envt to which all components belong to. (optional)
        @param display_titles: true if you want each line to be preceded by the name of each field.
        
        @return: the csv in an unicode string
    """
    res = u""
    for mcl_string in compo_descr: 
        ## Retrieve the component
        compos = filterMCL(mcl_string)
        
        for compo in [c.leaf for c in compos]:
            ## We have the component: analyse it.
            keys = compo.__dict__.keys()        
            keys.remove('id');keys.remove('class_name');keys.remove('instance_name');keys.remove('model_id')
            keys.sort()
            value_line = unicode(compo.__dict__['id']) + separator + unicode(compo.model.model) + separator + \
                        unicode(compo.__dict__['class_name']) + separator + unicode(compo.__dict__['instance_name']) + separator
            title_line = u'id' + separator + 'model' + separator + 'class_name' + separator + 'instance_name' + separator
            for key in keys:
                if key[0:1] == '_':
                    ## Internal protected or private field, following usual Python conventions => don't return it.
                    continue
                    
                value_line += unicode(compo.__dict__[key]) + separator
                title_line += key + separator
            
            if display_titles:
                res += title_line + u'\n'
            res += value_line + u'\n'   
        
    return res