# coding: utf-8

from django.shortcuts import render
from ref.models.instances import Environment
from ref.models.parameters import getParam


def envts(request):
    return render(request, 'ref/envts.html', {'envts': Environment.objects_active.filter(template_only=False).order_by('typology__chronological_order', 'typology__name'), 'colors': getParam('MODERN_COLORS').split(',')})

def templates(request):
    return render(request, 'ref/envts.html', {'envts': Environment.objects.filter(template_only=True).order_by('typology'), 'colors': getParam('MODERN_COLORS').split(',')})

def envt(request, envt_id):
    envt = Environment.objects.\
                    select_related('typology').\
                    prefetch_related('component_instances__field_set__field').\
                    prefetch_related('component_instances__rel_target_set').\
                    prefetch_related('component_instances__description__computed_field_set').\
                    prefetch_related('component_instances__instanciates__implements__application').\
                    get(pk=envt_id)
    return render(request, 'ref/envt.html', {'envt': envt, })
