# coding: utf-8

from django.shortcuts import render
from ref.models.instances import Environment, ComponentInstance
from ref.models.parameters import getParam


def envts(request):
    return render(request, 'ref/envts.html', {'envts': Environment.objects_active.filter(template_only=False).order_by('typology__chronological_order', 'typology__name'), 'colors': getParam('MODERN_COLORS').split(',')})

def templates(request):
    return render(request, 'ref/envts.html', {'envts': Environment.objects.filter(template_only=True).order_by('typology'), 'colors': getParam('MODERN_COLORS').split(',')})

def envt(request, envt_id):
    envt = Environment.objects.\
                    select_related('typology').\
                    get(pk=envt_id)    
    deleted = ComponentInstance.objects.filter(environments__id=envt_id, deleted=True).select_related('description').order_by('description__name', 'id')
    cis = ComponentInstance.objects.filter(environments__id=envt_id, deleted=False).\
                    select_related('description').\
                    prefetch_related('field_set').\
                    prefetch_related('rel_target_set').\
                    prefetch_related('description__computed_field_set').\
                    prefetch_related('description__field_set').\
                    select_related('instanciates__implements__application')   
    
    return render(request, 'ref/envt.html', {'envt': envt, 'deleted': deleted, 'cis' : cis})
