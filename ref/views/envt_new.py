# coding: utf-8
from django import forms
from ref.models import ComponentImplementationClass, ImplementationDescription, Environment, ComponentInstance, ComponentInstanceField, ComponentInstanceRelation
from django.shortcuts import render, render_to_response, redirect
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


def new_items(request):
    """Hub for creating all sorts of items"""
    return render(request, 'ref/ref_new_items.html', {'impls': ImplementationDescription.objects.all()})

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
        form = cls() # unbound form

    return render_to_response("ref/instance_edit_step1.html", {'form': form, 'descr' : descr})

def new_ci_step2(request, instance_id):
    instance = ComponentInstance.objects.get(pk=instance_id)
    descr = instance.implementation
    cls = form_for_model(descr)

    if request.POST:
        form = cls(request.POST)
        if form.is_valid():
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
        di = {'_id': instance.pk, '__descr_id': instance.implementation_id, '_deleted': instance.deleted, '_instanciates' : instance.instanciates_id}

        for field_instance in instance.field_set.all():
            di[field_instance.field.name] = field_instance.value

        for field_instance in instance.rel_target_set.all():
            di[field_instance.field.name] = field_instance.target_id

        form = cls(di) # unbound form

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
    _cic = CicChoiceField(queryset=ComponentImplementationClass.objects.order_by('implements__application__name', 'implements__name', 'name').all(), label='Offre technique implémentée', required=False)
    _env = forms.ModelChoiceField(queryset=Environment.objects.all(), label='Environnement', required=False)

    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-lg-2'
    helper.field_class = 'col-lg-9'
    helper.add_input(Submit('submit', 'Submit'))


__form_for_model_relations_cache = {}
def form_for_model_relations(descr):
    if __form_for_model_relations_cache.has_key(descr.id):
        return __form_for_model_relations_cache[descr.id]
    attrs = {}

    # Relations
    for field in descr.target_set.filter(max_cardinality__lte=1).prefetch_related('target__instance_set'):
        f = CiChoiceField(queryset=field.target.instance_set.order_by('environments__name'), label=field.label, required=field.min_cardinality == 1)
        attrs[field.name] = f

    cls = type(str("__" + descr.name.lower() + "_form"), (NewCiStep1Form,), attrs)
    __form_for_model_relations_cache[descr.id] = cls
    return cls

## Forms for single item edition (also 2nd step of creation)
class MiniModelForm(forms.Form):
    _id = forms.IntegerField(widget=forms.HiddenInput, required=False)
    _deleted = forms.BooleanField(required=False)
    _instanciates = forms.ModelChoiceField(queryset=ComponentImplementationClass.objects, required=False, label='composant logique')

    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-lg-2'
    helper.field_class = 'col-lg-9'
    helper.add_input(Submit('submit', 'Submit'))

__model_form_cache = {}
def form_for_model(descr):
    if __model_form_cache.has_key(descr.id):
        return __model_form_cache[descr.id]
    attrs = {}

    # Simple fields
    for field in descr.field_set.order_by('widget_row', 'name').all():
        f = forms.CharField(label=field.short_label, required=field.compulsory)
        attrs[field.name] = f

    # Relations
    for field in descr.target_set.filter(max_cardinality__lte=1).prefetch_related('target__instance_set'):
        f = forms.ModelChoiceField(queryset=field.target.instance_set, label=field.label, required=field.min_cardinality == 1)
        attrs[field.name] = f

    cls = type(str("__" + descr.name.lower() + "_form"), (MiniModelForm,), attrs)
    __model_form_cache[descr.id] = cls
    return cls
