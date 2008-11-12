# coding: utf-8

## Python imports

## Django imports
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django import forms
from django.core.urlresolvers import reverse


## MAGE imports
#from MAGE.ref.models import Environment, Component
from MAGE.ref.introspect import get_components_csv
#from MAGE.ref.helpers_light import getComponent
    
def marsu(request, url_end):
    return HttpResponse(get_components_csv([i.split(',') for i in url_end.split('/')]), mimetype="text/csv")

