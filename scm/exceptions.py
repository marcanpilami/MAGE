# coding: utf-8
'''
    @license: Apache License, Version 2.0
    @copyright: 2007-2013 Marc-Antoine Gouillart
    @author: Marc-Antoine Gouillart
'''

from MAGE.exceptions import MageCallerError, MageError, MageInternalError

class MageScmError(MageError):
    pass

class MageScmCallerError(MageCallerError):
    pass

class MageScmInternalError(MageInternalError):
    pass

class MageScmUndefinedVersionError(MageError):
    pass

class MageScmUnrelatedItemsError(MageError):
    pass

class MageScmFailedInstanceDependencyCheck(MageCallerError):
    def __init__(self, instance, dependency, error_text):
        self.instance = instance
        self.error = error_text
        self.dep = dependency
    
    def __str__(self):
        return '%s should be at version %s %s. Error is: %s' %(self.instance, self.dep.operator, self.dep.depends_on_version.version, self.error)
    
class MageScmFailedEnvironmentDependencyCheck(MageCallerError):
    def __init__(self, envt_name, ii, failing_dep_list):
        self.ii = ii;
        self.failing_dep = failing_dep_list
        self.envt_name = envt_name
    
    def __str__(self):
        if self.ii.__class__.__name__ == 'InstallableItem':
            name = self.ii.belongs_to_set.name
        else:
            name = self.ii.name
        res = '%s prerequisite(s) missing in order to install %s on environment %s' % (len(self.failing_dep), name, self.envt_name)
        for m in self.failing_dep:
            res = '' + res + "\n" + m.__str__()
        return res
    

class MageScmMissingComponent(MageCallerError):
    def __init__(self, ii, req_version, envt_name):
        self.ii = ii
        self.req_version = req_version
        self.envt_name = envt_name
    
    def __str__(self):
        return 'Missing component of type %s in environment %s (version %s)' % (self.ii, self.envt_name, self.req_version)
        
