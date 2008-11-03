# coding: utf-8

class GCLException(Exception):
    def __str__(self):
        return 'Exception module de GCL'

class InverseOrder(GCLException):
    def __str__(self):
        return 'Les CTV sont inverses. On ne peut downgrader un composant via une installation !'

class SameCTV(GCLException):
    def __str__(self):
        return 'On ne peut aller d\'une version vers la meme version'

class InconsistantIS(GCLException):
    def __init__(self, i_s):
        self.inst_set = i_s
    def __str__(self):
        return 'L\'IS %s est incoherent (plusieurs version differentes pour un même composant)' %(self.inst_set)


class UnrelatedCTV(Exception):
    def __init__(self, ctv1, ctv2):
        self.ctv1 = ctv1
        self.ctv2 = ctv2
    def __str__(self):
        return 'Les CTV % et %s n\'ont pas d\'ordre pariculier' %(self.ctv1, self.ctv2)

class MissingFieldException(Exception):
    """@todo: Finish this"""
    def __init__(self, comp):
        self.comp = comp
    def __str__(self):
        return u'Version non definie pour le composant %s' %(self.comp)

class FailedDependenciesCheckException(Exception):
    def __init__(self, comp, ctv):
        self.comp = comp
        self.ctv = ctv
    def __str__(self):
        return 'Incompatibilite : %s est en version %s, il faudrait %s' %(self.comp, self.comp.version, self.ctv.version)

class MissingComponentException(Exception):
    def __init__(self, installation_set, ctv, envt):
        self.ist = installation_set
        self.ctv = ctv
        self.envt = envt
    def __str__(self):
        return 'Incompatibilite : l\'installation de %s requiert un composant type %s non present dans l\'environnement %s.' \
                %(self.ist, self.ctv.class_name, self.envt)


class InconsistentComponentsException(Exception):
    def __init__(self, comp, envt):
        self.comp = comp
        self.envt = envt
    def __str__(self):
        return 'Incompatibilite : %s n\'appartient pas a %s' %(self.comp, self.envt)

class NotAFullIS(Exception):
    def __init__(self, IS):
        self.IS = IS
    def __str__(self):
        return 'Incompatibilite : %s est incrementiel, et ne peut faire d\'installations initiales de composants.' %(self.IS)
    
class InadequateIS(Exception):
    def __init__(self, comp, IS):
        self.comp = comp
        self.IS = IS
    def __str__(self):
        return 'Incompatibilite : le composant %s n\'est pas concerne par %s' %(self.comp, self.IS)



class UndefinedVersion(Exception):
    def __init__(self, comp):
        self.comp = comp
    def __str__(self):
        return 'Version non definie pour le composant %s' %(self.comp)

class ComponentCannotBeUpgraded(Exception):
    def __init__(self, comp):
        self.comp = comp
    def __str__(self):
        return u'Le composant %s de type %s ne peut etre mis à jour' %(self.comp.name, self.comp.type)