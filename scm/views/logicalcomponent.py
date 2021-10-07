# coding: utf-8
""" Logical component model """

## Python imports
import json

## Django imports
from django.views.decorators.cache import cache_control
from django.shortcuts import render
from django.http.response import HttpResponse
from MAGE.decorators import project_permission_required

## MAGE imports
from ref.models import LogicalComponent
from django.db.models.query import Prefetch
from scm.models import LogicalComponentVersion, InstallableSet, InstallableItem


def get_lc_versions(request, lc_id):
    lc = LogicalComponent.objects.get(pk=lc_id)
    res = []
    for v in lc.versions.all().order_by('pk'):
        res.append((v.id, v.version))

    return HttpResponse(json.dumps(res))

@project_permission_required
def lc_list(request, project):
    lcs = LogicalComponent.objects.filter(active=True, scm_trackable=True, application__project__name=project).order_by('application', 'name').select_related('application')
    return render(request, 'scm/lc_versions.html', {'lcs': lcs, 'project': project})

@cache_control(must_revalidate=True)
def lc_versions(request, lc_id):
    lc = LogicalComponent.objects.select_related('application').prefetch_related(
               Prefetch('versions', queryset=LogicalComponentVersion.objects.prefetch_related(Prefetch('installed_by', queryset=InstallableItem.objects.all().select_related('belongs_to_set__backupset'))))
           ).get(pk=lc_id)
    return render(request, 'scm/lc_versions_detail.html', {'lc': lc})



