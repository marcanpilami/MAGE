# coding: utf-8

## Python imports

## Django imports
from django.shortcuts import render, redirect
from django.http.response import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.db.models.query import Prefetch
from django.db.models.aggregates import Max
from django.core.cache.utils import make_template_fragment_key
from django.core.cache import cache
from django.contrib.auth.decorators import permission_required, login_required, user_passes_test

## MAGE imports
from ref.models import ComponentInstance, ImplementationDescription, ImplementationRelationDescription, Environment, Link, Project
from ref.models.parameters import getParam
from ref.permissions.perm_check import permission_required_project_aware, login_required_unless_anonymous_mode
from ref.permissions.perm_check import anonymous_mode
from scm.models import ComponentInstanceConfiguration


##############################################################################
## Home screen
##############################################################################

@permission_required_project_aware('ref.view_project', no_check_in_anonymous_mode=True)
def project(request):
    """Home page for a specific project (not the MAGE home)"""
    latest_setname = {}
    latest_date = {}
    envts = []
    link_title = None
    ck = make_template_fragment_key('project', [request.project.pk])
    p = cache.get(ck)
    if p is None:
        link_title = getParam('LINKS_TITLE')
        envts = Environment.objects_active.filter(project__pk=request.project.pk).annotate(latest_reconfiguration=Max('component_instances__configurations__id')).order_by('name')
        for e in envts:
            if e.latest_reconfiguration:
                cic = ComponentInstanceConfiguration.objects.select_related('result_of__belongs_to_set').get(pk=e.latest_reconfiguration)
                latest_setname[e.name] = cic.result_of.belongs_to_set.name
                latest_date[e.name] = cic.created_on

    return render(request, 'ref/project.html', {    'team_links_title': link_title,
                                                    'team_links': Link.objects.all(),
                                                    'latest_setname': latest_setname,
                                                    'latest_date': latest_date,
                                                    'envts': envts,
                                                    'templates': Environment.objects.filter(template_only=True) })

@login_required_unless_anonymous_mode
def welcome(request):
    """MAGE home - basically a project list. Redirects if only one project available"""
    projects = Project.objects.all()

    if not anonymous_mode:
        projects = [ project for project in projects if request.user.has_perm(f'ref.view_project_{project.id}')]

    if len(projects) == 1:
        return redirect('ref:project', project_id=projects[0].pk)

    return render(request, 'ref/welcome.html', { 'templates': projects })


##############################################################################
## Script helpers
##############################################################################

def script_login(request, username, password):
    user = authenticate(username=username, password=password)
    if user is not None and user.is_active:
        login(request, user)
        return HttpResponse("<html><body>User authenticated</body></html>")
    else:
        raise PermissionDenied  # will return a 403 (HTTP forbidden)

def script_login_post(request):
    if request.method == 'POST' and 'username' in request.POST and 'password' in request.POST:
        name = request.POST['username']
        passwd = request.POST['password']
        return script_login(request, name, passwd)
    raise PermissionDenied  # will return a 403 (HTTP forbidden)

def script_logout(request):
    logout(request)
    return HttpResponse("<html><body>User logged out</body></html>")

@login_required
def force_login(request):
    try:
        next = request.GET.get('next')
    except:
        next = '/'
    return redirect(next)


def urls(request):
    '''List of all URLs inside the web API'''
    return render(request, 'ref/urls.html')

def model_types(request):
    '''List of all installed component types'''
    return render(request, 'ref/model_types.html', {'models' : ImplementationDescription.objects.filter(Q(cic_set__implements__application__project=request.project) | Q(cic_set__implements__isnull = True)).distinct()})


def model_detail(request):
    ids = ImplementationDescription.objects.filter(Q(cic_set__implements__application__project=request.project) | Q(cic_set__implements__isnull = True)) \
        .order_by('tag', 'name').distinct() \
        .prefetch_related(Prefetch('target_set', ImplementationRelationDescription.objects.order_by('name').select_related('target')),'field_set', 'computed_field_set')

    #for idn in ids:


    #return render(request, 'ref/model_details.html', {'res' : sorted(ids.iteritems(), key=lambda (k, v) :  v['id']['name']) })
    return render(request, 'ref/model_details.html', {'res' : ids})


def shelllib_bash(request):
    return render(request, 'ref/helper_bash.sh', content_type='text/plain')

@user_passes_test(lambda u: u.is_superuser)
def debug(request):
    return render(request, 'ref/debug.html', {'envts': Environment.objects.all(), 'descrs' : ImplementationDescription.objects.all().order_by('tag', 'name')})

@user_passes_test(lambda u: u.is_superuser)
def control(request):
    descrs = ImplementationDescription.objects.all().prefetch_related(
          Prefetch('instance_set', queryset=ComponentInstance.objects.all().prefetch_related('rel_target_set', 'field_set', 'environments').select_related('instanciates')), \
           'target_set', 'field_set')
    
    many_envts = []
    missing_field = {}
    missing_rel = {}
    
    for d in descrs:
        for i in d.instance_set.all():
            
            ## Check simple fields
            for f in d.field_set.all():
                if not f.compulsory:
                    continue
                
                found = False
                for inf in i.field_set.all():
                    if inf.field_id == f.id and inf.value:
                        found = True
                        break
                if not found:
                    if i in missing_field:
                        missing_field[i].append(f)
                    else:
                        missing_field[i] = [f, ]
            
            ## Check relationships
            for f in d.target_set.all():
                if f.min_cardinality == 0:
                    continue
                
                found = False
                for inf in i.rel_target_set.all():
                    if inf.field_id == f.id:
                        found = True
                        break
                if not found:
                    if i in missing_rel:
                        missing_rel[i].append(f)
                    else:
                        missing_rel[i] = [f, ]
                        
            ## Check envts
            if i.environments.count() > 1:
                many_envts.append(i)
            
    return render(request, 'ref/control.html', {'many_envts': many_envts, 'missing_field': missing_field, 'missing_rel': missing_rel})

@user_passes_test(lambda u: u.is_superuser)
def clear_cache(request):
    try:
        cache.clear()
    except NotImplementedError:
        pass
    return HttpResponse('')
