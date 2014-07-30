# coding: utf-8

"""
    Graph module main file.
    This is a part of the MAGE core.
    
    @license: Apache License, Version 2.0
    @copyright: 2007-2013 Marc-Antoine Gouillart
    @author: Marc-Antoine Gouillart
"""

## Python imports
import unicodedata

## MAGE imports
from ref.models import ComponentInstance
from prm.models import getMyParams
from helpers import MageDC

## PYDOT imports
from pydot import Node, Edge

  
####################################################################################
## Drawing context
####################################################################################    

class DrawingContext(MageDC):
    def __init__(self):
        MageDC.__init__(self)
        
        ## Settings
        self.collapsed_nodes = {}
        self.parentRecursionLevel = 0
        self.patnersRecursionLevel = 0
        self.collapse_threshold = 3             ## if nbBrothers >= this, collapse!
        
        ## Components to draw
        self.components = None
        
        ## Presentation
        tmp = getMyParams()  ## We cache the params
        self.draw_compo_default = {}
        self.draw_compo_data = {}
        for param in tmp.filter(axis1='presentation default'):
            self.draw_compo_default[param.key] = param.value 
        for param in tmp.filter(model__pk__isnull=False):
            if not self.draw_compo_data.has_key(param.model.model): self.draw_compo_data[param.model.model] = {}
            self.draw_compo_data[param.model.model][param.key] = param.value
    
    #################################
    ## Recursion
    def getParentRecursionLevel(self, component):
        if self.parent_node_recursion_level.__contains__(component):
            return self.parent_node_recursion_level[component]
        else:
            return 0
    
    #################################
    ## Node aspect
    def getPresParam(self, key, component):
        model = component.model.model
        if self.draw_compo_data.has_key(model) and self.draw_compo_data[model].has_key(key):
            return self.draw_compo_data[model][key]
        return self.draw_compo_default[key]
    
    def build_label(self, component):
        res = '<'
        res += component.model.name
        if not component.name is None:
            res += "<br/>" + component.name
        elif component.instanciates is not None:
            res += "<br/>" + component.instanciates.name
        res += ">"
        return self.encode(res)
    


####################################################################################
## Functions to build the graphs
####################################################################################

def getGraph(django_filters={}, filename=None, context=None, django_filter_unnamed = ()):
    """
        draws (or stores) a map of all components and of their interactions
    """
    dc = context or DrawingContext()
    dc.components = ComponentInstance.objects.select_related().filter(*django_filter_unnamed, **django_filters)
    dc.set_simplify('true')
    dc.set_bgcolor('#F5F0F2')
    dc.set_concentrate('true')
    
    for compo in dc.components:
        if not compo.deleted:
            drawNode(compo, dc)
    
    if filename is None:
        return dc.render()
    else:
        dc.writeFile(filename)
    


####################################################################################
## Helpers
####################################################################################

def drawNode(component, context):
    """
        The dotGraph object will be updated to contain the component
        @warning: the context object given in argument is modified by the function!
    """   
    ## Retrieve (or create) the graph node for the current component
    alreadyExist = __nodeExists(component, context)
    curNode = __getNode(component, context, createIfAbsent=True)
    if not alreadyExist: context.add_node(curNode) 
    else: return curNode
    
    ## connectedTo
    for linkedCompo in component.connectedTo.all():
        if __nodeExists(linkedCompo, context): ## Already drawn. That way, we avoid the two-way-rel.
            # Draw (possibly the node) and the edge
            linkedNode = drawNode(linkedCompo, context) # recursion. Creates node if not already drawn.
            e = Edge(curNode, linkedNode, weight = '0', penwidth='5')
            e.set_arrowhead('none')
            e.set_color('antiquewhite4')
            context.add_edge(e)
    
    ## dependsOn
    for daddy in component.dependsOn.all():  
        if isCompoToBeDrawn(daddy, context):
            # Draw (possibly the node) and the edge
            linkedNode = drawNode(daddy, context) # recursion
            e = Edge(curNode, linkedNode, weight = '100')
            #e.set_style('dotted')
            e.set_color('blue2')
            context.add_edge(e)
    
    return curNode

def isCompoToBeDrawn(component, context):
    """
        Returns true if the component has already been drawn or if it is going to be
    """
    ## In the list of selected compo?
    if context.components.filter(pk=component.pk).exists(): return True
    
    ## Already drawn?
    if __nodeExists(component, context): return True
    
    ## Out of the selected components, but at an acceptable level of recursion?
    if __getRecLevelDO(component, context) <= context.parentRecursionLevel: return True
    if __getRecLevelCT(component, context) <= context.patnersRecursionLevel: return True
    
    ## else return false
    return False

def __getRecLevelDO(component, context, done = []):
    if context.components.filter(pk=component.pk).count() == 1:
        return 0
    rec_level = 999
    done.append(component)
    
    for daddy in component.subscribers.all():
        if daddy in done:
            continue
        i = __getRecLevelDO(daddy, context, done)
        if i < rec_level:
            rec_level = i
    return rec_level + 1

def __getRecLevelCT(component, context, prev=None):
    if context.components.filter(pk=component.pk).count() == 1:
        return 0
    rec_level = 999
    for daddy in component.connectedTo.all() | ComponentInstance.objects.filter(connectedTo=component):
        if daddy == prev: continue
        i = __getRecLevelCT(daddy, context, component)
        if i < rec_level:
            rec_level = i
    return rec_level + 1

def __nodeExists(component, context):
    return __getNode(component, context, False) is not None

def __getNode(component, context, createIfAbsent=True):
    ## The node may already exist in the graph. Since all operations on it are done at creation, we can return it at once.
    n = context.get_node(name=str(component.pk)) 
    if type(n) == Node:
        return n 
    elif (n is not None) and (len(n) > 0) and type(n[0]) == Node: ## get_node returns [] if not found.
        return n[0]
    else:
        n = None

    ## If the node is marked as collapsed, return the collapse artefact
    if context.collapsed_nodes.__contains__(component):
        return context.collapsed_nodes[component]
    
    ## If execution gets here : the node does not exist.
    if not createIfAbsent:
        return None
    
    ## Create the node
    n = __createNode(component, context)
    
    ## Should the node be collapsed?             
    if component.environments.count() <= 1:          ## Multi envt nodes should never be collapsed.
        nbBrothers = 1
        for parent in component.dependsOn.all():
            rs = parent.subscribers.filter(model=component.model, environments__in=component.environments.all())
            nbBrothers += rs.count() - 1
            if rs.count() >= context.collapse_threshold:
                ## Change the node into a collapse artifact
                n.set_label('<%s instances de<br/>%s>' % (nbBrothers, unicodedata.normalize('NFKD', component.model.name).encode('ascii', 'ignore')))
                ## Mark brothers as collapsed
                for brother in rs:
                    context.collapsed_nodes[brother] = n
    
    ## End : return the node   
    return n       
    

def __createNode(component, context):
    ## Build node
    curNode = Node(str(component.pk))
    curNode.set_label(context.build_label(component))
    curNode.set_shape(context.getPresParam('node_shape', component))
    
    ## Node color (by environments)
    if component.environments.count() > 0:
        curNode.set_fillcolor(context.getObjectColour(component.environments.all()[0].name))          
        curNode.set_style(context.getPresParam('node_style', component))
    else:
        curNode.set_fillcolor('floralwhite')
        curNode.set_style('filled')
    curNode.set_fontname('Segoe UI')
    curNode.set_fontsize('12')
    
    ## Return the node
    return curNode
