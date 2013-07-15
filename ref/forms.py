# coding: utf-8
'''
    @license: Apache License, Version 2.0
    @copyright: 2007-2013 Marc-Antoine Gouillart
    @author: Marc-Antoine Gouillart
'''

from django import forms
from ref.models import ComponentInstance


class DuplicateFormRelInline(forms.Form):
    old_target = forms.ModelChoiceField(queryset=ComponentInstance.objects.all())
    new_target = forms.ModelChoiceField(queryset=ComponentInstance.objects.none(), empty_label='-- Don\'t remap --', required = False)
    
    def __init__(self, *args, **kwargs):
        super(DuplicateFormRelInline, self).__init__(*args, **kwargs)
        if self.is_bound:
            self.fields['new_target'].queryset = ComponentInstance.objects.get(pk = self.data[self.prefix + '-old_target']).model.get_all_objects_for_this_type()
        if self.initial.has_key('old_target') and self.initial['old_target']:
            self.fields['new_target'].queryset = self.initial['old_target'].model.get_all_objects_for_this_type()

class DuplicateForm(forms.Form):
    new_name = forms.CharField(max_length=20)
    
    instances_to_copy = forms.TypedMultipleChoiceField(choices=(), initial=(), widget=forms.widgets.CheckboxSelectMultiple, coerce=int)
    
    def __init__(self, *args, **kwargs):
        self.envt = kwargs['envt']
        del kwargs['envt']
        super(DuplicateForm, self).__init__(*args, **kwargs)
        self.fields['instances_to_copy'].choices = [(i.pk, i.__unicode__()) for i in self.envt.component_instances.all()]
        self.fields['instances_to_copy'].initial = [i.pk for i in self.envt.component_instances.all()]
