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


## test getCompo : should work
print u"TEST GET 1"
compo = getComponent('oraclepackage', ['name=P1',], 'DEV1')
print compo

print u"\nTEST GET 2"
print getComponent('oracleschema', ['name=Schema Gold Events', 'instance_oracle=GCDEV', 'base_server=XGCT1'], 'DEV1')

print u"\nTEST GET 3"
print getComponent('oraclepackage', ['name=P2', 'parent_schema=dev1evt', 'instance_oracle=GCDEV', 'base_server=XGCT1'])


## test createASimpleComponent(compo_type, compo_descr, envt_name = None):
#print u"\n\nTEST CREATE 1"
#findOrCreateComponent('oraclepackage', l)
#
#print u"\nTEST CREATE 2"
#findOrCreateComponent('oraclepackage', ['name=PCK_MARSU', 'schema=Schema Gold Central', 'instance=GCDEV', 'server=MACHIN'])
