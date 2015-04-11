# coding: utf-8

from django.shortcuts import render
from django.db.models.query import Prefetch

from ref.models.instances import Environment, ComponentInstance, \
    ComponentInstanceField
from ref.models.description import ImplementationFieldDescription, \
    ImplementationComputedFieldDescription


def envt(request, envt_id):
    envt = Environment.objects.\
                    select_related('typology').\
                    get(pk=envt_id)   
    
    deleted = []
    if request.user.is_authenticated() and request.user.has_perm('ref.change_component_instance'):
        deleted = ComponentInstance.objects.filter(environments__id=envt_id, deleted=True).\
                    select_related('description').\
                    order_by('description__name', 'id')
    
    sec = (False,)
    if not envt.protected or (request.user.is_authenticated() and request.user.has_perm('ref.allfields_componentinstance')):
        sec = (True, False)
        
    cis = ComponentInstance.objects.filter(environments__id=envt_id, deleted=False).\
                    select_related('description').\
                    select_related('instanciates__implements__application').\
                    prefetch_related(Prefetch('field_set', queryset=ComponentInstanceField.objects.filter(field__widget_row__gte=0, field__sensitive__in=sec).order_by('field__widget_row'))).\
                    prefetch_related(Prefetch('description__field_set', queryset=ImplementationFieldDescription.objects.filter(widget_row__gte=0, sensitive__in=sec).order_by('widget_row'))).\
                    prefetch_related(Prefetch('description__computed_field_set', queryset=ImplementationComputedFieldDescription.objects.filter(widget_row__gte=0, sensitive__in=sec).order_by('widget_row'))).\
                    order_by('description__tag', 'description__name')

    return render(request, 'ref/envt.html', {'envt': envt, 'deleted': deleted, 'cis' : cis})

def backuped(request):
    cis = ComponentInstance.objects.filter(include_in_envt_backup=True, deleted=False).\
            select_related('instanciates__implements__application').\
            select_related('description').\
            prefetch_related('environments')
    return render(request, 'ref/instance_backup.html', {'cis': cis})
