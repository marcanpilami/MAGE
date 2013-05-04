# coding: utf-8
from MAGE.exceptions import MageCallerError


class MageMclAttributeNameError(MageCallerError):
    pass

class MageMclSyntaxError(MageCallerError):
    pass