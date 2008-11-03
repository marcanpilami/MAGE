#!/usr/bin/env python
# -*- coding: utf-8 -*-

## Setup django envt & django imports
from django.core.management import setup_environ
import settings
setup_environ(settings)

## MAGE imports
from MAGE.ref.helpers import *
from MAGE.gcl.helpers import *
from MAGE.gcl.models import *

#e = Environment.objects.get(name='ENVT1')
#l=['name=P1','schema=Schema Gold Events','instance=GCDEV','server=MACHIN']
#
### test getCompo : should work
#print u"TEST GET 1"
#compo = getComponent('oraclepackage', l, 'ENVT1')
#print compo
#
#print u"\nTEST GET 2"
#print getComponent('oracleschema', ['name=Schema Gold Events', 'instance=GCDEV', 'server=MACHIN'])
#
### test createASimpleComponent(compo_type, compo_descr, envt_name = None):
#print u"\n\nTEST CREATE 1"
#findOrCreateComponent('oraclepackage', l)
#
#print u"\nTEST CREATE 2"
#findOrCreateComponent('oraclepackage', ['name=PCK_MARSU', 'schema=Schema Gold Central', 'instance=GCDEV', 'server=MACHIN'])
