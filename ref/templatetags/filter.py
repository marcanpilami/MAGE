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

    res = ("%s" % value).replace('"', '\\"').replace('$', '\$')
    return ('"%s"' % res)

@register.filter
def apply_field_template(component_instance, computed_field):
    return computed_field.resolve(component_instance)

''' Returns (field_descr, field_value_or_None). Single pass method. Both lists must be sorted beforehand. '''
@register.filter
def project_ci_fields(descriptions, instances):
    i = instances.__iter__()
    n = next(i, None)
    for field_descr in descriptions:
        if n is not None and n.field_id == field_descr.pk:
            yield (field_descr, n.value)
            n = next(i, None)
        else:
            yield (field_descr, None)

@register.filter()
def urlify(value):
    if (isinstance(value, str) or isinstance(value, unicode)) and value.startswith('http'):
        if len(value.split('|')) == 2:
            link = value.split('|')[1]
            value = value.split('|')[0]
        else:
            link = 'cliquez ici'
        return mark_safe(("<a href='%s'>%s</a>" % (value, link)))
    elif (isinstance(value, str) or isinstance(value, unicode)) and value == 'True':
        return mark_safe("<span class='glyphicon glyphicon-ok' aria-hidden='true'></span>")
    elif (isinstance(value, str) or isinstance(value, unicode)) and value == 'False':
        return mark_safe("<span class='glyphicon glyphicon-remove' aria-hidden='true'></span>")
    elif value is None:
        return ''
    else:
        return value

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
