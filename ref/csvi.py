# coding: utf-8
'''
    @license: Apache License, Version 2.0
    @copyright: 2007-2013 Marc-Antoine Gouillart
    @author: Marc-Antoine Gouillart
'''

from cStringIO import StringIO
import csv


def get_components_exportable_attributes(component_instances=(), displayRestricted=False):
    keys = set()
    for compo in component_instances:
        compo.leaf.__dict__['component_type'] = compo.model.model
        keys = set(compo.exportable_fields(displayRestricted)) | set(keys)
    keys=list(keys)
    #keys.remove('model_id');keys.remove('_state');keys.append('environments')
    return keys

def get_components_csv(component_instances=(), display_titles=False, outputFile=None, displayRestricted=False):
    if not outputFile:
        output = StringIO()
    else:
        output = outputFile
        
    if len(component_instances) == 0:
        return ""
    
    keys = get_components_exportable_attributes(component_instances, displayRestricted)
    
    wr = csv.DictWriter(output, fieldnames=keys, restval="", extrasaction='ignore', dialect='excel', delimiter=";")
    if display_titles:
        wr.writeheader()
    
    for compo in component_instances:
        compo = compo.leaf   
        compo.__dict__['environments'] = ",".join([i[0] for i in compo.environments.values_list('name')])     
        wr.writerow(compo.__dict__)
        
    if not outputFile:
        res = output.getvalue()
        output.close()
        return res
    # else, no need to return anything - the CSV is written in the file


def get_components_pairs(component_instances=(), displayRestricted=False):
    keys = get_components_exportable_attributes(component_instances, displayRestricted)
    res = []
    
    for compo in component_instances:
        tmp = []
        compo = compo.leaf
        for key in keys:
            try:
                tmp.append({"key":key, "value":getattr(compo, key)})
            except AttributeError:
                pass
        res.append(tmp)

    return res