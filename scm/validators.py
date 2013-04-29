# coding: utf-8

from django.core.exceptions import ValidationError

def validate_non_empty(value):
    if value is None or len(value) == 0:
        raise ValidationError(u'un élément minimum requis')