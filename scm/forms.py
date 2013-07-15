# coding: utf-8

from django import forms
from django.forms import ModelForm

import re

from scm.models import Delivery, LogicalComponentVersion, InstallableItem, ItemDependency, InstallationMethod
from ref.models import LogicalComponent
from ref.widgets import ClearableFileInputPretty


class DeliveryForm(ModelForm):
    def clean_ticket_list(self):
        data = self.cleaned_data['ticket_list']
        if len(data) == 0:
            return data
        p = re.compile('([\da-zA-Z_-]+,?)+$')
        if p.match(data) is None:
            raise forms.ValidationError("This field must be a comma-separated list of ticket ID (letters and integers)")
        return data
    
    class Meta:
        model = Delivery
        exclude = ['removed', 'status',]
        widgets = { 'datafile': ClearableFileInputPretty}

class IIForm(ModelForm):
    target = forms.ModelChoiceField(queryset=LogicalComponent.objects.filter(scm_trackable=True, implemented_by__installation_methods__isnull=False).order_by('name').distinct(), label='Composant livré')
    version = forms.CharField(label='Version livrée')
    
    def save(self, commit=True):
        logicalcompo = self.cleaned_data['target']
        version = self.cleaned_data['version']
        v = LogicalComponentVersion.objects.get_or_create(logical_component=logicalcompo, version=version)[0]
        v.save()
        self.instance.what_is_installed = v
        o = super(IIForm, self).save(commit)
        return o
    
    def clean_how_to_install(self):
        data = self.cleaned_data['how_to_install']
        if len(data) == 0:
            raise forms.ValidationError("At least one technical target is required")
        return data
    
    def clean_datafile(self):
        dfile = self.cleaned_data['datafile']
        methods = self.cleaned_data['how_to_install']
        if len(methods) == 0:
            return dfile
        for method in methods:
            if method.checkers.count() > 0 and (dfile is None or dfile == False):
                raise forms.ValidationError('A datafile is required')
        if dfile == False: ## Cleared file
            return dfile
        
        for method in methods:
            method.check_package(dfile)
        return dfile
        
    def clean(self):
        cleaned_data = super(IIForm, self).clean()
        
        ## Check how_to_install consistency
        if self.cleaned_data.has_key('target') and self.cleaned_data.has_key('how_to_install'):
            logicalcompo = self.cleaned_data['target']
            htis = self.cleaned_data['how_to_install']
            for hti in htis:
                if not logicalcompo in [i.implements for i in hti.method_compatible_with.all()]:
                    raise forms.ValidationError("Inconsistent choice - that method is not compatible with this target")
            
        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        super(IIForm, self).__init__(*args, **kwargs)
        self.fields['how_to_install'].queryset = InstallationMethod.objects.filter(restoration_only = False)
        
        if self.instance != None and self.instance.pk is not None:
            self.initial['target'] = self.instance.what_is_installed.logical_component.pk
            self.initial['version'] = self.instance.what_is_installed.version
   
    class Meta:
        model = InstallableItem
        # exclude = ['what_is_installed',]
        fields = ('target', 'version', 'how_to_install', 'is_full', 'data_loss', 'datafile')  # 'what_is_installed')
        widgets = { 'datafile': ClearableFileInputPretty}


class IDForm(ModelForm):   
    target = forms.ModelChoiceField(queryset=LogicalComponent.objects.filter(scm_trackable=True, implemented_by__installation_methods__isnull=False).distinct(), label='dépend de ', required=False)
    class Meta:
        model = ItemDependency
        fields = ('target', 'depends_on_version', 'operator',)


class BackupForm(forms.Form):
    description = forms.CharField(max_length=90, required=False)
    date = forms.DateTimeField(input_formats=['%d/%m/%Y %H:%M', ])
    instances = forms.TypedMultipleChoiceField(choices=(), widget=forms.widgets.CheckboxSelectMultiple, coerce=int)

    def __init__(self, *args, **kwargs):
        self.envt = kwargs['envt']
        del kwargs['envt']
        super(BackupForm, self).__init__(*args, **kwargs)
        self.fields['instances'].choices = [(i.pk, i.__unicode__()) for i in self.envt.component_instances.all()]
    
