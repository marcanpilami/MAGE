# coding: utf-8

"""
    Graph module view file. This is the core of the module.
    
    @license: Apache License, Version 2.0
    @copyright: 2007-2013 Marc-Antoine Gouillart
    @author: Marc-Antoine Gouillart
"""

# Python imports
import unicodedata

# Django imports
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django import forms
from django.core.urlresolvers import reverse
from django.db.models import Q

# MAGE imports
from graphs_mlg import getGraph, DrawingContext
from ref.models import Environment, Application, ImplementationDescription
from cpn.tests import utility_create_test_envt

def full_pic(request):
    """Carte de l'ensemble des composants référencés"""
    #cfilter = {'environments__template_only':False}
    uFilter = (Q(environments__isnull=True) | Q(environments__template_only=False),)
    return HttpResponse(getGraph(django_filter_unnamed=uFilter), content_type="image/png")

def demo_pic(request):
    """Carte de l'ensemble de composants test"""
    if Application.objects.count() == 0:
        utility_create_test_envt(1)
    return HttpResponse(getGraph(), content_type="image/png")


def filter_pic(request, nbRelGenerations, collapseThr): 
    dico = request.GET
    cfilter = {}

    # Extract model filter from the url
    for fi in dico.keys():
        cfilter[unicodedata.normalize('NFKD', fi).encode('ascii', 'ignore')] = [int(i) for i in dico[fi].split(',')]
    
    # Init the drawing context
    dc = DrawingContext()
    dc.connection_level = int(nbRelGenerations)
    dc.collapse_threshold = int(collapseThr)
    
    # Return the picture
    return HttpResponse(getGraph(cfilter, context=dc), content_type="image/png")


def envt_pic(request, envt_id):
    # Create png with GraphWiz  
    dc = DrawingContext()
    dc.parentRecursionLevel = 1
    dc.patnersRecursionLevel = 5
    dc.collapse_threshold = 5
    cfilter = {'environments__pk':envt_id}
    
    # Return the picture
    return HttpResponse(getGraph(cfilter, context=dc), mimetype="image/png")

class CartoForm(forms.Form):
    envts = forms.MultipleChoiceField(
                    choices=[(e.pk, e.name) for e in Environment.objects.all().order_by('typology__chronological_order', 'name')],
                    widget=forms.widgets.CheckboxSelectMultiple,
                    initial=[] if Environment.objects.filter(template_only=False).count() == 0 else [Environment.objects.filter(template_only=False).order_by('typology__chronological_order', 'name')[0].pk],
                    label=u'Environnements à afficher')
    
    models = forms.MultipleChoiceField(
                    choices=[(m.pk, m.name) for m in ImplementationDescription.objects.all()],
                    widget=forms.widgets.CheckboxSelectMultiple,
                    initial=[m.pk for m in ImplementationDescription.objects.all()],
                    label=u'Composants à afficher')
    
    relRecursion = forms.IntegerField(
                    label=u'Générations de relations à afficher ',
                    max_value=3,
                    min_value=0,
                    initial=1)
            
    collapseThr = forms.IntegerField(
                    label=u'Réunir éléments similaires à partir de ',
                    max_value=20,
                    min_value=0,
                    initial=4)
    
    

def view_carto(request):
    """Marsupilamographe"""
    if request.method == 'POST':  # If the form has been submitted...
        form = CartoForm(request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            # Process the data in form.cleaned_data
            cfilter = {}
            cfilter['environments__pk__in'] = form.cleaned_data['envts']
            ad = reverse('gph:filter',
                         args=(str(form.cleaned_data['relRecursion']),
                               str(form.cleaned_data['collapseThr']))) + '?environments__pk__in=' 
            for env in form.cleaned_data['envts']: ad += env + ','
            ad = ad[:-1] + ';implementation__pk__in='
            for pk in form.cleaned_data['models']: ad += pk + ","
            ad = ad[:-1]
            
            return render_to_response('gph/view_carto.html', {'resultlink': ad, 'machin':'truc', 'form': form, })
    else:
        form = CartoForm()  # An unbound form

    return render_to_response('gph/view_carto.html', {'form': form, })



#from MAGE.tkm.models import Workflow
#from MAGE.gph.graphs_tkm import drawWorkflow
#
#def view_workflow(request, wkf):
#    try:
#        wk = Workflow.objects.get(pk = int(wkf))
#    except:
#        wk = Workflow.objects.get(name = wkf) #may raise exceptions
#    return HttpResponse(drawWorkflow(wk), mimetype="image/png")
