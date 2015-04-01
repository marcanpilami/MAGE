# coding: utf-8

from django import template
from django.db import models
from ref.models import ExtendedParameterDict
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def verbose_name(value):
    return value._meta.verbose_name

@register.filter
def ksh_protect_and_quote(value):
    if isinstance(value, bool) and value:
        return "1"
    elif isinstance(value, bool) and not value:
        return "0"

    if isinstance(value, int):
        return value

    if isinstance(value, ExtendedParameterDict):
        return '"%s"' % value

    if type(value).__name__ == 'ManyRelatedManager':
        return '"' + ','.join([a.name for a in value.all()]) + '"'

    if value is None:
        return '""'

    if isinstance(value, models.Model):
        return '"%s"' % value.pk

    res = ("%s" % value).replace('"', '\\"')
    return ('"%s"' % res)

@register.filter
def apply_field_template(component_instance, computed_field):
    return computed_field.resolve(component_instance)

@register.filter()
def urlify(value):
    if (isinstance(value, str) or isinstance(value, unicode)) and value.startswith('http'):
        return mark_safe(("<a href='%s'>cliquez ici</a>" % value))
    else:
        return value

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
