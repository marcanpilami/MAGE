# coding: utf-8

## Python imports
import json

## Django imports
from django.views.decorators.cache import cache_control
from django.shortcuts import render
from django.http.response import HttpResponse

## MAGE imports
from ref.models.models import LogicalComponent


def get_lc_versions(request, lc_id):
    lc = LogicalComponent.objects.get(pk=lc_id)
    res = []
    for v in lc.versions.all().order_by('pk'):
        res.append((v.id, v.version))

    return HttpResponse(json.dumps(res))

def lc_list(request):
    lcs = LogicalComponent.objects.filter(active=True, scm_trackable=True).order_by('application', 'name')
    return render(request, 'scm/lc_versions.html', {'lcs': lcs})

@cache_control(must_revalidate=True)
def lc_versions(request, lc_id):
    lc = LogicalComponent.objects.get(pk=lc_id)
    return render(request, 'scm/lc_versions_detail.html', {'lc': lc})



