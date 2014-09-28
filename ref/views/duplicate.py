# coding: utf-8

from django.shortcuts import render, redirect
from django import forms
from ref.models.instances import ComponentInstance, Environment
from ref.creation import duplicate_envt
from django.forms.formsets import formset_factory
from django.contrib.auth.decorators import permission_required
from django.db.transaction import atomic


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


#########################################
## Forms
#########################################

class DuplicateFormRelInline(forms.Form):
    old_target = forms.ModelChoiceField(queryset=ComponentInstance.objects.all())
    new_target = forms.ModelChoiceField(queryset=ComponentInstance.objects.none(), empty_label='-- Don\'t remap --', required=False)

    def __init__(self, *args, **kwargs):
        super(DuplicateFormRelInline, self).__init__(*args, **kwargs)
        if self.is_bound:
            self.fields['new_target'].queryset = ComponentInstance.objects.get(pk=self.data[self.prefix + '-old_target']).description.instance_set.all()
        if self.initial.has_key('old_target') and self.initial['old_target']:
            self.fields['new_target'].queryset = self.initial['old_target'].description.instance_set.all()

class DuplicateForm(forms.Form):
    new_name = forms.CharField(max_length=20)

    instances_to_copy = forms.TypedMultipleChoiceField(choices=(), initial=(), widget=forms.widgets.CheckboxSelectMultiple, coerce=int)

    def __init__(self, *args, **kwargs):
        self.envt = kwargs['envt']
        del kwargs['envt']
        super(DuplicateForm, self).__init__(*args, **kwargs)
        self.fields['instances_to_copy'].choices = [(i.pk, i.__unicode__()) for i in self.envt.component_instances.all()]
        self.fields['instances_to_copy'].initial = [i.pk for i in self.envt.component_instances.all()]


