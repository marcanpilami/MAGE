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


def new_items(request):
    """Hub for creating all sorts of items"""
    return render(request, 'ref/ref_new_items.html', {'impls': ImplementationDescription.objects.all()})

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

@permission_required('ref.scm_addcomponentinstance')
@atomic
def new_ci_step2(request, instance_id):
    instance = ComponentInstance.objects.select_related('description', 'implements')\
            .prefetch_related(
                  Prefetch('field_set', ComponentInstanceField.objects.order_by('field__widget_row', 'field__name').select_related('field')),
                  Prefetch('rel_target_set', ComponentInstanceRelation.objects.order_by('field__name').select_related('field')))\
            .prefetch_related('environments', 'description__field_set', 'description__target_set').get(pk=instance_id)
    descr = instance.description
    cls = form_for_model(descr)

    if request.POST:
        form = cls(request.POST)
        if form.is_valid():
            instance.deleted = form.cleaned_data['_deleted']
            instance.environments = form.cleaned_data['_envts']
            instance.instanciates = form.cleaned_data['_instanciates']
            instance.include_in_envt_backup = form.cleaned_data['_backup']
            
            for field in descr.field_set.all():
                if not field.name in form.changed_data:
                    continue
                new_data = form.cleaned_data[field.name]
                ComponentInstanceField.objects.update_or_create(defaults={'value': new_data} , field=field, instance=instance)

                for field in descr.target_set.all():
                    if not field.name in form.changed_data:
                        continue
                    new_data = form.cleaned_data[field.name]
                    ComponentInstanceRelation.objects.update_or_create(defaults={'target': new_data}, source=instance, field=field)
                
            instance.save()
    else:
        di = {'_id': instance.pk, '__descr_id': instance.description_id, '_deleted': instance.deleted, '_backup': instance.include_in_envt_backup,
              '_instanciates' : instance.instanciates_id, '_envts' : [e.id for e in instance.environments.all()]}

        for field_instance in instance.field_set.all():
            di[field_instance.field.name] = field_instance.value

        for field_instance in instance.rel_target_set.all():
            di[field_instance.field.name] = field_instance.target_id

        form = cls(di)  # unbound form

    return render_to_response("ref/instance_edit_step2.html", {'form': form, 'descr' : descr, 'instance': instance})



class NewEnvtForm(forms.Form):
    name = forms.CharField(max_length=30)
    description = forms.CharField(max_length=100)

class CicChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return '%s - [%s] - offre [%s]' % (obj.implements.application, obj.implements.name, obj.name)

class CiChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return ' %s - %s (%s)' % (obj.first_environment(), obj.name, obj.instanciates.name if obj.instanciates else 'none')


## Forms for item creation (step 1)
class NewCiStep1Form(forms.Form):
    _env = forms.ModelChoiceField(queryset=Environment.objects.all(), label='Environnement', required=False)

    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-lg-2'
    helper.field_class = 'col-lg-9'
    helper.add_input(Submit('submit', 'Submit'))


def form_for_model_relations(descr):
    attrs = {}

    # CIC
    if descr.cic_set.count() > 0:
        attrs['_cic'] = CicChoiceField(queryset=descr.cic_set.order_by('implements__application__name', 'implements__name', 'name').select_related('implements__application').all(),
                                       label='Offre technique implémentée', required=False)

    # Relations
    for field in descr.target_set.filter(max_cardinality__lte=1).prefetch_related('target__instance_set'):
        f = CiChoiceField(queryset=field.target.instance_set.order_by('environments__name').prefetch_related('environments'), label=field.label, required=field.min_cardinality == 1)
        attrs[field.name] = f

    cls = type(str("__" + descr.name.lower() + "_form"), (NewCiStep1Form,), attrs)
    return cls

## Forms for single item edition (also 2nd step of creation)
class ModelChoiceFieldCIC(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s (%s)" % (obj.name, obj.description)

class MiniModelForm(forms.Form):
    _id = forms.IntegerField(widget=forms.HiddenInput, required=False)
    _deleted = forms.BooleanField(required=False, label='effacé')
    _backup = forms.BooleanField(required = False, label='inclus dans backup')
    _instanciates = ModelChoiceFieldCIC(queryset=ComponentImplementationClass.objects, required=False, label='offre implémentée')
    _envts = forms.ModelMultipleChoiceField(queryset=Environment.objects.order_by('name').filter(template_only=False, active=True), required=False, label='environnements')    

    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-lg-2'
    helper.field_class = 'col-lg-9'
    helper.add_input(Submit('submit', 'Submit'))

def form_for_model(descr):
    attrs = {}

    # Simple fields
    for field in descr.field_set.all():  #.order_by('widget_row', 'name').all():
        f = forms.CharField(label=field.short_label, required=field.compulsory)
        attrs[field.name] = f

    # Relations
    for field in descr.target_set.all():
        if field.max_cardinality > 1:
            continue
        f = forms.ModelChoiceField(queryset=field.target.instance_set, label=field.label, required=field.min_cardinality == 1)
        attrs[field.name] = f

    return type(str("__" + descr.name.lower() + "_form"), (MiniModelForm,), attrs)
