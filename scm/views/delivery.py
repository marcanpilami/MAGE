# coding: utf-8

## Django imports
from django.views.decorators.cache import cache_control
from django.shortcuts import render

## MAGE imports
from ref.models import LogicalComponent, Environment
from scm.models import Delivery, InstallableSet, InstallableItem, LogicalComponentVersion
from django.db.models.query import Prefetch
from django.db.models.aggregates import Max


@cache_control(must_revalidate=True, max_age=600)
def delivery_list(request, project):
    deliveries = Delivery.objects.filter(set_content__what_is_installed__logical_component__application__project__name=project).order_by('-set_date').prefetch_related(Prefetch(
        'set_content', InstallableItem.objects.select_related('what_is_installed__logical_component').prefetch_related('how_to_install'))
    )[:40]
    lis = LogicalComponent.objects.filter(scm_trackable=True, active=True, application__project__name=project).order_by('application__name', 'name').prefetch_related('versions', 'application')
    return render(request, 'scm/all_deliveries.html', {'deliveries': deliveries, 'lis': lis, 'project': project})

@cache_control(no_cache=True)
def delivery(request, project, iset_id):
    delivery = InstallableSet.objects.filter(pk=iset_id).prefetch_related(Prefetch('set_content',
        queryset=InstallableItem.objects.select_related('what_is_installed__logical_component__application')))[0]    
    m = Environment.objects.filter(active=True, managed=True).filter(component_instances__configurations__result_of__belongs_to_set_id=iset_id, project__name=project).annotate(dd=Max('component_instances__configurations__created_on'))
    return render(request, 'scm/delivery_detail.html', {'installs': m, 'delivery': delivery, 'envts': Environment.objects_active.filter(managed=True, project__name=project).order_by('typology__chronological_order', 'name'),
                                                        'project': project})
