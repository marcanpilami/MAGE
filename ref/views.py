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
from ref.forms import DuplicateForm, DuplicateFormRelInline, CartoForm
from ref.models import ComponentInstance, Environment, ImplementationDescription
from ref.mcl import parser
from ref.models.parameters import getMyParams, getParam
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
import unicodedata
from ref.graphs_mlg import getGraph, DrawingContext
from django.db.transaction import atomic
from ref.form_instance import InstanceForm, form_for_model, MiniModelForm
from ref.models.models import ComponentImplementationClass, \
    ComponentInstanceField, ComponentInstanceRelation
from functools import wraps
from _functools import partial
from django.forms.models import ModelChoiceIterator


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
    return render(request, 'ref/model_types.html', {'models' : ImplementationDescription.objects.all()})

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
@atomic
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
            for rel in cpn.relationships.all():
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


##############################################################################
## CI edition
##############################################################################

@atomic
def edit_comp(request, instance_id=None, description_id=None):
    instance = None

    if request.POST:
        cd = MiniModelForm(request.POST)
        if cd.is_valid() and cd.cleaned_data['_id']:
            instance = ComponentInstance.objects.get(pk=cd.cleaned_data['_id'])

    if not request.POST and instance_id:
        instance = ComponentInstance.objects.get(pk=instance_id)

    form = form_for_model(instance.implementation if instance else ImplementationDescription.objects.get(pk=description_id))(request.POST or (instance.proxy if instance else None))

    if request.POST and form.is_valid():
        ## Save fields
        print form.cleaned_data

        ci = None
        if form.cleaned_data.has_key('_id'):
            cid = form.cleaned_data.pop('_id')
            if cid:
                ci = ComponentInstance.objects.get(pk=cid).proxy
        if not ci:
            impl_id = form.cleaned_data['_descr_id'] or description_id
            descr = ImplementationDescription.class_for_id(impl_id)
            ci = descr()
        form.cleaned_data.pop('_descr_id')


        for key, value in form.cleaned_data.iteritems():
            print 'setting %s on %s' % (key , ci._instance.id)
            setattr(ci, key, value)

        ci.save()

        ## Done
        return redirect("ref:instance_edit", instance_id=ci._instance.id)

    return render_to_response("ref/instance_edit.html", {'form': form})

@atomic
def envt_instances(request):
    e = Environment.objects.get(pk=1)
    # ModelChoiceIterator optim - https://code.djangoproject.com/ticket/22841
    cics = ComponentImplementationClass.objects.all()
    #iterator = ModelChoiceIterator(forms.ModelChoiceField(None, required=False, empty_label='kkkkkk'))
    #choices = [iterator.choice(obj) for obj in ComponentImplementationClass.objects.all()]
    #choices.append(iterator.choice(""))

    ffs = {}
    typ_items = {}
    for instance in e.component_instances.prefetch_related('implementation__field_set').prefetch_related('implementation__target_set').\
            prefetch_related('field_set__field', 'rel_target_set').\
            prefetch_related('rel_target_set__field').\
            order_by('implementation__tag'):
        # for each instance, crate a dict containing all the values
        di = {'_id': instance.pk, '__descr_id': instance.implementation_id, '_deleted': instance.deleted, '_instanciates' : instance.instanciates_id}

        for field_instance in instance.field_set.all():
            di[field_instance.field.name] = field_instance.value

        for field_instance in instance.rel_target_set.all():
            di[field_instance.field.name] = field_instance.target_id

        # add the dict to a list of instances with the same implementation
        if typ_items.has_key(instance.implementation):
            typ_items[instance.implementation].append(di)
        else:
            typ_items[instance.implementation] = [di, ]

    for typ, listi in typ_items.iteritems():
        cls = form_for_model(typ)
        InstanceFormSet = formset_factory(wraps(cls)(partial(cls, cics=cics)) , extra=2)
        ffs[typ] = InstanceFormSet(request.POST or None, initial=listi, prefix=typ.name)

    if request.POST:
        valid = True
        for typ, formset in ffs.iteritems():
            if not formset.is_valid():
                valid = False
                break
        if valid:
            print 'ok'
        else:
            print 'ko'

        if valid:
            for typ, formset in ffs.iteritems():
                if formset.has_changed():
                    for form in formset:
                        if form.has_changed():
                            instance_id = form.cleaned_data['_id'] if form.cleaned_data.has_key('_id') else None
                            instance = None
                            if instance_id:
                                instance = ComponentInstance.objects.get(pk=instance_id)
                            else:
                                instance = ComponentInstance(implementation=typ)
                                instance.save()
                                instance.environments.add(e)

                            if '_deleted' in form.changed_data:
                                instance.deleted = form.cleaned_data['_deleted']
                                
                            if '_instanciates' in form.changed_data:
                                instance.instanciates = form.cleaned_data['_instanciates']

                            for field in typ.field_set.all():
                                if not field.name in form.changed_data:
                                    continue
                                new_data = form.cleaned_data[field.name]
                                ComponentInstanceField.objects.update_or_create(defaults={'value': new_data} , field=field, instance=instance)

                            for field in typ.target_set.all():
                                if not field.name in form.changed_data:
                                    continue
                                new_data = form.cleaned_data[field.name]
                                ComponentInstanceRelation.objects.update_or_create(defaults={'target': new_data}, source=instance, field=field)
                            instance.save()


    return render_to_response("ref/instance_envt.html", {'fss': ffs, 'envt': e})


