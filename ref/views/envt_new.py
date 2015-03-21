# coding: utf-8

## Django imports
from django import forms
from django.shortcuts import render, render_to_response, redirect
from django.db.transaction import atomic
from django.contrib.auth.decorators import permission_required

## MAGE imports
from ref.models import ComponentImplementationClass, ImplementationDescription, Environment, ComponentInstance, ComponentInstanceField, ComponentInstanceRelation

## Other libs imports
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.db.models.query import Prefetch

''' 
    This file contains views and form for the standard component instance creation and update. (unitary forms)

    Creation is divided in two forms so as to be able to apply naming conventions during creation:
    * first step asks for the environment and linked items, for these could be used in convention
    * naming convention is applied and component instance is created with only this data 
      (may result in an incorrect CI for compulsory fields may still be null after applying conventions)
    * second step allows to edit the same data, plus all fields
'''

def new_items(request):
    """Hub for creating all sorts of items"""
    return render(request, 'ref/ref_new_items.html', {'impls': ImplementationDescription.objects.all()})


#####################################################################
## STEP 1: envt + relationships
#####################################################################

## Views
@permission_required('ref.scm_addcomponentinstance')
@atomic
def new_ci_step1(request, description_id):
    descr = ImplementationDescription.objects.get(pk=description_id)
    cls = form_for_model_relations(descr)

    if request.POST:
        form = cls(request.POST)
        if form.is_valid():
            ## Do things & redirect
            ci = ImplementationDescription.class_for_name(descr.name)(**form.cleaned_data)
            ci.save()
            return redirect('ref:edit_ci', instance_id=ci._instance.pk)
    else:
        form = cls()  # unbound form

    return render_to_response("ref/instance_edit_step1.html", {'form': form, 'descr' : descr})

## Forms
class NewCiStep1Form(forms.Form):
    _env = forms.ModelChoiceField(queryset=Environment.objects.all(), label='Environnement', required=False)

    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-lg-2'
    helper.field_class = 'col-lg-9'
    helper.add_input(Submit('submit', 'Submit'))

class CicChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return '%s - [%s] - offre [%s]' % (obj.implements.application, obj.implements.name, obj.name)

class CiChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return ' %s - %s (%s)' % (obj.first_environment(), obj.name, obj.instanciates.name if obj.instanciates else 'none')

def form_for_model_relations(descr):
    attrs = {}

    # CIC
    if descr.cic_set.count() > 0:
        attrs['_cic'] = CicChoiceField(queryset=descr.cic_set.order_by('implements__application__name', 'implements__name', 'name').select_related('implements__application').all(),
                                       label='Offre technique implémentée', required=False)

    # Relations
    for field in descr.target_set.filter(max_cardinality__lte=1).prefetch_related('target__instance_set'):
        f = CiChoiceField(queryset=field.target.instance_set.order_by('environments__name').select_related('instanciates').prefetch_related('environments'), label=field.label, required=field.min_cardinality == 1)
        attrs[field.name] = f

    cls = type(str("__" + descr.name.lower() + "_form"), (NewCiStep1Form,), attrs)
    return cls


#####################################################################
## STEP 2: all fields
#####################################################################

# Views
@permission_required('ref.scm_addcomponentinstance')
@atomic
def new_ci_step2(request, instance_id):  # always edit an existing CI - to create a CI use step 1.
    instance = ComponentInstance.objects.select_related('description', 'implements')\
            .prefetch_related(
                  Prefetch('field_set', ComponentInstanceField.objects.order_by('field__widget_row', 'field__name').select_related('field')),
                  Prefetch('rel_target_set', ComponentInstanceRelation.objects.order_by('field__name').select_related('field')))\
            .prefetch_related('environments', 'description__field_set', 'description__target_set').get(pk=instance_id)
    cls = form_for_model(instance.description)

    if request.POST:
        form = cls(request.POST, instance=instance)
        if form.is_valid():
            form.save()
    else:
        form = cls(instance=instance)

    return render_to_response("ref/instance_edit_step2.html", {'form': form, 'descr' : instance.description, 'instance': instance})


# Forms
class FullCIEditFormBase(forms.ModelForm):
    class Meta:
        model = ComponentInstance
        fields = ['deleted', 'include_in_envt_backup', 'instanciates', 'environments', ]
        
    def __init__(self, *args, **kwargs):
        super(FullCIEditFormBase, self).__init__(*args, **kwargs)
        
        ## Restrict some choices
        self.fields["environments"].queryset = Environment.objects.order_by('name').filter(template_only=False, active=True)
        self.fields["instanciates"].queryset = ComponentImplementationClass.objects.order_by('implements__application__name', 'name').filter(active=True, implements__active=True)

        ## Stupid: self.instance can be overridden by a field named instance... So we store it inside another field (with a forbidden name)
        self.mage_instance = self.instance

        ## Init dynamic fields values
        for field_instance in self.instance.rel_target_set.all():
            self.fields[field_instance.field.name].initial = field_instance.target_id

        for field_instance in self.instance.field_set.all():
            self.fields[field_instance.field.name].initial = field_instance.value
    
    def save(self, commit=True):
        if len(self.changed_data) == 0:
            return
        
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

        super(FullCIEditFormBase, self).save(commit=commit)

            
    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-lg-2'
    helper.field_class = 'col-lg-9'
    helper.add_input(Submit('submit', 'Submit'))

def form_for_model(descr):
    attrs = {}

    # Simple fields
    for field in descr.field_set.all():  #.order_by('widget_row', 'name').all():
        if field.datatype == 'bool':
            f = forms.BooleanField(label=field.short_label, required=False)
        elif field.datatype == 'int':
            f = forms.IntegerField(label=field.short_label, required=field.compulsory)
        else:
            f = forms.CharField(label=field.short_label, required=field.compulsory, max_length=255)
        attrs[field.name] = f

    # Relations
    for field in descr.target_set.all():
        if field.max_cardinality > 1:
            continue
        f = forms.ModelChoiceField(queryset=field.target.instance_set, label=field.label, required=field.min_cardinality == 1)
        attrs[field.name] = f

    return type(str("__" + descr.name.lower() + "_form"), (FullCIEditFormBase,), attrs)
