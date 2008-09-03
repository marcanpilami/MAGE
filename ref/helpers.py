# -*- coding: utf-8 -*-

## Django imports
from django.db.models.loading import get_apps, get_model

## MAGE imports
from MAGE.ref.models import *

#TODO: add a __ navigation option in the getCompo functions

class UnknownModel(Exception):
    def __init__(self, model_name):
        self.model_name=model_name
    def __str__(self):
        return u'Le type de composant %s est introuvable' %(self.model_name)

class UnknownComponent(Exception):
    def __init__(self, compo_name):
        self.compo_name=compo_name
    def __str__(self):
        return u'Le composant %s est introuvable' %(self.compo_name)

class TooManyComponents(Exception):
    def __init__(self, compo_descr):
        self.compo_name=compo_name
    def __str__(self):
        return u'Plusieurs composants répondent à la description donnée' %(self.compo_descr)

class UnknownParent(Exception):
    def __init__(self, parent_name, model_name):
        self.parent_name=parent_name
        self.model_name=model_name
    def __str__(self):
        return u'Les composants de type %s n\'ont pas de parent de nom %s' %(self.model_name, self.parent_name)

class TooComplexToBuild(Exception):
    def __init__(self, compo_name, model_name):
        self.compo_name=compo_name
        self.model_name=model_name
    def __str__(self):
        return u'Impossible de construire automatiquement le composant %s de type %s \
(composant ayant plusieurs champs ou plusieurs parents)' %(self.compo_name, self.model_name)

class MissingConnectedToComponent(Exception):
    def __init__(self,parents, compo_type):
        self.parents = parents
        self.compo_type=compo_type 
    def __str__(self):
        return u'Il est nécéssaire de préciser les parents suivants pour un composant \
de type %s : %s' %(self.compo_type, self.parents) 
        
def getComponent(compo_type, compo_descr, envt_name = None):
    """Finds a component given its name and type, and optionaly its parents' names 
    @param compo_descr: an ordered list [name=value, parent_field_name=value, grandparent_field_name=value, ...]
    @param compo_type: as a string, lowercase
    @param envt_name: the environment name
    @return: the component instance if found. (raises an exception if not)
    
    @raise UnknownModel: if compo_type cannot be resolved
    @raise UnknownComponent: if no component can be found with the given component description
    @raise TooManyComponents: if multiple components are returned using the given component description
    @raise UnknownParent: if a specified parent field doesn't exist""" 
    if envt_name == None:
        print u'Recherche d\'un composant %s sans envt.' %(compo_descr)
    else:
        print u'Recherche d\'un composant %s dans l\'envt : %s.' %(compo_descr, envt_name) 
    ## Parse arguments
    familly_names=[couple.split('=') for couple in compo_descr]
    
    ## Get the model (raises UnknownModel exception)
    model = getModel(compo_type)

    ## First selection : environment, type and compo name
    #print u'type__model=%s, name=%s' %(compo_type.lower(), familly_names[0][1])
    rs = Composant.objects.filter(type__model=compo_type.lower(), name=familly_names[0][1])
    #print rs.count()
    if envt_name != None:
        rs = rs.filter(environments__name=envt_name)
    if rs.count() == 0:
        raise UnknownComponent(compo_descr)
    if rs.count == 1:
        return rs.all()[0]

    ## Refine the selection with parents' names
    i = 1
    while i < len(compo_descr) and rs.count() > 1:
        field = familly_names[i][0]
        value = familly_names[i][1]
        parents = model.parents
        
        ## Check parent field exists
        try:
            parentModel = parents[field] # string
        except:
            raise UnknownParent(field, model.__name__)
        
        ## Django query construction
        d = {}
        papa = ""
        for p in range(0,i):
            papa = papa + "dependsOn__"
        #d[papa + 'type'] = MageModelType.objects.get(model=parentModel.lower()) # Django bug (#8046) ??? name alone should be enough
        d[papa +'name'] = value
        
        ## Query
        rs = rs.filter(**d)
        
        ## Iteration
        i=i+1
        model = getModel(model.parents[field])
 
    ## We are at the end of our knowledge, we have failed if the compo is still unfound
    if rs.count() > 1:
        raise TooManyComponents(compo_descr)
    
    ## Return the one and only component
    return rs.all()[0]


def findOrCreateComponent(compo_type, compo_descr, envt_name = None):
    try:
        return getComponent(compo_type, compo_descr, envt_name)
    except UnknownComponent:
        return __createASimpleComponent(compo_type, compo_descr, envt_name)



def __createASimpleComponent(compo_type, compo_descr, envt_name = None):
    """Creates a new component. 
        Only for components without fields (but the base Composant fields) and 0 to 1 parents.
        
        @param compo_descr: an ordered list [name=value, parent_field_name=value, grandparent_field_name=value, ...]
        @param compo_type: as a string, lowercase
        @param envt_name: the environment name
        @return: the new component instance, raises an exception if an error occurs
    """
    print u'Création d\'un composant : %s' %compo_descr
    #####################################
    ## New compo itself
    familly_names=[couple.split('=') for couple in compo_descr]
    model = getModel(compo_type)
    
    ## Create a new model instance
    a = model(name=familly_names[0][1])
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
    
    ## Get or create parent component (without envt - wevcould be looking for a server, or anything not envt related)
    try:
        papa = findOrCreateComponent(parents[familly_names[1][0]], compo_descr[1:]) 
    except:
        a.delete()
        raise
    
    a.dependsOn = [papa]
    a.save()
    
    ## Return the new component
    return a


def getModel(model_name):
    """Helper function to find a model by its name (case insensitive)"""
    for app in [tmp.__name__.split('.')[-2] for tmp in get_apps()]:
        res=get_model(app, model_name)
        if res != None:
            return res
    raise UnknownModel(model_name)