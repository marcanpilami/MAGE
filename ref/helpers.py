# -*- coding: utf-8 -*-

""" 
    This file contains helpers for accessing the referential in scripts or other
    Django applications :
        - Find a component with a hierachical description
        - Create a (simple) component
        - Retrieve a model class or a model ContentType
        - List all component models
    
    @author: Marc-Antoine Gouillart
    @contact: marsu_pilami@msn.com
    @license: GNU GVL v3
"""

## Django imports
from django.contrib.contenttypes.models import ContentType

## MAGE imports
from MAGE.ref.models import *
from MAGE.ref.exceptions import *


def filterSimplifiedMCL(ucl, envt = None, compo_type = None):
    ## Compo type ?
    if compo_type:
        model=getModel(compo_type)
    else:
        model=Component
    
    if type(envt) == Environment: envt_name = envt.name
    else: envt_name = envt
    
    ## First selection through name
    if envt_name:
        res = model.objects.filter(instance_name = ucl[0], environments__name=envt_name) | model.objects.filter(class_name = ucl[0], environments__name=envt_name)
    else:
        res = model.objects.filter(instance_name = ucl[0]) | model.objects.filter(class_name = ucl[0])
    compos = [ (i,i) for i in res.all() ]
    
    ## Selection refinment through parents
    for name in ucl[1:]:
        tmp = []
        for compo in compos:
            tmp += [ (compo[0],i) for i in (compo[1].dependsOn.filter(instance_name = name) | compo[1].dependsOn.filter(class_name = name)).all() ]
        compos = []
        for i in tmp:
            if i not in compos:
                compos.append(i) 
    
    ## Return the list
    return [ i[0] for i in compos ]

def getSimplifiedMCL(mcl, envt_name = None, compo_type = None):
    res = filterSimplifiedMCL(mcl, envt_name, compo_type)
    if res.__len__() > 1:
        raise TooManyComponents(mcl)
    if res.__len__() == 0:
        raise UnknownComponent(mcl)
    return res[0]
    

def getMCL(mcl, envt = None, compo_type = None):
    res = filterMCL(mcl, envt, compo_type)
    if res.__len__() > 1:
        raise TooManyComponents(mcl)
    if res.__len__() == 0:
        raise UnknownComponent(mcl)
    return res[0]
    
def filterMCL(mcl, envt = None, compo_type = None):
    """
        MCL do-it-all function
    """    
    #####################################################
    ## Simplified MCL string
    #####################################################
    if (type(mcl) == str or type(mcl) == unicode) and mcl.find('=') == -1:
        model = None
        envt_name = None
        
        j = mcl.split('|')
        names = j[0]
        if j.__len__() >= 2:
            firstfield=j[1]
        else:
            firstfield = None
        if j.__len__() == 3:
            model=j[2]
        
        # Firstfield may be an environment
        if firstfield:
            try:    
                envt_name = Environment.objects.get(name=firstfield).name
            except:
                ## It is not. It should be a model name or a model.
                model = firstfield 
        
        return filterSimplifiedMCL(names.split(','), envt_name, model)
   
   
    #####################################################
    ## Complete MCL string
    #####################################################
    if (type(mcl) == str or type(mcl) == unicode) and mcl.find('=') != -1:
        envt_name = None
        j=mcl.split('|')
        duets = j[0].split(',')
        
        if j.__len__() == 2:
            envt_name = j[1]
        
        return filterCompleteMCL(duets, envt_name)
    
    
    #####################################################
    ## Complete MCL array
    #####################################################
    if type(mcl) == list and type(mcl[0]) == tuple:
        return filterCompleteMCL(mcl, envt)
    
    
    #####################################################
    ## Simplified MCL array
    #####################################################
    if type(mcl) == list and type(mcl[0]) == str:
        return filterSimplifiedMCL(mcl, envt, compo_type)
    
    raise SyntaxError('parametres incorrects')



def filterCompleteMCL(mcl, envt = None):   
    ## Parse arguments
    if type(mcl[0]) == str:
        familly_names = [(couple.split('=')[0].strip("'\" "), couple.split('=')[1].strip("'\" ")) for couple in mcl]
    else:
        familly_names = mcl
    
    ## Get the model (raises UnknownModel exception)
    model = getModel(familly_names[0][0])
    
    ## get envt
    if type(envt) == Environment: envt_name = envt.name
    else: envt_name = envt
    
    ## First selection : environment, type and compo name
    rs = model.objects.filter(class_name=familly_names[0][1]) | \
                model.objects.filter(instance_name=familly_names[0][1])
    
    if envt_name:
        rs = rs.filter(environments__name=envt_name)
    if rs.count() == 0:
        raise UnknownComponent(familly_names)
    
    ## Refine the selection with parents' names
    res = [ (i,i) for i in rs.all() ]
    for duet in familly_names[1:]:
        field = duet[0]
        value = duet[1]
        parents = model.parents
        try:
            parent_model = getModel(model.parents[field])
        except KeyError:
            raise UnknownParent(compo_type, field)
        
        tmp=[]
        for compo in res:
            tmp += [ (compo[0],i) for i in (compo[1].dependsOn.filter(instance_name = value, model__model=model.parents[field].lower()) | 
                                            compo[1].dependsOn.filter(class_name = value, model__model=model.parents[field].lower())).all() ]
        res = [ i for i in tmp if i not in res ]
            
        ## Iteration
        model = parent_model
        
    return [ i[0] for i in res ]


def getCompleteMCL(mcl, envt = None):
    res = filterCompleteMCL(mcl, envt)
    if res.__len__() > 1:
        raise TooManyComponents(mcl)
    if res.__len__() == 0:
        raise UnknownComponent(mcl)
    return res[0]


def findOrCreateComponent(compo_type, compo_descr, envt_name = None):
    try:
        return getComponent(compo_type, compo_descr, envt_name)
    except UnknownComponent:
        return __createASimpleComponent(compo_type, compo_descr, envt_name)



def __createASimpleComponent(compo_type, compo_descr, envt_name = None):
    """Creates a new component. 
        Only for components without fields (but the base Component fields) and 0 to 1 parents.
        Will NOT recursively create the parents of the component
        
        @param compo_descr: an ordered list [name=value, parent_field_name=value, grandparent_field_name=value, ...]
        @param compo_type: as a string, lowercase
        @param envt_name: the environment name
        @return: the new component instance, raises an exception if an error occurs
    """
    #print u'Création d\'un composant : %s' %compo_descr
    #####################################
    ## New compo itself
    familly_names=[couple.split('=') for couple in compo_descr]
    model = getModel(compo_type)
    
    ## Create a new model instance
    a = model(class_name=familly_names[0][1])
    try:
        a.save()
    except :
        raise TooComplexToBuild(familly_names[0][1], compo_type)
    
    ## Add to environment
    if envt_name != None:
        a.environments=[Environment.objects.get(name=envt_name)]
        a.save()
    
    #####################################
    ## Parents
    ## Link to parents, as stated in the "parents" dictionnary inside the model class itself. 
    parents = model.parents
    
    ## If no parents needed => finish
    if parents == None or parents.__len__() == 0:
        return a
    
    ## If multiple parents : impossible to build (the compo_descr list contains a single line of parents, no forks)
    if parents.__len__() > 1:
        a.delete()
        raise TooComplexToBuild(familly_names[0][1], compo_type)
    
    ## If required parents are absent => error
    if parents.__len__() != 0 and compo_descr.__len__() == 1:
        a.delete()
        raise MissingConnectedToComponent(parents, compo_type)
    
    ## Get (don't create !) parent component (without envt - we could be looking for a server, or anything not envt related)
    try:
        papa = getComponent(parents[familly_names[1][0]], compo_descr[1:]) 
    except UnknownComponent:
        a.delete()
        raise TooComplexToBuild(familly_names[0][1], compo_type)
    
    a.dependsOn = [papa]
    a.save()
    
    ## Return the new component
    return a

def getModelDescriptor(model_name):
    """Helper function to find a model ContentType object by its name (case insensitive)"""
    try:
        return ContentType.objects.get(model=model_name.lower())
    except ContentType.DoesNotExist:
        raise UnknownModel(model_name)

def getModel(model_name):
    """Helper function to find a model by its name (case insensitive)"""
    return getModelDescriptor(model_name).model_class()



#########################################################
## ContentType filtering functions
#########################################################

def list_component_models():
    """Returns a list of all instanciable component models present in MAGE"""
    res = []
    for model in ContentType.objects.all():
        if issubclass(model.model_class(), Component) and model.model_class() != Component:
            res += [model]
    return res 

def component_models_generator():
    """Generator of all instanciable component models present in MAGE"""
    for model in ContentType.objects.all():
        if issubclass(model.model_class(), Component) and model.model_class() != Component:
            yield model
