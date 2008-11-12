#!/usr/bin/env python
# -*- coding: utf-8 -*-

## Setup django envt & django imports
from django.core.management import setup_environ
import settings
setup_environ(settings)

## MAGE imports
from MAGE.ref.helpers_light import *
from MAGE.ref.introspect import get_components_csv


print u'\n\n************Test 1 : une PK unique'
print get_components_csv([4])


print u'\n\n************Test 2 : deux PK'
print get_components_csv([4,3])


print u'\n\n************Test 3 : 2 chaînes de description'
print get_components_csv([['@TRUC','GESCO_DEV'], ['QM.GSC.DEV1']])


#print u'\n\n************Test 4 : 2 chaînes de description'

#print u'\n\n************Test 5 : mélange, 4 éléments'
