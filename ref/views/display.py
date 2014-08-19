# coding: utf-8

from django.shortcuts import render
from ref.models.models import Environment
from ref.models.parameters import getParam
from django.core.cache import cache

def envts(request):
    return render(request, 'ref/envts.html', {'envts': Environment.objects_active.filter(template_only=False).order_by('typology__chronological_order', 'typology__name'), 'colors': getParam('MODERN_COLORS').split(',')})

def templates(request):
    return render(request, 'ref/envts.html', {'envts': Environment.objects.filter(template_only=True).order_by('typology'), 'colors': getParam('MODERN_COLORS').split(',')})

def envt(request, envt_id):
    # we don't use the decorator in order to be able to invalidate cache manually
    a = cache.get('view_envt_%s' % envt_id)
    if a:
        return a

    envt = Environment.objects.\
                    select_related('typology').\
                    prefetch_related('component_instances__field_set__field').\
                    prefetch_related('component_instances__rel_target_set').\
                    prefetch_related('component_instances__implementation__computed_field_set').\
                    prefetch_related('component_instances__instanciates__implements__application').\
                    get(pk=envt_id)
    a = render(request, 'ref/envt.html', {'envt': envt, })
    cache.set('view_envt_%s' % envt_id, a , None)
    return a
