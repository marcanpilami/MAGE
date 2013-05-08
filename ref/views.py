# coding: utf-8

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.contenttypes.models import ContentType
from django import forms

from MAGE.exceptions import MageCallerError
from ref.csvi import get_components_csv
from ref.creation import duplicate_envt, create_instance
from ref.models import ComponentInstance, Environment
from ref.mcl import parser
from prm.models import getMyParams, getParam

def csv(request, url_end):
    comps = ComponentInstance.objects.filter(pk__in=url_end.split(','))    
    return HttpResponse(get_components_csv(comps, displayRestricted=(request.user.is_authenticated() and request.user.has_perm('ref.allfields_componentinstance'))), mimetype="text/csv")

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
    allow_creation = forms.BooleanField(initial = False, required=False)

def mcl_tester(request):
    base = request.build_absolute_uri('/')[:-1]
    error = None
    if request.method == 'POST': # If the form has been submitted...
        form = MclTesterForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            try:
                res = parser.get_components(form.cleaned_data['mcl'], allow_create=form.cleaned_data['allow_creation'])
                return render(request, 'ref/mcltester.html', {'mcl': form.cleaned_data['mcl'], 'form': form, 'results': res, 'base': base})
            except MageCallerError, e:
                error = e.message 
    else:
        form = MclTesterForm() # An unbound form

    return render(request, 'ref/mcltester.html', {'form': form, 'base': base, 'error': error})


def mcl_query(request, mcl, titles = '1'):
    res = parser.get_components(mcl)
    if titles == '1':
        titles = True
    else:
        titles = False
        
    response = HttpResponse(content_type='text/csv')
    get_components_csv(res, titles, response, displayRestricted=(request.user.is_authenticated() and request.user.has_perm('ref.allfields_componentinstance')))
    return response
    
    
def mcl_create(request, mcl, use_convention = '1'):
    if use_convention == '1':
        use_convention = True
    else:
        use_convention = False
    res = create_instance(mcl, use_convention)
    
    response = HttpResponse(content_type='text/csv')
    get_components_csv(res, True, response, displayRestricted=(request.user.is_authenticated() and request.user.has_perm('ref.allfields_componentinstance')))
    return response

def mcl_create_without_convention(request, mcl):
    return mcl_create(request, mcl, '0')

def envt_duplicate(request, envt_name):
    e = duplicate_envt(envt_name, "new_name", {})
    
    return redirect('admin:ref_environment_change', e.id)
