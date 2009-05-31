#coding: UTF-8

"""
    MAGE main page module
    
    @author: Marc-Antoine Gouillart
    @contact: marsu_pilami@msn.com
    @license: GNU GVL v3
"""

## Django imports
from django.db import models

## MAGE imports
from MAGE.ref.models import Component

## Base field for referencing detail templates
Component.detail_template = None    #TODO: is this still really usefull?
