'''
Created on 8 mars 2013

@author: Marc-Antoine
'''

from cStringIO import StringIO
import csv

def get_components_csv(component_instances = (), display_titles = False):
    output = StringIO()
    
    if component_instances.count() == 0:
        return ""
    
    keys = []
    for compo in component_instances:
        keys = list(set(compo.leaf.__dict__.keys()) | set(keys))              
    keys.remove('model_id');keys.remove('_state')
    wr = csv.DictWriter(output, keys, quoting=csv.QUOTE_ALL, extrasaction='ignore')
    wr.writeheader()
    
    for compo in component_instances:
        compo = compo.leaf
        
        #keys = compo.__dict__.keys()        
        #keys.remove('id');keys.remove('class_name');keys.remove('instance_name');keys.remove('model_id')
        #keys.sort()
        
        wr.writerow(compo.__dict__)
        
    res = output.getvalue()
    output.close()
    return res


