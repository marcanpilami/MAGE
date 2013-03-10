'''
Created on 8 mars 2013

@author: Marc-Antoine
'''

## Django imports
from django.contrib.contenttypes.models import ContentType
from ref.models import ComponentInstance

def list_component_models():
    """Returns a list of all instanciable component models present in MAGE"""
    res = []
    for model in ContentType.objects.all():
        if issubclass(model.model_class(), ComponentInstance) and model.model_class() != ComponentInstance:
            res += [model]
    return res 