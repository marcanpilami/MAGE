
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType

from ref.csvi import get_components_csv
from ref.models import ComponentInstance, Environment
from ora.tests import utility_create_test_envt
from prm.models import getMyParams, getParam

def csv(request, url_end):
    utility_create_test_envt(1)
    comps = ComponentInstance.objects.filter(pk__in=url_end.split(','))
    return HttpResponse(get_components_csv(comps), mimetype="text/csv")

def welcome(request):
    links = [ i for i in getMyParams() if i.axis1 == 'Technical team links']
    
    colors = getParam('LINK_COLORS').split(',')
    i = -1
    for link in links:
        if i < len(colors) - 1:
            i = i + 1
        else:
            i = 0
        link.color = colors[i]
        
        url = getParam(link.key + '_URL')
        link.url = url
         
    return render(request, 'ref/welcome.html', {'team_links': links, })


def envts(request):
    return render(request, 'ref/envts.html', {'envts': Environment.objects.all().order_by('typology'), 'colors': getParam('MODERN_COLORS').split(',')})

def envt(request, envt_id):
    envt = Environment.objects.get(pk=envt_id)
    return render(request, 'ref/envt.html', {'envt': envt, })

def model_types(request):
    return render(request, 'ref/model_types.html', {'models' :  [i for i in ContentType.objects.all() if issubclass(i.model_class(), ComponentInstance) and i.app_label != 'ref']})
