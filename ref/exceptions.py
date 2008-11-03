# -*- coding: utf-8 -*-


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
        self.compo_name=compo_descr
    def __str__(self):
        return u'Plusieurs composants répondent à la description donnée %s' %(self.compo_descr)

class UnknownParent(Exception):
    def __init__(self, parent_name, model_name):
        self.parent_name=parent_name
        self.model_name=model_name
    def __str__(self):
        return u'Les composants de type %s n\'ont pas de parent nomme "%s"' %(self.model_name, self.parent_name)

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
        return u'Il est necessaire de preciser les parents suivants pour un composant \
de type %s : %s' %(self.compo_type, self.parents) 