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


#############################################################
## Simplified notation tests
#############################################################

print u"\n01 (['P2','rec2evt','GCDEV','XGCT1']) - liste de str"
res = getMCL(['P2','rec2evt','GCDEV','XGCT1'])
print res
print type(res)
print type(res.leaf)

print u"\n02 (\"P2,rec2evt,GCDEV,XGCT1\") - chaîne de caractères"
res = getMCL("P2,rec2evt,GCDEV,XGCT1")
print res
print type(res)
print type(res.leaf)

print u"\n03 (\"P2,rec2evt,GCDEV,XGCT1|OraclePackage\") - chaine de caractères avec model"
res = getMCL("P2,rec2evt,GCDEV,XGCT1|OrAclePackAge")
print res
print type(res)
print type(res.leaf)

print u"\n04 (\"P2,rec2evt,GCDEV,XGCT1|DEV2|OraclePackage\") - chaine de caractères avec model et environnement"
res = getMCL("P2,rec2evt,GCDEV,XGCT1|DEV2|OraclePackage")
print res
print type(res)
print type(res.leaf)


#############################################################
## Exceptions
#############################################################

print u"\nTEST GET2 3 (P2 sur rec2evt sur GCTRT : Unknown compo)"
try: print getMCL(['P2','rec2evt','GCTRT','XGCT1'])
except UnknownComponent,e: print "Exception OK : " + e.__str__()

print u"\nTEST GET2 4 (P2 : TooManyCompos)"
try: print getMCL(['P2',])
except TooManyComponents,e: print "Exception OK : " + e.__str__()


#############################################################
## Simplified notation tests
#############################################################

print u"\n02.01"
try: res = getMCL("oracleschema=Schema Gold Events, instance_oracle=GCDEV, base_server=XGCT1")
except TooManyComponents,e: print "Exception OK : " + e.__str__()

print u"\n02.02"
res = getMCL("oracleschema=dev1evt, instance_oracle=GCDEV, base_server=XGCT1")
print res
print type(res)

print u"\n02.03"
try: 
    res = getMCL("'oracleschema=dev1evt', 'instance_oracle'='GCDEV', 'base_server=XGCT2'")
    raise Exception ('test échoué')
except UnknownComponent,e: print "Exception OK : " + e.__str__()


print u"\n02.04 - getMCL([('oracleschema','dev1evt'), ('instance_oracle', 'GCDEV'), ('base_server', 'XGCT1')])"
res = getMCL([('oracleschema','dev1evt'), ('instance_oracle', 'GCDEV'), ('base_server', 'XGCT1')])
print res
print type(res)




## test createASimpleComponent(compo_type, compo_descr, envt_name = None):
#print u"\n\nTEST CREATE 1"
#findOrCreateComponent('oraclepackage', l)
#
#print u"\nTEST CREATE 2"
#findOrCreateComponent('oraclepackage', ['name=PCK_MARSU', 'schema=Schema Gold Central', 'instance=GCDEV', 'server=MACHIN'])
