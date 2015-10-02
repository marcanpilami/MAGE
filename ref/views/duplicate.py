# coding: utf-8
from django.db.models.query import Prefetch
from django.shortcuts import render, redirect
from django import forms
from django.forms.formsets import formset_factory
from django.contrib.auth.decorators import permission_required
from django.db.transaction import atomic
from ref.models.ou import folder_permission_required
from ref.models.classifier import AdministrationUnit

from ref.models.instances import ComponentInstance, Environment
from ref.creation import duplicate_envt


@folder_permission_required('read_envt')
@folder_permission_required('read_envt_sensible')
@atomic
def envt_duplicate_name(request, folder_id, envt_name):
    e = Environment.objects.prefetch_related(
        Prefetch('component_instances',
                 queryset=ComponentInstance.objects.
                 select_related('description').prefetch_related('relationships'))).get(name=envt_name)
    formset_class = formset_factory(DuplicateFormRelInline, extra=0)
    target_folders = [f for f in AdministrationUnit.objects.all() if request.user.has_perm('add_envt')]

    if request.method == 'POST':  # If the form has been submitted...
        form = DuplicateForm(request.POST, envt=e, scope=target_folders)  # A form bound to the POST data
        fs = formset_class(request.POST)

        if form.is_valid() and fs.is_valid():  # All validation rules pass
            remaps = {}
            for f in fs.cleaned_data:
                if f['new_target']:
                    remaps[f['old_target'].id] = f['new_target'].id

            if not request.user.has_perm('add_envt', form.cleaned_data['new_folder']):
                raise Exception('user has no add_envt permission on tagret folder')

            e1 = duplicate_envt(envt_name, form.cleaned_data['new_name'], form.cleaned_data['new_description'],
                                AdministrationUnit.objects.get(pk=int(form.cleaned_data['new_folder'])), remaps,
                                *ComponentInstance.objects.filter(pk__in=form.cleaned_data['instances_to_copy']))
            return redirect('admin:ref_environment_change', e1.id)
    else:
        form = DuplicateForm(envt=e, scope=target_folders)  # An unbound form

        # Create a formset for each external relation
        internal_pks = [i.pk for i in e.component_instances.all()]
        ext = {}
        initial_rel = []
        for cpn in e.component_instances.all():
            for rel in cpn.relationships.all():
                if rel.id not in internal_pks:
                    ext[rel] = None
        for rel in ext.keys():
            initial_rel.append({'old_target': rel, 'new_target': None})
        fs = formset_class(initial=initial_rel)

    return render(request, 'ref/envt_duplicate.html', {'form': form, 'envt': e, 'fs': fs})


#########################################
# Forms
#########################################

class DuplicateFormRelInline(forms.Form):
    old_target = forms.ModelChoiceField(queryset=ComponentInstance.objects.select_related('description').all())
    new_target = forms.ModelChoiceField(queryset=ComponentInstance.objects.none(),
                                        empty_label='-- Don\'t remap --',
                                        required=False)

    def __init__(self, *args, **kwargs):
        super(DuplicateFormRelInline, self).__init__(*args, **kwargs)
        if self.is_bound:
            self.fields['new_target'].queryset = ComponentInstance.objects.get(
                pk=self.data[self.prefix + '-old_target']).description.instance_set.all()
        if 'old_target' in self.initial and self.initial['old_target']:
            self.fields['new_target'].queryset = self.initial['old_target'].description.instance_set.all()


class DuplicateForm(forms.Form):
    new_name = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))
    new_description = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    new_folder = forms.ChoiceField(choices=(), initial=(),
                                   widget=forms.widgets.Select(attrs={'class': 'form-control'}))

    instances_to_copy = forms.TypedMultipleChoiceField(choices=(), initial=(),
                                                       widget=forms.widgets.CheckboxSelectMultiple, coerce=int)

    def __init__(self, *args, **kwargs):
        self.envt = kwargs['envt']
        del kwargs['envt']
        self.scope = kwargs['scope']
        del kwargs['scope']
        super(DuplicateForm, self).__init__(*args, **kwargs)
        self.fields['instances_to_copy'].choices = sorted(
            [(i.pk, "%s%s - %s" % (i.description.description[0].capitalize(),i.description.description[1:],
                                   i.__unicode__())) for i in self.envt.component_instances.all()], key=lambda x: x[1])
        self.fields['instances_to_copy'].initial = [i.pk for i in self.envt.component_instances.all()]
        self.fields['new_folder'].choices = [(i.pk, i.name) for i in self.scope if i.name != 'root']
        self.fields['new_folder'].initial = self.envt.project_id
