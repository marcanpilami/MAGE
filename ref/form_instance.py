# coding: utf-8

'''
Created on 13 août 2014

@author: Marc-Antoine
'''
from django import forms
from ref.models.models import ComponentImplementationClass
from django.forms.models import ModelChoiceIterator

class InstanceForm(forms.Form):
    def __init__(self, *args, **kwargs):
        descr = kwargs.pop('description')
        super(InstanceForm, self).__init__(*args, **kwargs)

        for field in descr.field_set.all():
            self.fields[field.name] = forms.CharField(label=field.label)

class MiniModelForm(forms.Form):
    def __init__(self, cics, **kwargs):
        super(MiniModelForm, self).__init__(**kwargs)
        iterator = ModelChoiceIterator(self.fields['_instanciates'])
        choices = [iterator.choice(obj) for obj in cics]
        choices.append(("", self.fields['_instanciates'].empty_label))
        self.fields['_instanciates'].choices = choices

    _id = forms.IntegerField(widget=forms.HiddenInput, required=False)
    _descr_id = forms.IntegerField(widget=forms.HiddenInput, required=False)
    _deleted = forms.BooleanField(required=False)
    _instanciates = forms.ModelChoiceField(queryset=ComponentImplementationClass.objects, required=False, label='composant logique')

__model_form_cache = {}

def form_for_model(descr):
    if __model_form_cache.has_key(descr.id):
        return __model_form_cache[descr.id]

    attrs = {}

    # common fields


    # Simple fields
    for field in descr.field_set.all():
        f = forms.CharField(label=field.short_label, required=field.compulsory)
        attrs[field.name] = f

    # Relations
    for field in descr.target_set.filter(max_cardinality__lte=1).prefetch_related('target__instance_set'):
        f = forms.ModelChoiceField(queryset=field.target.instance_set, label=field.label, required=field.min_cardinality == 1)
        attrs[field.name] = f

    cls = type(str("__" + descr.name.lower() + "_form"), (MiniModelForm,), attrs)
    __model_form_cache[descr.id] = cls
    return cls

