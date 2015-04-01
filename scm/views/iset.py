# coding: utf-8

## Python imports
import csv
import json

## Django imports
from django.shortcuts import render
from django.http.response import HttpResponse, HttpResponseNotFound

## MAGE imports
from scm.models import InstallableSet, InstallableItem
from django.forms.models import model_to_dict


def iset_export(request, iset, output_format='json'):
    try:
        iset = InstallableSet.objects.get(name=iset)
    except InstallableSet.DoesNotExist:
        try:
            iset = InstallableSet.objects.get(pk=iset)
        except InstallableSet.DoesNotExist:
            return HttpResponseNotFound('there is no installable set by this name or ID')

    if output_format == 'csv':
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="iset.csv"'
        res = model_to_dict(iset, exclude='datafile')
        wr = csv.DictWriter(response, fieldnames=res.keys(), restval="", extrasaction='ignore', dialect='excel', delimiter=";")
        wr.writeheader()
        wr.writerow(res)
        return response

    if output_format in ('csvc', 'sh', 'bash4'):
        res = []
        for ii in iset.set_content.all():
            a = __ii_to_dict(ii)
            res.append(a)
    else:
        res = model_to_dict(iset, exclude='datafile')
        res['set_content'] = []
        for ii in iset.set_content.all():
            iid = model_to_dict(ii, exclude=('datafile', 'belongs_to_set'))
            iid['how_to_install'] = [ {'name': m.name, 'id': m.pk, 'target_offers': [{'id': lll.id, 'name': lll.name} for lll in m.method_compatible_with.all()]} for m in ii.how_to_install.all()]
            lcv = ii.what_is_installed
            iid['what_is_installed'] = {'id': lcv.pk, 'version': lcv.version, 'target_logical_component_id': lcv.logical_component.id, 'target_logical_component_name': lcv.logical_component.name}
            res['set_content'].append(iid)

    if output_format == 'csvc':
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="iset.csv"'
        wr = csv.DictWriter(response, fieldnames=res[0].keys(), restval="", extrasaction='ignore', dialect='excel', delimiter=";")
        wr.writeheader()
        wr.writerows(res)
        return response

    elif output_format == 'sh':
        return render(request, 'scm/iset_export_sh.html', {'res': res}, content_type="text/plain")

    elif output_format == 'json':
        response = HttpResponse(content_type='text/json; charset=utf-8')
        json.dump(res, fp=response, ensure_ascii=False, indent=4)
        return response

def __ii_to_dict(ii):
    a = {}
    a['is_full'] = ii.is_full
    a['target_offers_names'] = ",".join([",".join([ml.name for ml in m.method_compatible_with.all()]) for m in ii.how_to_install.all() ])
    a['target_offers_ids'] = ",".join([",".join([str(ml.id) for ml in m.method_compatible_with.all()]) for m in ii.how_to_install.all() ])
    a['how_to_install_ids'] = ",".join([str(m.id) for m in ii.how_to_install.all() ])
    a['how_to_install_names'] = ",".join([str(m.name) for m in ii.how_to_install.all() ])
    a['version'] = ii.what_is_installed.version
    a['cic_id'] = ii.what_is_installed.id
    a['target_logical_component_name'] = ii.what_is_installed.logical_component.name
    a['target_logical_component_id'] = ii.what_is_installed.logical_component_id
    a['target_application'] = ii.what_is_installed.logical_component.application.name
    a['ii_id'] = ii.pk
    a['data_loss'] = ii.data_loss
    a['url'] = ii.datafile.url
    return a

def iset_id(request, iset_name):
    res = 0
    try:
        iset = InstallableSet.objects.get(name=iset_name)
        res = iset.id
    except InstallableSet.DoesNotExist:
        return HttpResponseNotFound('there is no installable set with this ID', content_type='text/plain')

    response = HttpResponse(content_type='text/plain')
    response.write(res)
    return response

def ii_export(request, ii_id, output_format='sh'):
    ii = InstallableItem.objects.get(pk=ii_id)
    di = __ii_to_dict(ii)
    return render(request, 'scm/iset_export_sh.html', {'res': [di, ], 'iset': ii.belongs_to_set}, content_type="text/plain;charset=utf-8")

