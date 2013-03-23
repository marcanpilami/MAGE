# coding: utf-8

from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from django import forms
from django.core.urlresolvers import reverse

from ref.csvi import get_components_csv
from ref.models import ComponentInstance, Environment
from ref.mcl import parser
from cpn.tests import utility_create_test_envt
from prm.models import getMyParams, getParam
from django.http.response import HttpResponseRedirect

def csv(request, url_end):
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


class MclTesterForm(forms.Form):
    mcl = forms.CharField(max_length=300, initial='()', label='Requête MCL', widget=forms.TextInput(
                 attrs={'size':'200', 'class':'inputText'}))   

def mcl_tester(request):
    base = request.build_absolute_uri('/')[:-1]
    if request.method == 'POST': # If the form has been submitted...
        form = MclTesterForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            res = parser.get_components(form.cleaned_data['mcl'])
            return render(request, 'ref/mcltester.html', {'mcl': form.cleaned_data['mcl'], 'form': form, 'results': res, 'base': base} ) 
    else:
        form = MclTesterForm() # An unbound form

    return render(request, 'ref/mcltester.html', {'form': form, 'base': base})


def mcl_request(request, titles, mcl, format = None):
    res = parser.get_components(mcl)
    if titles == '1':
        titles = True
    else:
        titles = False
        
    response = HttpResponse(content_type='text/csv')
    get_components_csv(res, titles, response)
    return response
    
    
def create_instance(request, instance_type, name):
    pass    