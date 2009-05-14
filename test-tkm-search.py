#!/bin/python
# -*- coding: utf-8 -*-


## Setup django envt
from django.core.management import setup_environ
import settings
setup_environ(settings)
from django.db import models
#models.get_apps()
from django.db import transaction
from django.contrib.auth.models import User, Group, Permission


## Python imports
from datetime import date

## MAGE imports
from MAGE.tkm.models import * 


print u"recherche de sdf"
print Ticket.objects.search(u'sdf')

print u"\n\nrecherche de QUA1"
print Ticket.objects.search(Environment.objects.get(name='QUA1'))

print u"\n\nrecherche de sdf + QUA1"
print Ticket.objects.search(u'sdf', Environment.objects.get(name='QUA1'))

print u"\n\nrecherche de sdf + DEV1"
print Ticket.objects.search(u'sdf', Environment.objects.get(name='DEV1'))
