# coding: utf-8

## Python imports
import csv

## Django imports
from django.shortcuts import render
from django.http.response import HttpResponse

## MAGE imports
from scm.models import InstallableSet


def iset_content_shell(request, isetid):
    iset = InstallableSet.objects.get(pk=int(isetid))
    return render(request, 'scm/shell_ii_detail_ksh.html', {'is': iset}, content_type="text/text")

def iset_id(request, iset_name):
    res = 0
    try:
        iset = InstallableSet.objects.get(name=iset_name)
        res = iset.id
    except InstallableSet.DoesNotExist:
        res = 0

    response = HttpResponse(content_type='text/text')
    response.write(res)
    return response


def iset_content_csv(request, iset):
    if isinstance(iset, unicode):
        try:
            i = int(iset)
            iset = InstallableSet.objects.get(pk=i)
        except:
            iset = InstallableSet.objects.get(name=iset)

    response = HttpResponse(content_type='text/csv')
    wr = csv.DictWriter(response, fieldnames=('id', 'target', 'target_id', 'version', 'is_full', 'data_loss'), restval="", extrasaction='ignore', dialect='excel', delimiter=";")
    wr.writeheader()

    for ii in iset.set_content.all():
        wr.writerow({'id': ii.id, 'target': ii.what_is_installed.logical_component.name, 'target_id': ii.what_is_installed.logical_component.id, 'version': ii.what_is_installed.version, 'is_full': ii.is_full, 'data_loss': ii.data_loss})

    return response
