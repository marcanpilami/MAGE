# coding: utf-8
'''
    @license: Apache License, Version 2.0
    @copyright: 2007-2013 Marc-Antoine Gouillart
    @author: Marc-Antoine Gouillart
'''

from django.core.exceptions import ValidationError

def validate_non_empty(value):
    if value is None or len(value) == 0:
        raise ValidationError(u'un élément minimum requis')