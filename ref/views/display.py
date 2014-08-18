# coding: utf-8

from django.shortcuts import render
from ref.models.models import Environment
from ref.models.parameters import getParam

def envts(request):
    return render(request, 'ref/envts.html', {'envts': Environment.objects_active.filter(template_only=False).order_by('typology__chronological_order', 'typology__name'), 'colors': getParam('MODERN_COLORS').split(',')})

def templates(request):
    return render(request, 'ref/envts.html', {'envts': Environment.objects.filter(template_only=True).order_by('typology'), 'colors': getParam('MODERN_COLORS').split(',')})

def envt(request, envt_id):
    envt = Environment.objects.select_related('field_set__field').select_related('rel_target_set').select_related('implementation__computed_field_set').get(pk=envt_id)
    return render(request, 'ref/envt.html', {'envt': envt, })
