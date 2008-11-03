# coding: utf-8

from django import template
from django.template import Variable
from MAGE.ref.models import Component
from MAGE.sav.models import SaveSet

register = template.Library()

##############################################################################
## 
##############################################################################
@register.simple_tag
def component_saved_version(comp_pk, saveset_pk):
    try:
        c = Component.objects.get(pk=int(comp_pk))
    except:
        return "Erreur PK composant %s" %comp_pk
    try:
        i = SaveSet.objects.get(pk=int(saveset_pk))
    except:
        return "Erreur PK sauvegarde %s" %saveset_pk
    
    try:
        cv = i.versioned_components.get(component__pk=int(comp_pk))
    except:
        return "Composant non versionné lors de la sauvegarde."
    return cv.version.version
    