#!/bin/python
# -*- coding: utf-8 -*-

"""
    Test file for the TKM + auth application
    Uses objects from populate.py
    It is an independant script, called without any arguments.

    @author: mag
"""

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


@transaction.commit_manually
def createStupidUsers():
    ## Create users
    u1 = User.objects.create_user('b', 'b@b.com', 'b')
    u2 = User.objects.create_user('c', 'b@b.com', 'c')
    u3 = User.objects.create_user('d', 'b@b.com', 'd')
    u1.save(); u2.save(); u3.save()
 
    ## Create groups
    g1 = Group(name = u'Développeurs')
    g2 = Group(name = u'Testeurs')
    g3 = Group(name = u'Chefs')
    g1.save(), g2.save(); g3.save()

    ## Assign groups
    u1.groups.add(g1)
    u2.groups.add(g2)
    u3.groups.add(g2)
    # g3 is empty as we don't like bosses
    
    ## Create or get permissions
    p1 = Permission.objects.get(codename='add_ticket')
    p2 = Permission.objects.get(codename='change_ticket')
    
    ## Assign permissions
    g2.permissions.add(p1)      ## Testers can create tickets
    g1.permissions.add(p2)      ## Devs can update a ticket
    
    transaction.commit()

    
createStupidUsers()
