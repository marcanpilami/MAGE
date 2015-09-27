# coding: utf-8

# Python imports
import json

# Django imports
from django import forms
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models.query_utils import Q
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render_to_response, render

# MAGE imports
from ref.models import Environment, ComponentInstance, ImplementationDescription, ImplementationRelationType, \
    AdministrationUnit, get_user_scope, folder_permission_required
from ref.graph_mlg2 import getNetwork
from ref.graph_struct import getStructureTree


class ModelMultipleChoiceFieldDescription(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return "%s%s" % (obj.description[0].capitalize(), obj.description[1:])


########################################################################################################################
# Masupilamographe forms & views
########################################################################################################################
class CartoForm(forms.Form):
    envts = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.widgets.CheckboxSelectMultiple,
        label=u'Restreindre aux environnements ',
        required=False)

    models = ModelMultipleChoiceFieldDescription(
        queryset=None,
        widget=forms.widgets.CheckboxSelectMultiple,
        required=False,
        label=u'Restreindre aux types ')

    reltypes = forms.ModelMultipleChoiceField(
        queryset=ImplementationRelationType.objects.all(),
        widget=forms.widgets.CheckboxSelectMultiple,
        required=False,
        label=u'Suivre les liens ')

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

    scope = forms.MultipleChoiceField(
        choices=(),
        label=u'Restreindre aux dossiers ',
        required=False,
        widget=forms.widgets.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        if 'scope_restriction' in kwargs:
            self.scope_restriction = kwargs['scope_restriction']
            del kwargs['scope_restriction']
        if 'initial_scope' in kwargs:
            self.initial_scope = kwargs['initial_scope']
            del kwargs['initial_scope']

        super(CartoForm, self).__init__(*args, **kwargs)
        self.fields['models'].queryset = ImplementationDescription.objects.order_by('tag', 'name').all()
        # self.fields['models'].initial = [m.pk for m in ImplementationDescription.objects.all()]
        self.fields['reltypes'].queryset = ImplementationRelationType.objects.all()
        self.fields['reltypes'].initial = [m.pk for m in ImplementationRelationType.objects.all()]
        try:
            self.fields['scope'].choices = [(i.pk, i.name) for i in self.scope_restriction]
            if hasattr(self, 'initial_scope'):
                self.fields['scope'].initial = self.initial_scope

            self.fields['envts'].queryset = Environment.objects_active.all().order_by('typology__chronological_order',
                                                                                      'name').filter(
                project__in=self.scope_restriction)
        except AttributeError:
            self.fields['scope'].choices = [(i.pk, i.name) for i in AdministrationUnit.objects.all()]
            self.fields['envts'].queryset = Environment.objects_active.all().order_by('typology__chronological_order',
                                                                                      'name')
            self.fields['envts'].initial = [] if Environment.objects_active.count() == 0 else [
                Environment.objects_active.order_by('typology__chronological_order', 'name')[0].pk, ]


@folder_permission_required('read_envt')
def carto_form(request, folder_id):
    """ Marsupilamographe view - basically only a form with some javascript that will query carto_content_form """
    return render_to_response('ref/view_carto2.html', {
        'form': CartoForm(scope_restriction=get_user_scope(folder_id, request.user, 'read_envt'),
                          initial_scope=folder_id),
        'folder_id': folder_id})


@login_required
def carto_content_form(request):
    """ The view actually returning data (AJAX) to the marsupilamographe """
    form = None
    if request.method == 'POST':  # If the form has been submitted...
        form = CartoForm(request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            rs = ComponentInstance.objects.all()

            if len(form.cleaned_data['envts']) > 0:
                rs = rs.filter(environments__pk_in=form.cleaned_data['envts'])

            if len(form.cleaned_data['models']) > 0:
                rs = rs.filter(description_id__in=form.cleaned_data['models'])

            if len(form.cleaned_data['scope']) > 0:
                ids = [int(i) for i in form.cleaned_data['scope']]
                print ids
                rs = rs.filter(Q(project_id__in=ids) | Q(environments__project_id__in=ids))

            te = {}
            for lt in form.cleaned_data['reltypes']:
                te[lt.name] = form.cleaned_data['relRecursion']

            # security: only allow instances from allowed scopes
            scope = get_user_scope(AdministrationUnit.objects.get(name='root'), request.user, 'read_envt')
            rs = rs.filter(Q(environments__project__in=scope) | Q(project__in=scope))

            response = HttpResponse(content_type='text/json; charset=utf-8')
            json.dump(getNetwork(rs.all(), select_related=te, collapse_threshold=form.cleaned_data['collapseThr']),
                      fp=response, ensure_ascii=False, indent=4)
            return response

    return HttpResponseBadRequest(form.errors if form else 'only available through form POST')


########################################################################################################################
# Views helping with specific CI graphs
########################################################################################################################

# TODO: security. Or remove - not really useful.
def carto_content(request, ci_id_list, collapse_threshold=3, select_related=2):
    response = HttpResponse(content_type='text/json; charset=utf-8')
    json.dump(getNetwork(ComponentInstance.objects.filter(id__in=[int(i) for i in ci_id_list.split(',')]),
                         select_related=dict(
                             (t.name, int(select_related)) for t in ImplementationRelationType.objects.all()),
                         collapse_threshold=int(collapse_threshold)), fp=response, ensure_ascii=False, indent=4)
    return response


@user_passes_test(lambda u: u.is_staff)
def carto_full(request):
    """  View - Graph with all CI """
    return render_to_response('ref/view_carto_full.html')


@user_passes_test(lambda u: u.is_staff)
def carto_content_full(request, collapse_threshold=3):
    """  Content - Graph with all CI """
    response = HttpResponse(content_type='text/json; charset=utf-8')
    json.dump(getNetwork(ComponentInstance.objects.filter(deleted=False).all(), select_related={},
                         collapse_threshold=int(collapse_threshold)), fp=response, ensure_ascii=False, indent=4)
    return response


@folder_permission_required('read_envt')
def carto_content_scope(request, folder_id, collapse_threshold=3):
    """  Content - Graph with all CI within a scope (not recursive) """
    response = HttpResponse(content_type='text/json; charset=utf-8')
    json.dump(getNetwork(ComponentInstance.objects.filter(deleted=False, environments__project_id=folder_id).all(),
                         select_related={}, collapse_threshold=int(collapse_threshold)), fp=response,
              ensure_ascii=False, indent=4)
    return response


@folder_permission_required('read_envt')
def carto_scope(request, folder_id):
    """  Content - Graph with all CI within a scope (not recursive) """
    return render_to_response('ref/view_carto_full.html', {'scope_id': folder_id})


########################################################################################################################
# Structure graphs
########################################################################################################################

@folder_permission_required('view_meta')
def carto_description_content(request, folder_id):
    response = HttpResponse(content_type='text/json; charset=utf-8')
    json.dump(getStructureTree(), fp=response, ensure_ascii=False, indent=4)
    return response


@folder_permission_required('view_meta')
def carto_description(request, folder_id):
    return render_to_response('ref/view_carto_struct.html')


########################################################################################################################
# Debug helpers
########################################################################################################################

@user_passes_test(lambda u: u.is_staff)
def carto_debug(request):
    response = HttpResponse(content_type='text/json; charset=utf-8')
    json.dump(getNetwork(Environment.objects.get(name='DEV1').component_instances.all(),
                         select_related=dict((t.name, 2) for t in ImplementationRelationType.objects.all()),
                         collapse_threshold=3),
              fp=response, ensure_ascii=False, indent=4)
    return render(request, 'ref/debug_mlgdata.html', {'json': response, })
