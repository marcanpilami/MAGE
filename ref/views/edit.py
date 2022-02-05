# coding: utf-8

## Python imports
from functools import wraps, partial

## Django imports
from django import forms
from django.forms.formsets import formset_factory
from django.forms.models import ModelChoiceIterator, ModelForm, modelformset_factory
from django.forms.widgets import CheckboxSelectMultiple, CheckboxInput
from django.shortcuts import render, redirect

from django.db.models.query import Prefetch
from django.db.transaction import atomic
from django.core.cache import cache

## MAGE imports
from ref.models import ComponentImplementationClass, ComponentInstanceRelation, ComponentInstanceField, ComponentInstance, Environment, ImplementationDescription
from ref.conventions import value_instance_fields, value_instance_graph_fields
from ref.permissions.perm_check import permission_required_project_aware


'''
    This file contains all views and forms related to modifying component instances
    (exception: standard creation and modification are in envt_new.py)
'''


#####################################################################
## Edit all CI related to an environment
#####################################################################

@atomic
@permission_required_project_aware('ref.modify_project')
def envt_instances(request, envt_id=1):
    e = Environment.objects.get(pk=envt_id)
    # ModelChoiceIterator optim - https://code.djangoproject.com/ticket/22841

    ffs = {}
    typ_items = {}
    for instance in e.component_instances.prefetch_related('description__field_set').prefetch_related('description__target_set').\
            prefetch_related('field_set__field', 'rel_target_set').\
            prefetch_related('rel_target_set__field').\
            order_by('description__tag'):
        # for each instance, crate a dict containing all the values
        di = {'_id': instance.pk, '__descr_id': instance.description_id, '_deleted': instance.deleted, '_instanciates' : instance.instanciates_id}

        for field_instance in instance.field_set.all():
            if field_instance.field.datatype == 'bool':
                di[field_instance.field.name] = field_instance.value == 'True'
            else:
                di[field_instance.field.name] = field_instance.value

        for field_instance in instance.rel_target_set.all():
            di[field_instance.field.name] = field_instance.target_id

        # add the dict to a list of instances with the same description
        if instance.description in typ_items:
            typ_items[instance.description].append(di)
        else:
            typ_items[instance.description] = [di, ]

    for typ, listi in typ_items.items():
        cls = form_for_model(typ)
        InstanceFormSet = formset_factory(wraps(cls)(partial(cls,
                 cics=ComponentImplementationClass.objects.filter(technical_description_id=typ.id).order_by('name'))) , extra=0)
        ffs[typ] = InstanceFormSet(request.POST or None, initial=listi, prefix=typ.name)

    if request.POST:
        valid = True
        for typ, formset in ffs.items():
            if not formset.is_valid():
                valid = False
                break

        if valid:
            for typ, formset in ffs.items():
                if formset.has_changed():
                    for form in formset:
                        if form.has_changed():
                            instance_id = form.cleaned_data['_id'] if '_id' in form.cleaned_data else None
                            instance = None
                            if instance_id:
                                instance = ComponentInstance.objects.get(pk=instance_id)
                            else:
                                instance = ComponentInstance(description=typ)
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


    return render(request, "ref/instance_envt.html", {'fss': ffs, 'envt': e})


## Forms
class MiniModelForm(forms.Form):
    def __init__(self, cics, **kwargs):
        super(MiniModelForm, self).__init__(**kwargs)
        iterator = ModelChoiceIterator(self.fields['_instanciates'])
        choices = [iterator.choice(obj) for obj in cics]
        choices.append(("", self.fields['_instanciates'].empty_label))
        self.fields['_instanciates'].choices = choices

    _id = forms.IntegerField(widget=forms.HiddenInput, required=False)
    _descr_id = forms.IntegerField(widget=forms.HiddenInput, required=False)
    _instanciates = forms.ModelChoiceField(queryset=ComponentImplementationClass.objects, required=False, label='composant logique')

descr_terseform_cache = {}
def form_for_model(descr):
    attrs = {}
    key = 'descr_terseformset_%s' % descr.id
    if cache.get(key) and key in descr_terseform_cache:
        return descr_terseform_cache[key]

    # Simple fields
    for field in descr.field_set.all():
        if field.datatype == 'bool':
            f = forms.BooleanField(label=field.short_label, required=False)
        elif field.datatype == 'int':
            f = forms.IntegerField(label=field.short_label, required=field.compulsory)
        else:
            f = forms.CharField(label=field.short_label, required=field.compulsory, max_length=255)
        attrs[field.name] = f

    # Relations
    for field in descr.target_set.filter(max_cardinality__lte=1).prefetch_related('target__instance_set'):
        f = forms.ModelChoiceField(queryset=field.target.instance_set, label=field.label, required=field.min_cardinality == 1)
        attrs[field.name] = f

    # deleted checkbox is last
    attrs['_deleted'] = forms.BooleanField(required=False, label="effacé")

    cls = type(str("__" + descr.name.lower() + "_form"), (MiniModelForm,), attrs)
    descr_terseform_cache[key] = cls
    cache.set(key, key)
    return cls


#####################################################
## Debug form for changing types
#####################################################

class HorizontalCheckboxSelectMultiple(CheckboxSelectMultiple):
    template_name="widgets/widget_checkbox_select_multiple_horizontal"

class CIForm(ModelForm):
    def __init__(self, descriptions, envts, cics, **kwargs):
        super(CIForm, self).__init__(**kwargs)
        iterator = ModelChoiceIterator(self.fields['description'])
        choices = [iterator.choice(obj) for obj in descriptions]
        choices.append(("", self.fields['description'].empty_label))
        self.fields['description'].choices = choices

        iterator = ModelChoiceIterator(self.fields['environments'])
        choices = [iterator.choice(obj) for obj in envts]
        self.fields['environments'].choices = choices

        iterator = ModelChoiceIterator(self.fields['instanciates'])
        choices = [iterator.choice(obj) for obj in cics]
        choices.append(("", self.fields['instanciates'].empty_label))
        self.fields['instanciates'].choices = choices


    class Meta:
        model = ComponentInstance
        fields = ['description', 'instanciates', 'environments', 'deleted']
        widgets = {'environments' : HorizontalCheckboxSelectMultiple()}

@atomic
@permission_required_project_aware('ref.modify_project')
def edit_all_comps_meta(request):
    CIFormSet = modelformset_factory(ComponentInstance, form=CIForm, extra=0)
    CIFormSet.form = staticmethod(partial(CIForm, descriptions=ImplementationDescription.objects.all().order_by('name'),
                                        envts=Environment.objects.all().order_by('name'),
                                        cics=ComponentImplementationClass.objects.all().order_by('implements__application__name', 'name')))

    if request.method == 'POST':
        formset = CIFormSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
            return redirect("ref:instance_all")
    else:
        formset = CIFormSet(queryset=ComponentInstance.objects.all().select_related('description').prefetch_related('environments'))

    return render(request, "ref/instance_all.html", {"formset": formset, })


############################################################
## Debug form for changing all elements of a description
############################################################

class ReinitModelForm(ModelForm):
    mage_retemplate = forms.BooleanField(label='T', required=False, widget=CheckboxInput(attrs={'class': 't'}))

    class Meta:
        model = ComponentInstance
        fields = ['instanciates', ]

    def __init__(self, cics, **kwargs):
        super(ReinitModelForm, self).__init__(**kwargs)

        iterator = ModelChoiceIterator(self.fields['instanciates'])
        choices = [iterator.choice(obj) for obj in cics]
        choices.append(("", self.fields['instanciates'].empty_label))
        self.fields['instanciates'].choices = choices

        if self.instance:
            # Stupid: self.instance can be overridden by a field named instance... So we store it inside another field (with a forbidden name)
            self.mage_instance = self.instance

            for field_instance in self.instance.rel_target_set.all():
                if field_instance.field.max_cardinality > 1:
                    continue
                self.fields[field_instance.field.name].initial = field_instance.target_id

            for field_instance in self.instance.field_set.all():
                self.fields[field_instance.field.name].initial = field_instance.value

    def save(self, commit=True):
        for field in self.mage_instance.description.field_set.all():
            if not field.name in self.changed_data:
                    continue
            new_data = self.cleaned_data[field.name]
            ComponentInstanceField.objects.update_or_create(defaults={'value': new_data} , field=field, instance=self.mage_instance)

        for field in self.mage_instance.description.target_set.all():
            if not field.name in self.changed_data:
                continue
            new_data = self.cleaned_data[field.name]
            ComponentInstanceRelation.objects.update_or_create(defaults={'target': new_data}, source=self.mage_instance, field=field)

        super(ReinitModelForm, self).save(commit=commit)

        ## Template application can only occur after everything is saved, so is at the end of save()
        if self.cleaned_data['mage_retemplate']:
            value_instance_fields(self.instance, force=True)
            value_instance_graph_fields(self.instance, force=True)

def reinit_form_for_model(descr):
    attrs = {}

    # Relations
    for field in descr.target_set.filter(max_cardinality__lte=1).prefetch_related('target__instance_set'):
        f = forms.ModelChoiceField(queryset=field.target.instance_set, label=field.label, required=field.min_cardinality == 1)
        attrs[field.name] = f

    # Simple fields
    for field in descr.field_set.all():
        f = forms.CharField(label=field.short_label, required=False)
        attrs[field.name] = f

    return type(str("__" + descr.name.lower() + "_reinitform"), (ReinitModelForm,), attrs)

@atomic
@permission_required_project_aware('ref.modify_project')
def descr_instances_reinit(request, descr_id=4):
    descr = ImplementationDescription.objects.get(pk=descr_id)
    cics = ComponentImplementationClass.objects.filter(technical_description_id=descr_id)

    cls = reinit_form_for_model(descr)
    InstanceFormSet = modelformset_factory(ComponentInstance, form=cls, extra=0)
    InstanceFormSet.form = staticmethod(partial(cls, cics=cics))

    if request.POST:
        formset = InstanceFormSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
            return redirect("ref:instance_descr_reinit", descr_id)
    else:
        instances = ComponentInstance.objects.filter(description_id=descr_id).\
                prefetch_related(Prefetch('rel_target_set', queryset=ComponentInstanceRelation.objects.select_related('field'))).\
                prefetch_related(Prefetch('field_set', queryset=ComponentInstanceField.objects.select_related('field'))).\
                prefetch_related('environments')
        formset = InstanceFormSet(queryset=instances)

    return render(request, "ref/instance_descr_reinit.html", {'formset': formset, 'descr': descr})
