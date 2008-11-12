# coding: utf-8

## Python imports

## Django imports
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django import forms
from django.core.urlresolvers import reverse


## MAGE imports
from MAGE.gcl.models import Installation, Tag, ComponentTypeVersion, Component
from MAGE.liv.models import Delivery 
from MAGE.ref.models import Environment
from MAGE.gcl.helpers import goToTagThroughDeliveries

def installs_list_envt(request, envt_name):
    install_list = Installation.objects.filter(target_envt__name = envt_name).order_by('install_date')
    return render_to_response('install_list.html', {'install_list' : install_list, 'envt_name': envt_name})


def tag_list(request):
    """Liste des niveaux applicatifs de référence"""
    tag_list = Tag.objects.order_by('snapshot_date')
    return render_to_response('tags_list.html', {'tag_list' : tag_list })

def installs_comp(request, compoID):
    install_list = Installation.objects.filter(target_components__pk = compoID).order_by('install_date')
    compo = Component.objects.get(pk=compoID)
    return render_to_response('component_installs.html', {'install_list' : install_list, 'compo': compo})

def delivery_list(request):
    """Liste des livraisons disponibles"""
    dl = Delivery.objects.all()
    return render_to_response('del_list.html', {'del_list' : dl, })

def version_list(request):
    """Liste classée des différentes versions de composant d'environnement connues du système.
    En l'état, c'est surtout un test de la relation d'ordre des versions."""
    list1 = [i for i in ComponentTypeVersion.objects.all()]#filter(class_name='@TRUC')]
    list1.sort(cmp=ComponentTypeVersion.compare)
    list2 = [i for i in ComponentTypeVersion.objects.all()]#filter(class_name='@TRUC')]
    list2.sort(cmp=ComponentTypeVersion.compare, reverse=True)
    
    return render_to_response('ctv_list.html', {'list1': list1, 'list2':list2})

class GoToTagForm(forms.Form):
    envt_to_update = forms.ChoiceField(
            choices = [(e.pk, e.__unicode__()) for e in Environment.objects.all()], 
            widget = forms.widgets.Select,                    
            label = u'Environnement à amener au niveau de référence :')
    tag_to_use = forms.ChoiceField(
            choices = [(e.pk, e.__unicode__()) for e in Tag.objects.all()], 
            widget = forms.widgets.Select,                    
            label = u'Niveau applicatif de référence :')

def go_to_tag_is_list(request, envt_id = None, tag_id = None):
    """Déterminer la liste des livraisons à installer pour atteindre un niveau applicatif de référence"""
    if request.method == 'POST':                    # If the form has been submitted...
        form = GoToTagForm(request.POST)            # A form bound to the POST data
        if form.is_valid():                         # All validation rules pass
            # Process the data in form.cleaned_data            
            envt = Environment.objects.get(pk = form.cleaned_data['envt_to_update'])
            tag = Tag.objects.get(pk = form.cleaned_data['tag_to_use'])
            
            is_list = goToTagThroughDeliveries(envt, tag)
            request.method = "GET"
            return HttpResponseRedirect(reverse('MAGE.gcl.views.go_to_tag_is_list', args = [str(envt.pk),str(tag.pk)])) # Redirect after POST
    else:
        if not envt_id or not tag_id:
            form = GoToTagForm()                    # An unbound, new form
            is_list = None
        else:
            envt = Environment.objects.get(pk = envt_id)
            tag = Tag.objects.get(pk = tag_id)
            is_list = goToTagThroughDeliveries(envt, tag)
            form = GoToTagForm()                    # An unbound, new form
            form.envt_to_update = envt_id
            form.tag_to_use = tag_id

    return render_to_response('go_to_tag.html', {'form': form, 'is_list':is_list})