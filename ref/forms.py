# coding: utf-8
'''
    @license: Apache License, Version 2.0
    @copyright: 2007-2013 Marc-Antoine Gouillart
    @author: Marc-Antoine Gouillart
'''

from django import forms
from ref.models import ComponentInstance
from ref.models.models import Environment, ImplementationDescription


class DuplicateFormRelInline(forms.Form):
    old_target = forms.ModelChoiceField(queryset=ComponentInstance.objects.all())
    new_target = forms.ModelChoiceField(queryset=ComponentInstance.objects.none(), empty_label='-- Don\'t remap --', required=False)

    def __init__(self, *args, **kwargs):
        super(DuplicateFormRelInline, self).__init__(*args, **kwargs)
        if self.is_bound:
            self.fields['new_target'].queryset = ComponentInstance.objects.get(pk=self.data[self.prefix + '-old_target']).implementation.instance_set.all()
        if self.initial.has_key('old_target') and self.initial['old_target']:
            self.fields['new_target'].queryset = self.initial['old_target'].implementation.instance_set.all()

class DuplicateForm(forms.Form):
    new_name = forms.CharField(max_length=20)

    instances_to_copy = forms.TypedMultipleChoiceField(choices=(), initial=(), widget=forms.widgets.CheckboxSelectMultiple, coerce=int)

    def __init__(self, *args, **kwargs):
        self.envt = kwargs['envt']
        del kwargs['envt']
        super(DuplicateForm, self).__init__(*args, **kwargs)
        self.fields['instances_to_copy'].choices = [(i.pk, i.__unicode__()) for i in self.envt.component_instances.all()]
        self.fields['instances_to_copy'].initial = [i.pk for i in self.envt.component_instances.all()]

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


