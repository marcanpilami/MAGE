# coding: utf-8

## Python imports
import unicodedata

## MAGE imports
from MAGE.ref.models import Component
from register import getGraphOptions

## PYDOT imports
from pydot import *


## Hypothesis: -graph options cannot be changed by the end user
##             -no model named 'default'

  
  
####################################################################################
## Draw context
####################################################################################    

class DrawingContext():
    def __init__(self):
        """default init"""
        self.envt_colours = {}
        self.cur_colour = 0
        self.collapsed_nodes = {}
        self.graph = Dot(overlap="false", graph_type='digraph', splines="true")
        self.parentRecursionLevel = 0
        self.patnersRecursionLevel = 0
        self.components = None
        self.collapse_threshold = 3             ## if nbBrothers >= this, collapse!
    
    #################################
    ## Rendering functions
    def render(self):
        for compo in self.components:
            drawNode(compo, self)
        return self.graph.create(format='png', prog='dot')
    
    def writeFile(self, filepath):
        for compo in self.components:
            drawNode(compo, self)
        return self.graph.write(path=filepath, format='png', prog='dot')
    
    #################################
    ## Envt colour handling
    colours = ['bisque1', 'darkorange', 'gold1', 'mediumseagreen', 'skyblue', 'orchid', 'gray']
    def getEnvtColor(self,envt_name):
        try:
            return self.envt_colours[envt_name]
        except:
            pass
        self.envt_colours[envt_name] = self.colours[self.cur_colour]
        if self.cur_colour == self.colours.__len__() - 1:
            self.cur_colour = 0
        else:
            self.cur_colour += 1
        return self.envt_colours[envt_name]
    
    #################################
    ## Recursion
    def getParentRecursionLevel(self, component):
        if self.parent_node_recursion_level.__contains__(component):
            return self.parent_node_recursion_level[component]
        else:
            return 0



####################################################################################
## Functions to build the graphs
####################################################################################

def getGraph(django_filters = {}, filename = None, context = None):
    """
        draws a map of all components and of their interactions
    """
    if context is None: dc = DrawingContext()
    else: dc = context
    dc.components = Component.objects.filter(**django_filters)
    #dc.graph.set_simplify(True) #BUG: in pydot?
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
        @warning: the context object given in argument is modified by the function !
    """
    ## Retrieve draw options
    options = getGraphOptions(component.leaf.__class__)
    
    ## Retrieve (or create) the graph node for the current component
    alreadyExist = __nodeExists(component, context)
    curNode = __getNode(component, context)
    if not alreadyExist: context.graph.add_node(curNode) 
    else: return curNode
    
    ## connectedTo
    for linkedCompo in component.connectedTo.all():
        if isCompoToBeDrawn(linkedCompo, context):
            # Draw (possibly the node) and the edge
            linkedNode = drawNode(linkedCompo, context) # recursion
            e = Edge(curNode, linkedNode)
            e.set_arrowhead('none')
            context.graph.add_edge(e)
    
    ## dependsOn
    for daddy in component.dependsOn.all():  
        if isCompoToBeDrawn(daddy, context):
            # Draw (possibly the node) and the edge
            linkedNode = drawNode(daddy, context) # recursion
            e = Edge(curNode, linkedNode)
            e.set_style('dotted')
            context.graph.add_edge(e)
    
    return curNode

def isCompoToBeDrawn(component, context):
    """
        Returns true if the component has already been drawn or if it is going to be
    """
    ## In the list of selected compo?
    if context.components.filter(pk=component.pk).count() != 0: return True
    
    ## Already drawn?
    if __nodeExists(component, context): return True
    
    ## Out of the selected components, but at an acceptable level of recursion?
    if __getRecLevelDO(component, context) <= context.parentRecursionLevel: return True
    if __getRecLevelCT(component, context) <= context.patnersRecursionLevel: return True
    
    ## else return false
    return False

def __getRecLevelDO(component, context):
    if context.components.filter(pk=component.pk).count() == 1:
        return 0
    rec_level = 999
    for daddy in component.subscribers.all():
        i = __getRecLevelDO(daddy, context)
        if i < rec_level:
            rec_level = i
    return rec_level + 1

def __getRecLevelCT(component, context, prev = None):
    if context.components.filter(pk=component.pk).count() == 1:
        return 0
    rec_level = 999
    for daddy in component.connectedTo.all() | Component.objects.filter(connectedTo=component):
        if daddy == prev: continue
        i = __getRecLevelCT(daddy, context, component)
        if i < rec_level:
            rec_level = i
    return rec_level + 1

def __nodeExists(component, context):
    return not __getNode(component, context, False) == None

def __getNode(component, context, createIfAbsent = True):
    ## The node may already exist in the graph. Since all operations on it are done at creation, we can return it at once.
    n = context.graph.get_node(name=component.pk.__str__())  
    if n != None and type(n) == Node: ## get_node returns [] if not found.
        return n
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
        nbBrothers=1
        for parent in component.dependsOn.all():
            rs = parent.subscribers.filter(model=component.model, environments__in=component.environments.all() )
            nbBrothers += rs.count() - 1
            if rs.count() >= context.collapse_threshold:
                ## Change the node into a collapse artifact
                n.set_label('<%s instances de<br/>%s>' %(nbBrothers, unicodedata.normalize('NFKD', component.model.name).encode('ascii','ignore')))
                ## Mark brothers as collapsed
                for brother in rs:
                    context.collapsed_nodes[brother]=n
    
    ## End : return the node   
    return n       
    

def __createNode(component, context):
    ## Retrieve draw options
    options = getGraphOptions(component.leaf.__class__)
    
    ## Build node
    curNode = Node(component.pk)
    curNode.set_label(options['label'](component))
    curNode.set_shape(options['shape'])
    
    ## Node color (by environmnents)
    if component.environments.all().__len__() > 0:
        curNode.set_fillcolor(context.getEnvtColor(component.environments.all()[0].name))          
        curNode.set_style('filled')
    
    ## Return the node
    return curNode