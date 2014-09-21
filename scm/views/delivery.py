# coding: utf-8

## Django imports
from django.views.decorators.cache import cache_control
from django.shortcuts import render

## MAGE imports
from ref.models import LogicalComponent, Environment
from scm.models import Delivery, InstallableSet


@cache_control(must_revalidate=True, max_age=600)
def delivery_list(request):
    deliveries = Delivery.objects.order_by('set_date').reverse().select_related('set_content__what_is_installed__logical_component')
    lis = LogicalComponent.objects.filter(scm_trackable=True, active=True).order_by('pk').select_related('versions')
    return render(request, 'scm/all_deliveries.html', {'deliveries': deliveries, 'lis': lis})

@cache_control(no_cache=True)
def delivery(request, iset_id):
    delivery = InstallableSet.objects.get(pk=iset_id)
    return render(request, 'scm/delivery_detail.html', {'delivery': delivery, 'envts': Environment.objects_active.filter(managed=True).order_by('typology__chronological_order', 'name')})

