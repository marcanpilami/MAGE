# coding: utf-8
'''
    @license: Apache License, Version 2.0
    @copyright: 2007-2013 Marc-Antoine Gouillart
    @author: Marc-Antoine Gouillart
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