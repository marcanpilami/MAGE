# coding: utf-8
""" Logical component model """

## Python imports
import json

## Django imports
from django.views.decorators.cache import cache_control
from django.shortcuts import render
from django.http.response import HttpResponse

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

def lc_list(request):
    lcs = LogicalComponent.objects.filter(active=True, scm_trackable=True).order_by('application', 'name').select_related('application')
    return render(request, 'scm/lc_versions.html', {'lcs': lcs})

@cache_control(must_revalidate=True)
def lc_versions(request, lc_id):
    lc = LogicalComponent.objects.select_related('application').prefetch_related(
               Prefetch('versions', queryset=LogicalComponentVersion.objects.prefetch_related(Prefetch('installed_by', queryset=InstallableItem.objects.select_related('belongs_to_set'))))
           ).get(pk=lc_id)
    return render(request, 'scm/lc_versions_detail.html', {'lc': lc})



