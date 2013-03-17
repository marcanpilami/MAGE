# coding: utf-8

from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from django import forms
from django.core.urlresolvers import reverse
from django.db.models import Max
from django.db import connection


from ref.models import Environment, ComponentInstance, EnvironmentType,\
    LogicalComponent
from scm.tests import create_test_is, SimpleTest

from django.http.response import HttpResponseRedirect
from scm.models import ComponentInstanceConfiguration, InstallableSet,\
    InstallableItem, Installation
from django.db.models.aggregates import Count
from cpn.tests import TestHelper
from scm.install import install_iset_envt

def envts(request):
    envts = Environment.objects.annotate(latest_reconfiguration=Max('component_instances__configurations__created_on')).\
        annotate(configuration_modification_count=Count('component_instances__configurations')).\
        order_by('typology')
    return render(request, 'scm/envts.html', {'envts': envts, })

def all_installs(request, envt_name):
    envt = Environment.objects.get(name=envt_name)
    installs = Installation.objects.filter(modified_components__component_instance__environments=envt)
    #logical_components = envt.component_instances
  
    return render(request, 'scm/envt_all_installs.html', {'installs': installs, 'envt':envt })

def demo(request):
    for IS in InstallableSet.objects.all():
        IS.delete()
    for ii in InstallableItem.objects.all():
        ii.delete()
    for envt in Environment.objects.all():
        envt.delete()
    for ci in ComponentInstance.objects.all():
        ci.delete()
    for et in EnvironmentType.objects.all():
        et.delete()
    for lc in LogicalComponent.objects.all():
        lc.delete()
    is_list = create_test_is()
    
    ref = TestHelper()
    install_iset_envt(is_list[0], ref.envt_prd1)
    install_iset_envt(is_list[1], ref.envt_prd1)
    
    return HttpResponseRedirect(reverse('welcome'))
    