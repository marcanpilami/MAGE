# coding: utf-8

## Python imports
from datetime import timedelta

## Django imports
from django.utils.timezone import now
from django.shortcuts import render
from django.utils.datastructures import SortedDict
from django.db.models.query import Prefetch

## MAGE imports
from ref.models import Environment, LogicalComponent
from scm.models import Installation, ComponentInstanceConfiguration


def all_installs(request, envt_name, limit):
    '''All installs on a given environment'''
    if isinstance(limit, unicode):
        limit = int(limit)
    envt = Environment.objects.get(name=envt_name)
    envt.potential_tag = now().strftime('%Y%M%d') + "_" + envt_name
    dlimit = now() - timedelta(days=limit)
    
    installs = Installation.objects.filter(install_date__gt=dlimit).filter(modified_components__component_instance__environments=envt).distinct().order_by('-pk').\
            prefetch_related(Prefetch('modified_components', queryset=ComponentInstanceConfiguration.objects.all().select_related('component_instance__instanciates')))
    logical_components = LogicalComponent.objects.filter(scm_trackable=True, active=True, implemented_by__instances__environments=envt).distinct()\
                            .select_related('application')

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
    Installation.objects.filter()
    envts = Environment.objects_active.filter(managed=True).order_by('typology__chronological_order', 'name')
    res = SortedDict()
    for lc in LogicalComponent.objects.filter(scm_trackable=True, active=True).select_related('application').order_by('application__name', 'name') :
        lc_list = []
        for envt in envts:
            compo_instances = envt.component_instances.filter(instanciates__implements__id=lc.id)
            versions = [i.latest_cic for i in compo_instances if i.version_object_safe]
            if len(versions) > 0:
                versions.sort(key=lambda x : x.created_on, reverse=True)
                lc_list.append(versions[0].result_of.what_is_installed)
            else:
                lc_list.append(None)
        res[lc] = lc_list

    return render(request, 'scm/lc_installs_envt.html', {'res': res, 'envts': envts})
