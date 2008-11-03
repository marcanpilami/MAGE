#!/bin/python
# -*- coding: utf-8 -*-

## Setup django envt
from django.core.management import setup_environ
import settings
setup_environ(settings)
from django.db import transaction
from django.db import models
models.get_apps()

## Python imports
from datetime import date

## MAGE imports
from MAGE.sav.models import *

save_full_environment('DEV1')
