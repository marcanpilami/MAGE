# coding: utf-8
'''
    @license: Apache License, Version 2.0
    @copyright: 2007-2013 Marc-Antoine Gouillart
    @author: Marc-Antoine Gouillart
'''

## Django imports
from django import forms
from django.http import HttpResponse
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import PermissionDenied
from django.db.models.fields.related import ManyToManyField, ForeignKey
from django.shortcuts import render, redirect, render_to_response
from django.forms.formsets import formset_factory
from django.db.models import Q

## MAGE imports
from MAGE.exceptions import MageCallerError
from ref.csvi import get_components_csv, get_components_pairs
from ref.creation import duplicate_envt, create_instance
from ref.forms import DuplicateForm, DuplicateFormRelInline
from ref.models import ComponentInstance, Environment, ImplementationDescription
from ref.mcl import parser
from prm.models import getMyParams, getParam
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
import unicodedata
from ref.graphs_mlg import getGraph, DrawingContext


##############################################################################
## Shell and CSV export
##############################################################################

def csv(request, url_end):
    comps = ComponentInstance.objects.filter(pk__in=url_end.split(','))
    return HttpResponse(get_components_csv(comps, displayRestricted=(request.user.is_authenticated() and request.user.has_perm('ref.allfields_componentinstance'))), mimetype="text/csv")


##############################################################################
## Home screen
##############################################################################

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


##############################################################################
## Envt list & detail
##############################################################################

def envts(request):
    return render(request, 'ref/envts.html', {'envts': Environment.objects_active.filter(template_only=False).order_by('typology__chronological_order', 'typology__name'), 'colors': getParam('MODERN_COLORS').split(',')})

def templates(request):
    return render(request, 'ref/envts.html', {'envts': Environment.objects.filter(template_only=True).order_by('typology'), 'colors': getParam('MODERN_COLORS').split(',')})

def envt(request, envt_id):
    envt = Environment.objects.select_related('field_set__field').select_related('rel_target_set').select_related('implementation__computed_field_set').get(pk=envt_id)
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

    return render(request, 'ref/model_details.html', {'res' : sorted(res.iteritems(), key=lambda (k, v) :  v['id']['name']) })


##############################################################################
## Queries
##############################################################################

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


def mcl_query_shell(request, mcl):
    res = parser.get_components(mcl)
    compos = get_components_pairs(res, request.user.is_authenticated() and request.user.has_perm('ref.allfields_componentinstance'))
    return render(request, 'ref/shell_mcl_result_ksh.html', {'attrs': compos}, content_type="text/text")

def mcl_create(request, mcl, use_convention='1'):
    if use_convention == '1':
        use_convention = True
    else:
        use_convention = False
    res = create_instance(mcl, use_convention)

    response = HttpResponse(content_type='text/csv')
    get_components_csv(res, True, response, displayRestricted=(request.user.is_authenticated() and request.user.has_perm('ref.allfields_componentinstance')))
    return response


##############################################################################
## Misc
##############################################################################

def mcl_create_without_convention(request, mcl):
    return mcl_create(request, mcl, '0')

def envt_duplicate(request, envt_name):
    e = duplicate_envt(envt_name, "new_name", {})

    return redirect('admin:ref_environment_change', e.id)

@permission_required('ref.scm_addenvironment')
def envt_duplicate_name(request, envt_name):
    e = Environment.objects.get(name=envt_name)
    FS = formset_factory(DuplicateFormRelInline, extra=0)

    if request.method == 'POST': # If the form has been submitted...
        form = DuplicateForm(request.POST, envt=e) # A form bound to the POST data
        fs = FS(request.POST)

        if form.is_valid() and fs.is_valid(): # All validation rules pass
            remaps = {}
            for f in fs.cleaned_data:
                if f['new_target']:
                    remaps[f['old_target'].id] = f['new_target'].id
            e1 = duplicate_envt(envt_name, form.cleaned_data['new_name'], remaps, *ComponentInstance.objects.filter(pk__in=form.cleaned_data['instances_to_copy']))
            return redirect('admin:ref_environment_change', e1.id)
    else:
        form = DuplicateForm(envt=e) # An unbound form

        ## Create a formset for each external relation
        internal_pks = [i.pk for i in e.component_instances.all()]
        ext = {}
        initial_rel = []
        for cpn in e.component_instances.all():
            for rel in cpn.connectedTo.all() | cpn.dependsOn.all():
                if not rel.id in internal_pks:
                    ext[rel] = None
        for rel in ext.keys():
            initial_rel .append({'old_target':rel, 'new_target': None})
        fs = FS(initial=initial_rel)

    return render(request, 'ref/envt_duplicate.html', {'form': form, 'envt': e, 'fs': fs})

def urls(request):
    return render(request, 'ref/urls.html')


##############################################################################
## Script helpers
##############################################################################

def script_login(request, username, password):
    user = authenticate(username=username, password=password)
    if user is not None and user.is_active:
        login(request, user)
        return HttpResponse("<html><body>User authenticated</body></html>")
    else:
        raise PermissionDenied # will return a 403 (HTTP forbidden)

def script_logout(request):
    logout(request)
    return HttpResponse("<html><body>User logged out</body></html>")


##############################################################################
## Cartography
##############################################################################

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
    # Create png with GraphWiz
    dc = DrawingContext()
    dc.connection_level = 2
    dc.collapse_threshold = 5
    cfilter = {'environments__pk':envt_id}

    # Return the picture
    return HttpResponse(getGraph(cfilter, context=dc), content_type="image/png")

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
