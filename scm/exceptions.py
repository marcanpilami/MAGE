'''
Created on 17 mars 2013

@author: Marc-Antoine
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