# coding: utf-8

## Python imports
import unicodedata



####################################################################################
## Options handling
####################################################################################

def default_label(component):
    res = '<'
    if component.class_name != component.model.name:
        res += component.model.name + "<br/>" + component.class_name 
    else:
        res += component.model.name
    if not component.instance_name is None and component.class_name != component.instance_name:
        res += "<br/>" + component.instance_name
    res += ">"
    return unicodedata.normalize('NFKD', res).encode('ascii','ignore') # Graphviz or pydot limitation

## Default options for building all graphs
__defaultGraphOptions = {
                            'allowDrawConnections':True,
                            'allowDrawChildren':True,
                            'shape':'ellipse',
                            'label':default_label,
                        }

__ModelsGraphOptions = {'default':__defaultGraphOptions}
def registerGraphOption(model, option_class):
    """
        Associates an options class (ie. a class with static fields such as "label", "shape"...) with a model, 
        so that this model will use the given options for all graphs rather than the default behaviour
    """
    modelOptions = __ModelsGraphOptions['default'].copy()
    for opt in modelOptions.iterkeys():
        try:
            modelOptions[opt] = getattr(option_class,opt)
        except AttributeError:
            pass
    __ModelsGraphOptions[model] = modelOptions


def getGraphOptions(model):
    try:
        return __ModelsGraphOptions[model]
    except KeyError:
        return __ModelsGraphOptions['default']