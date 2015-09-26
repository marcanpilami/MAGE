# coding: utf-8
from django.contrib.auth.views import redirect_to_login

from django.shortcuts import render
from django.db.models.query import Prefetch
from django.db.models import Q
from django.db.models.aggregates import Count
from ref.models.acl import folder_permission_required
from ref.models.classifier import AdministrationUnit

from ref.models.instances import Environment, ComponentInstance, \
    ComponentInstanceField
from ref.models.description import ImplementationFieldDescription, \
    ImplementationComputedFieldDescription


def envt(request, envt_id):
    envt = Environment.objects.\
                    select_related('typology').select_related('project').\
                    get(pk=envt_id)

    if not request.user.has_perm('read_envt', envt):
        return redirect_to_login(request.path)

    deleted = []
    if request.user.is_authenticated() and request.user.has_perm('ref.change_component_instance'):
        deleted = ComponentInstance.objects.filter(environments__id=envt_id, deleted=True).\
                    select_related('description').\
                    order_by('description__name', 'id')

    sec = (False,)
    if not envt.protected or (request.user.is_authenticated() and request.user.has_perm('read_envt_sensible', envt)):
        sec = (True, False)

    cis = ComponentInstance.objects.filter(environments__id=envt_id, deleted=False).\
                    select_related('description').\
                    select_related('instanciates__implements__application').\
                    prefetch_related(Prefetch('field_set', queryset=ComponentInstanceField.objects.filter(field__widget_row__gte=0, field__sensitive__in=sec).order_by('field__widget_row', 'field__id'))).\
                    prefetch_related(Prefetch('description__field_set', queryset=ImplementationFieldDescription.objects.filter(widget_row__gte=0, sensitive__in=sec).order_by('widget_row', 'id'))).\
                    prefetch_related(Prefetch('description__computed_field_set', queryset=ImplementationComputedFieldDescription.objects.filter(widget_row__gte=0, sensitive__in=sec).order_by('widget_row', 'id'))).\
                    order_by('description__tag', 'description__name')

    return render(request, 'ref/envt.html', {'envt': envt, 'deleted': deleted, 'cis' : cis})

@folder_permission_required('read_envt')
def backuped(request, folder_id):
    folder = AdministrationUnit.objects.get(pk = folder_id)
    cis = ComponentInstance.objects.filter(include_in_envt_backup=True, deleted=False, environments__project__in = folder.scope()).\
            select_related('instanciates__implements__application').\
            select_related('description').\
            prefetch_related('environments')
    return render(request, 'ref/instance_backup.html', {'cis': cis, 'folder': folder})

@folder_permission_required('read_envt')
def shared_ci(request, folder_id, recursive = False):
    deleted = []
    sec = (False,)
    if request.user.is_authenticated() and request.user.has_perm('read_envt_sensible', folder_id):
        sec = (True, False)

    if recursive:
        folder = AdministrationUnit.objects.get(pk = folder_id)
        scope = [ s for s in folder.scope() if request.user.has_perm('read_envt', s.pk) ]
        cis = ComponentInstance.objects.annotate(num_envt=Count('environments')).filter(project_id__in = scope)
        sec = (False,) # cannot easily ensure ACL enforcement below the current folder, so no sensitive data allowed.

        if request.user.has_perm('change_envt', folder_id):
            deleted = ComponentInstance.objects.annotate(num_envt=Count('environments')).\
                    filter(project_id__in = scope, deleted=True).filter(Q(num_envt=0)).\
                    select_related('description').\
                    order_by('description__name', 'id')
    else:
        cis = ComponentInstance.objects.annotate(num_envt=Count('environments')).filter(project_id = folder_id)

        if request.user.has_perm('change_envt', folder_id):
            deleted = ComponentInstance.objects.annotate(num_envt=Count('environments')).\
                    filter(project_id = folder_id, deleted=True).filter(Q(num_envt=0)).\
                    select_related('description').\
                    order_by('description__name', 'id')

    cis = cis.filter(deleted=False).\
                    filter(Q(num_envt = 0)).\
                    select_related('description').\
                    prefetch_related(Prefetch('field_set', queryset=ComponentInstanceField.objects.filter(field__widget_row__gte=0, field__sensitive__in=sec).order_by('field__widget_row', 'field__id'))).\
                    prefetch_related(Prefetch('description__field_set', queryset=ImplementationFieldDescription.objects.filter(widget_row__gte=0, sensitive__in=sec).order_by('widget_row', 'id'))).\
                    prefetch_related(Prefetch('description__computed_field_set', queryset=ImplementationComputedFieldDescription.objects.filter(widget_row__gte=0, sensitive__in=sec).order_by('widget_row', 'id'))).\
                    order_by('description__tag', 'description__name')

    return render(request, 'ref/envt_shared.html', {'folder_id': folder_id, 'deleted': deleted, 'cis' : cis, 'recursive': recursive})
