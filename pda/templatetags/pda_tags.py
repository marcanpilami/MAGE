# coding: utf-8

from django import template
from django.template import Variable
from MAGE.ref.models import Component
import MAGE
register = template.Library()

##############################################################################
## Component_detail tag (experiment with exec)
##############################################################################
@register.simple_tag
def component_detail(comp_pk):
    c = Component.objects.get(pk=comp_pk).leaf 
    try:
        mod = c.description_view[:c.description_view.rfind('.')]
        exec ("import " + mod)
        exec("a = " + c.description_view + "(" + comp_pk.__str__() + ")")
        return a
    except:
        return "ERREUR"



##############################################################################
## More tag (experiment without exec, with context modification)
##############################################################################

@register.tag(name='more')
def compilation_more(parser, token):
    try:
        tag_name, component = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "Le tag %r a besoin d'un argument unique" %  token.contents.split()[0]
    return ComponentNode(component)

## Renderer
class ComponentNode(template.Node):
    def __init__(self, component):
        self.component = Variable(component)
    
    def render(self, context):
        comp = self.component.resolve(context).leaf
        if not isinstance(comp, Component):
            context['template_to_render'] = None
            context['comp'] = None
            return ""
        
        context['template_to_render'] = comp.detail_template
        context['comp'] = comp
        return ""