# coding: utf-8

class MissingFieldException(Exception):
    """@todo: Finish this"""
    def __init__(self, comp):
        self.comp = comp
    def __str__(self):
        return 'Version non definie pour le composant %s' %(self.comp)

class FailedDependenciesCheckException(Exception):
    def __init__(self, comp, ctv):
        self.comp = comp
        self.ctv = ctv
    def __str__(self):
        return 'Incompatibilté : %s est en version %s, il faudrait %s' %(self.comp, self.comp.version, self.ctv.version)

class InconsistentComponentsException(Exception):
    def __init__(self, comp, envt):
        self.comp = comp
        self.envt = envt
    def __str__(self):
        return 'Incompatibilté : %s n\'appartient pas � %s' %(self.comp, self.envt)

class NotAFullIS(Exception):
    def __init__(self, IS):
        self.IS = IS
    def __str__(self):
        return 'Incompatibilté : %s est incrémentiel, et ne peut faire d\'installations initiales de composants.' %(self.IS)
    
class InadequateIS(Exception):
    def __init__(self, comp, IS):
        self.comp = comp
        self.IS = IS
    def __str__(self):
        return 'Incompatibilté : le composant %s n\'est pas concerné par %s' %(self.comp, self.IS)



class UndefinedVersion(Exception):
    def __init__(self, comp):
        self.comp = comp
    def __str__(self):
        return 'Version non definie pour le composant %s' %(self.comp)

class ComponentCannotBeUpgraded(Exception):
    def __init__(self, comp):
        self.comp = comp
    def __str__(self):
        return u'Le composant %s de type %s ne peut être mis à jour' %(self.comp.name, self.comp.type)