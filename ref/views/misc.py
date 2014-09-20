# coding: utf-8

from ref.models.parameters import getMyParams, getParam
from django.shortcuts import render
from django.http.response import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import PermissionDenied
from django.contrib.contenttypes.models import ContentType
from ref.models.models import ComponentInstance, ImplementationDescription
from django.db.models.fields.related import ManyToManyField, ForeignKey
from ref.models.com import Link


##############################################################################
## Home screen
##############################################################################

def welcome(request):
    link_title = getParam('LINKS_TITLE')
    return render(request, 'ref/welcome.html', {'team_links_title': link_title, 'team_links': Link.objects.all(), })


##############################################################################
## Script helpers
##############################################################################

def script_login(request, username, password):
    user = authenticate(username=username, password=password)
    if user is not None and user.is_active:
        login(request, user)
        return HttpResponse("<html><body>User authenticated</body></html>")
    else:
        raise PermissionDenied # will return a 403 (HTTP forbidden)

def script_logout(request):
    logout(request)
    return HttpResponse("<html><body>User logged out</body></html>")



def urls(request):
    '''List of all URLs inside the web API'''
    return render(request, 'ref/urls.html')

def model_types(request):
    '''List of all installed component types'''
    return render(request, 'ref/model_types.html', {'models' : ImplementationDescription.objects.all()})


def model_detail(request):
    '''Does not work any more'''
    res = {}
    for ct in [i for i in ContentType.objects.all() if issubclass(i.model_class(), ComponentInstance) and i.app_label != 'ref']:
        model = ct.model_class()
        res[model] = {}
        d = res[model]

        d['id'] = {'name': model.__name__, 'code':ct.model, 'verbose_name': model._meta.verbose_name}

        d['fields'] = []

        for fi in model._meta.fields:
            if fi.attname in ('instanciates_id', 'deleted', 'include_in_envt_backup', 'model_id', 'componentinstance_ptr_id'):
                continue

            f = {'code': fi.attname, 'verbose_name':fi.verbose_name, 'default':fi.default if fi.has_default() else None, 'null': fi.null, 'unique': fi.unique}

            if f.has_key('rel') and f.rel:
                f['target'] = f.related.model

            if isinstance(fi, ForeignKey) or isinstance(fi, ManyToManyField):
                f['mcl_compat'] = 'no'
            elif fi.model == ComponentInstance:
                f['mcl_compat'] = 'base'
            else:
                f['mcl_compat'] = 'cast'

            d['fields'].append(f)

        for fi, descr in model.parents.items():
            f = {'code': fi, 'target': descr.get('model'), 'verbose_name': 'depends on', 'default': None, 'card': descr.get('cardinality') or 1, 'mcl_compat': 'rel'}
            d['fields'].append(f)

    return render(request, 'ref/model_details.html', {'res' : sorted(res.iteritems(), key=lambda (k, v) :  v['id']['name']) })

