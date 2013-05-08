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
from django.db.models.fields.related import ManyToManyField, ForeignKey

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

def model_detail(request):
    res = {}
    for ct in [i for i in ContentType.objects.all() if issubclass(i.model_class(), ComponentInstance) and i.app_label != 'ref']:
        model = ct.model_class()
        res[model] = {}
        d = res[model]
        
        d['id'] = {'name': model.__name__, 'code':ct.model, 'verbose_name': model._meta.verbose_name}
    
        d['fields'] = []
        
        for fi in model._meta.fields:
            if fi.attname in ('instanciates_id', 'deleted', 'include_in_envt_backup', 'model_id', 'componentinstance_ptr_id'):
                continue
            
            f = {'code': fi.attname, 'verbose_name':fi.verbose_name, 'default':fi.default if fi.has_default() else None, 'null': fi.null, 'unique': fi.unique}
            
            if f.has_key('rel') and f.rel:
                f['target'] = f.related.model
            
            if isinstance(fi, ForeignKey) or isinstance(fi, ManyToManyField):
                f['mcl_compat'] = 'no'
            elif fi.model == ComponentInstance:
                f['mcl_compat'] = 'base'
            else:
                f['mcl_compat'] = 'cast'
                
            d['fields'].append(f)
                
        for fi, descr in model.parents.items():
            f = {'code': fi, 'target': descr.get('model'), 'verbose_name': 'depends on', 'default': None, 'card': descr.get('cardinality') or 1, 'mcl_compat': 'rel'}
            d['fields'].append(f)
            
    return render(request, 'ref/model_details.html', {'res' : sorted(  res.iteritems(), key= lambda (k, v) :  v['id']['name']) })


class MclTesterForm(forms.Form):
    mcl = forms.CharField(max_length=300, initial='()', label='Requête MCL', widget=forms.TextInput(
                 attrs={'size':'200', 'class':'inputText'}))   
    allow_creation = forms.BooleanField(initial=False, required=False)

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


def mcl_query(request, mcl, titles='1'):
    res = parser.get_components(mcl)
    if titles == '1':
        titles = True
    else:
        titles = False
        
    response = HttpResponse(content_type='text/csv')
    get_components_csv(res, titles, response, displayRestricted=(request.user.is_authenticated() and request.user.has_perm('ref.allfields_componentinstance')))
    return response
    
    
def mcl_create(request, mcl, use_convention='1'):
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
