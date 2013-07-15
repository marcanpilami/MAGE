# coding: utf-8
'''
    @license: Apache License, Version 2.0
    @copyright: 2007-2013 Marc-Antoine Gouillart
    @author: Marc-Antoine Gouillart
'''

from MAGE.exceptions import MageCallerError


class MageMclAttributeNameError(MageCallerError):
    pass

class MageMclSyntaxError(MageCallerError):
    pass