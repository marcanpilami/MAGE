# coding: utf-8

from django.http.response import HttpResponse
from ref.graphs_mlg import getGraph, DrawingContext
from django.db.models import Q
import unicodedata
from django import forms
from ref.models import Environment, ImplementationDescription
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.core.cache import cache
import json
from ref.graph_mlg2 import getNetwork


def full_pic(request):
    """Carte de l'ensemble des composants référencés"""
    #cfilter = {'environments__template_only':False}
    uFilter = (Q(environments__isnull=True) | Q(environments__template_only=False),)
    return HttpResponse(getGraph(django_filter_unnamed=uFilter), content_type="image/png")

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
    # cached?
    a = cache.get('view_pic_envt_%s' % envt_id)
    if a:
        return a

    # Create png with GraphWiz
    dc = DrawingContext()
    dc.connection_level = 2
    dc.collapse_threshold = 5
    cfilter = {'environments__pk':envt_id}

    # Return the picture
    a = HttpResponse(getGraph(cfilter, context=dc), content_type="image/png")
    cache.set('view_pic_envt_%s' % envt_id, a, None)
    return a

def view_carto(request):
    """Marsupilamographe"""
    if request.method == 'POST':  # If the form has been submitted...
        form = CartoForm(request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            # Process the data in form.cleaned_data
            cfilter = {}
            cfilter['environments__pk__in'] = form.cleaned_data['envts']
            ad = reverse('ref:grfilter',
                         args=(str(form.cleaned_data['relRecursion']),
                               str(form.cleaned_data['collapseThr']))) + '?environments__pk__in='
            for env in form.cleaned_data['envts']: ad += env + ','
            ad = ad[:-1] + ';implementation__pk__in='
            for pk in form.cleaned_data['models']: ad += pk + ","
            ad = ad[:-1]

            return render_to_response('ref/view_carto.html', {'resultlink': ad, 'machin':'truc', 'form': form, })
    else:
        form = CartoForm()  # An unbound form

    return render_to_response('ref/view_carto.html', {'form': form, })


class CartoForm(forms.Form):
    envts = forms.ModelMultipleChoiceField(
                    queryset=Environment.objects.all().order_by('typology__chronological_order', 'name'),
                    widget=forms.widgets.CheckboxSelectMultiple,
                    #initial=[] if Environment.objects.filter(template_only=False).count() == 0 else [Environment.objects.filter(template_only=False).order_by('typology__chronological_order', 'name')[0].pk],
                    label=u'Environnements à afficher')

    models = forms.ModelMultipleChoiceField(
                    queryset=ImplementationDescription.objects.all(),
                    widget=forms.widgets.CheckboxSelectMultiple,
                    #initial=[m.pk for m in ImplementationDescription.objects.all()],
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


def carto_form(request):
    return render_to_response('ref/view_carto2.html')

def carto_content(request):
    response = HttpResponse(content_type='text/json; charset=utf-8')
    json.dump(getNetwork(Environment.objects.get(name='DEV1').component_instances.all()), fp=response, ensure_ascii=False, indent=4)
    return response

