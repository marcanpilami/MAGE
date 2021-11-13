# coding: utf-8

## Python imports
import json

## Django imports
from django import forms
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render

## MAGE imports
from ref.models import Environment, ImplementationDescription
from ref.graph_mlg2 import getNetwork
from ref.models.description import ImplementationRelationType
from ref.models.instances import ComponentInstance
from ref.graph_struct import getStructureTree
from django.db.models import Q


class CartoForm(forms.Form):
    envts = forms.ModelMultipleChoiceField(
                    queryset=None,
                    widget=forms.widgets.CheckboxSelectMultiple,
                    label=u'Environnements ')

    models = forms.ModelMultipleChoiceField(
                    queryset=None,
                    widget=forms.widgets.CheckboxSelectMultiple,
                    required=False,
                    label=u'Composants ')

    reltypes = forms.ModelMultipleChoiceField(
                    queryset=ImplementationRelationType.objects.all(),
                    widget=forms.widgets.CheckboxSelectMultiple,
                    required=False,
                    label=u'Suivre ')

    relRecursion = forms.IntegerField(
                    label=u'sur générations ',
                    max_value=3,
                    min_value=0,
                    initial=1)

    collapseThr = forms.IntegerField(
                    label=u'Réunir éléments similaires à partir de ',
                    max_value=20,
                    min_value=0,
                    initial=3)
    
    include_deleted = forms.BooleanField(
                    label=u'inclure éléments effacés',
                    initial=False,
                    required=False)

    def __init__(self, *args, project, **kwargs):
        self.project = project
        super().__init__(*args, **kwargs)

        if project == 'all':
            self.fields['envts'].queryset = Environment.objects_active.all().order_by('typology__chronological_order', 'name')
            self.fields['envts'].initial = [] if Environment.objects_active.count() == 0 else [Environment.objects_active.order_by('typology__chronological_order', 'name')[0].pk, ]
        else:
            self.fields['envts'].queryset = Environment.objects_active.filter(project=project).order_by('typology__chronological_order', 'name')
            self.fields['envts'].initial = [] if Environment.objects_active.filter(project=project).count() == 0 else [Environment.objects_active.filter(project=project).order_by('typology__chronological_order', 'name')[0].pk, ]

        self.fields['models'].queryset = ImplementationDescription.objects.order_by('tag', 'name').all()
        self.fields['models'].initial = [m.pk for m in ImplementationDescription.objects.all()]
        self.fields['reltypes'].queryset = ImplementationRelationType.objects.all()
        self.fields['reltypes'].initial = [m.pk for m in ImplementationRelationType.objects.all()]

def carto_form(request, project='all'):
    """Marsupilamographe"""
    return render(request, 'ref/view_carto2.html', {'formset': CartoForm(project=project)})

def carto_content_form(request, project='all'):
    form = None
    if request.method == 'POST':  # If the form has been submitted...
        form = CartoForm(data=request.POST,project=project)
        if form.is_valid():  # All validation rules pass
            if form.cleaned_data['include_deleted']:
                rs = ComponentInstance.objects.all()
            else:
                rs = ComponentInstance.objects.filter(deleted=False)

            if len(form.cleaned_data['envts']) > 0:
                rs = rs.filter(environments__pk__in=form.cleaned_data['envts'])

            if len(form.cleaned_data['models']) > 0:
                rs = rs.filter(description_id__in=form.cleaned_data['models'])

            te = {}
            for lt in form.cleaned_data['reltypes']:
                te[lt.name] = form.cleaned_data['relRecursion']

            response = HttpResponse(content_type='text/json; charset=utf-8')
            json.dump(getNetwork(rs.all(), select_related=te, collapse_threshold=form.cleaned_data['collapseThr']), fp=response, ensure_ascii=False, indent=4)
            return response

    return HttpResponseBadRequest(form.errors if form else 'only available through form POST')

def carto_content(request, ci_id_list, collapse_threshold=3, select_related=2):
    response = HttpResponse(content_type='text/json; charset=utf-8')
    json.dump(getNetwork(ComponentInstance.objects.filter(id__in=[int(i) for i in ci_id_list.split(',')]), select_related=dict((t.name, int(select_related)) for t in ImplementationRelationType.objects.all()), collapse_threshold=int(collapse_threshold)), fp=response, ensure_ascii=False, indent=4)
    return response

def carto_content_full(request, collapse_threshold=3, project=None):
    response = HttpResponse(content_type='text/json; charset=utf-8')
    if not project:
        json.dump(getNetwork(ComponentInstance.objects.filter(deleted=False).all(), select_related={}, collapse_threshold=int(collapse_threshold)), fp=response, ensure_ascii=False, indent=4)
    else:
        json.dump(getNetwork(ComponentInstance.objects.filter(Q(deleted=False), Q(environments__project__name=project)).all(), select_related={}, collapse_threshold=int(collapse_threshold)), fp=response, ensure_ascii=False, indent=4)
    return response

def carto_description_content(request):
    response = HttpResponse(content_type='text/json; charset=utf-8')
    json.dump(getStructureTree(), fp=response, ensure_ascii=False, indent=4)
    return response

def carto_description(request):
    return render(request, 'ref/view_carto_struct.html')

def carto_full(request):
    return render(request, 'ref/view_carto_full.html')

def carto_debug(request):
    response = HttpResponse(content_type='text/json; charset=utf-8')
    json.dump(getNetwork(Environment.objects.get(name='DEV1').component_instances.all(),
                         select_related=dict((t.name, 2) for t in ImplementationRelationType.objects.all()),
                         collapse_threshold=3),
              fp=response, ensure_ascii=False, indent=4)
    return render(request, 'ref/debug_mlgdata.html', {'json': response, })
