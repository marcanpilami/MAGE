# coding: utf-8

## Python imports
from datetime import timedelta

## Django imports
from django.utils.timezone import now
from django.shortcuts import render
from django.utils.datastructures import SortedDict
from django.db.models.query import Prefetch
from django.db.models import Max

## MAGE imports
from ref.models import Environment, LogicalComponent
from scm.models import Installation, ComponentInstanceConfiguration, \
    ComponentInstance


def all_installs(request, envt_name, limit):
    '''All installs on a given environment'''
    if isinstance(limit, unicode):
        limit = int(limit)
    envt = Environment.objects.get(name=envt_name)
    envt.potential_tag = now().strftime('%Y%M%d') + "_" + envt_name
    dlimit = now() - timedelta(days=limit)
    
    installs = Installation.objects.filter(install_date__gt=dlimit).filter(modified_components__component_instance__environments=envt).distinct().\
            order_by('-pk').\
            select_related('installed_set').\
            prefetch_related(Prefetch('modified_components', 
                    queryset=ComponentInstanceConfiguration.objects.all().select_related('component_instance__instanciates', 'result_of__what_is_installed')))
    logical_components = LogicalComponent.objects.filter(scm_trackable=True, active=True, implemented_by__instances__environments=envt).distinct()\
                            .order_by('application__name', 'name').select_related('application')

    versions = {}
    for compo in envt.component_instances.filter(deleted=False, instanciates__isnull=False, instanciates__implements__scm_trackable=True):
        try:
            lc = logical_components.get(id=compo.instanciates.implements_id)
        except LogicalComponent.DoesNotExist:
            continue
        if versions.has_key(lc):
            versions[lc] += (compo.version,)
        else:
            versions[lc] = (compo.version,)

    return render(request, 'scm/envt_all_installs.html', {'installs': installs, 'envt':envt, 'logical_components':logical_components, 'versions': versions, 'limit': limit })


def lc_versions_per_environment(request):
    envts = Environment.objects_active.filter(managed=True, active=True).order_by('typology__chronological_order', 'name')
    
    cics = ComponentInstance.objects.annotate(latest_change_id=Max('configurations__id'))\
            .filter(latest_change_id__isnull=False).values_list('latest_change_id', flat=True)   
    cics = ComponentInstanceConfiguration.objects.filter(pk__in=cics, component_instance__instanciates__implements__isnull=False)\
            .filter(component_instance__deleted=False)\
            .filter(component_instance__instanciates__active=True)\
            .filter(component_instance__instanciates__implements__active=True)\
            .select_related('component_instance__instanciates__implements__application', 'result_of__what_is_installed')\
            .prefetch_related('component_instance__environments')
    
    res = {}
    for cic in cics:
        if not res.has_key(cic.component_instance.instanciates.implements):
            res[cic.component_instance.instanciates.implements] = SortedDict()
            for e in envts:
                res[cic.component_instance.instanciates.implements][e] = []
        
        for e in cic.component_instance.environments.all():
            # only add different versions
            try:
                if not cic.result_of.what_is_installed in res[cic.component_instance.instanciates.implements][e]:
                    res[cic.component_instance.instanciates.implements][e].append(cic.result_of.what_is_installed)
            except KeyError:
                pass  # happens for unmanaged, deleted... envts & the like            
    
    return render(request, 'scm/lc_installs_envt.html', {'res': SortedDict(sorted( res.items(), key = lambda t : t[0].application_id)), 'envts': envts})
    
