# coding: utf-8

from ref.models.parameters import getMyParams, getParam
from django.shortcuts import render
from django.http.response import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import PermissionDenied
from django.contrib.contenttypes.models import ContentType
from ref.models.models import ComponentInstance, ImplementationDescription, \
    ImplementationRelationDescription, Environment
from django.db.models.fields.related import ManyToManyField, ForeignKey
from ref.models.com import Link
from django.db.models.query import Prefetch


##############################################################################
## Home screen
##############################################################################

def welcome(request):
    link_title = getParam('LINKS_TITLE')
    return render(request, 'ref/welcome.html', {'team_links_title': link_title, 'team_links': Link.objects.all(), 'envts': Environment.objects.order_by('typology', 'name').all() })


##############################################################################
## Script helpers
##############################################################################

def script_login(request, username, password):
    user = authenticate(username=username, password=password)
    if user is not None and user.is_active:
        login(request, user)
        return HttpResponse("<html><body>User authenticated</body></html>")
    else:
        raise PermissionDenied # will return a 403 (HTTP forbidden)

def script_logout(request):
    logout(request)
    return HttpResponse("<html><body>User logged out</body></html>")



def urls(request):
    '''List of all URLs inside the web API'''
    return render(request, 'ref/urls.html')

def model_types(request):
    '''List of all installed component types'''
    return render(request, 'ref/model_types.html', {'models' : ImplementationDescription.objects.all()})


def model_detail(request):
    ids = ImplementationDescription.objects.order_by('tag', 'name').prefetch_related(Prefetch('target_set', ImplementationRelationDescription.objects.order_by('name').select_related('target')),
                                                                                     'field_set',
                                                                                     'computed_field_set')

    #for idn in ids:


    #return render(request, 'ref/model_details.html', {'res' : sorted(ids.iteritems(), key=lambda (k, v) :  v['id']['name']) })
    return render(request, 'ref/model_details.html', {'res' : ids })

