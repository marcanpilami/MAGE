# coding: utf-8

'''
Created on 17 mars 2013

@author: Marc-Antoine
'''

class MageError(Exception):
    pass

class MageInternalError(MageError):
    pass

class MageCallerError(MageError):
    pass