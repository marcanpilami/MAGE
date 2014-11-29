# coding: utf-8

from ref.models.parameters import getParam
from django.shortcuts import render
from django.http.response import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import PermissionDenied
from ref.models import ImplementationDescription, ImplementationRelationDescription, Environment
from ref.models.com import Link
from django.db.models.query import Prefetch
from django.db.models.aggregates import Max
from scm.models import ComponentInstanceConfiguration
from django.views.decorators.cache import cache_page
from django.core.cache.utils import make_template_fragment_key
from django.core.cache import cache


##############################################################################
## Home screen
##############################################################################

def welcome(request):
    latest = {}
    link_title = None
    ck = make_template_fragment_key('welcome_all')
    p = cache.get(ck)
    if p is None:
        link_title = getParam('LINKS_TITLE')
        envts = Environment.objects_active.annotate(latest_reconfiguration=Max('component_instances__configurations__id'))
        for e in envts:
            if e.latest_reconfiguration:
                latest[e.name] = ComponentInstanceConfiguration.objects.get(pk=e.latest_reconfiguration).result_of.belongs_to_set.name

    return render(request, 'ref/welcome.html', {'team_links_title': link_title, 'team_links': Link.objects.all(),
                            'latest': latest,
                            'envts': Environment.objects_active.order_by('typology', 'name').annotate(latest_reconfiguration=Max('component_instances__configurations__created_on')).\
                            annotate(latest_reconfiguration=Max('component_instances__configurations__created_on')).all(),
                            'templates': Environment.objects.filter(template_only=True) })


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

def script_login_post(request):
    if request.method == 'POST' and request.POST.has_key('username') and request.POST.has_key('password'):
        name = request.POST['username']
        passwd = request.POST['password']
        return script_login(request, name, passwd)
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
    ids = ImplementationDescription.objects.order_by('tag', 'name').prefetch_related(Prefetch('target_set', ImplementationRelationDescription.objects.order_by('name').select_related('target')),
                                                                                     'field_set',
                                                                                     'computed_field_set')

    #for idn in ids:


    #return render(request, 'ref/model_details.html', {'res' : sorted(ids.iteritems(), key=lambda (k, v) :  v['id']['name']) })
    return render(request, 'ref/model_details.html', {'res' : ids })


def shelllib_bash(request):
    return render(request, 'ref/helper_bash.sh', content_type='text/plain')
