# coding: utf-8

from django.http import HttpResponse
from django.db import transaction
from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from django import forms
from django.core.urlresolvers import reverse
from django.db.models import Max
from django.db import connection


from ref.models import Environment, ComponentInstance, EnvironmentType, \
    LogicalComponent
from scm.tests import create_test_is, SimpleTest

from django.http.response import HttpResponseRedirect
from scm.models import ComponentInstanceConfiguration, InstallableSet, \
    InstallableItem, Installation, Delivery
from django.db.models.aggregates import Count
from cpn.tests import TestHelper
from scm.install import install_iset_envt
from datetime import datetime, timedelta

def envts(request):
    envts = Environment.objects.annotate(latest_reconfiguration=Max('component_instances__configurations__created_on')).\
        annotate(configuration_modification_count=Count('component_instances__configurations')).\
        order_by('typology')
    return render(request, 'scm/envts.html', {'envts': envts, })

def all_installs(request, envt_name, limit=15):
    envt = Environment.objects.get(name=envt_name)
    dlimit = datetime.now() - timedelta(days=limit)
    installs = Installation.objects.filter(install_date__gt=dlimit).filter(modified_components__component_instance__environments=envt).distinct().order_by('-pk')
    # logical_components = envt.component_instances.all().instanciates.implements;
    logical_components = LogicalComponent.objects.filter(implemented_by__instances__environments=envt)
    
    versions = {}
    for compo in envt.component_instances.filter(instanciates__isnull=False):
        lc = logical_components.get(id=compo.instanciates.implements_id)
        versions[lc] = compo.version
        
    return render(request, 'scm/envt_all_installs.html', {'installs': installs, 'envt':envt, 'logical_components':logical_components, 'versions': versions, 'limit': limit })

def delivery_list(request):
    deliveries = Delivery.objects.order_by('pk').select_related('set_content__what_is_installed__logical_component')
    return render(request, 'scm/all_deliveries.html', {'deliveries': deliveries})

@transaction.commit_on_success
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
    
