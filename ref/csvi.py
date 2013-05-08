'''
Created on 8 mars 2013

@author: Marc-Antoine
'''

from cStringIO import StringIO
import csv

def get_components_csv(component_instances=(), display_titles=False, outputFile=None, displayRestricted=False):
    if not outputFile:
        output = StringIO()
    else:
        output = outputFile
        
    if len(component_instances) == 0:
        return ""
    
    keys = ()
    for compo in component_instances:
        compo.leaf.__dict__['component_type'] = compo.model.model
        if displayRestricted:
            keys = list(set(compo.leaf.__dict__.keys()) | set(keys))
        else:      
            keys = list(set([ i for i in compo.leaf.__dict__.keys() if i not in compo.leaf.restricted_fields]) | set(keys))
    keys.remove('model_id');keys.remove('_state');keys.append('environments')
    
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


