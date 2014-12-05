# coding: utf-8

from django.db.transaction import atomic
from django import forms
from ref.models import ComponentImplementationClass, ComponentInstanceRelation, ComponentInstanceField, ComponentInstance, Environment, ImplementationDescription
from django.forms.models import ModelChoiceIterator, ModelForm, \
    modelform_factory, modelformset_factory
from django.shortcuts import render_to_response, redirect
from django.forms.formsets import formset_factory
from functools import wraps
from _functools import partial
from django.contrib.auth.decorators import permission_required
from django.forms.widgets import Textarea, NumberInput, Select, \
    CheckboxSelectMultiple
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.encoding import force_text
from django.utils.functional import curry


@atomic
def edit_comp(request, instance_id=None, description_id=None):
    """ still used ?"""
    instance = None

    if request.POST:
        cd = MiniModelForm(request.POST)
        if cd.is_valid() and cd.cleaned_data['_id']:
            instance = ComponentInstance.objects.get(pk=cd.cleaned_data['_id'])

    if not request.POST and instance_id:
        instance = ComponentInstance.objects.get(pk=instance_id)

    form = form_for_model(instance.description if instance else ImplementationDescription.objects.get(pk=description_id))(request.POST or (instance.proxy if instance else None))

    if request.POST and form.is_valid():
        ## Save fields
        ci = None
        if form.cleaned_data.has_key('_id'):
            cid = form.cleaned_data.pop('_id')
            if cid:
                ci = ComponentInstance.objects.get(pk=cid).proxy
        if not ci:
            impl_id = form.cleaned_data['_descr_id'] or description_id
            descr = ImplementationDescription.class_for_id(impl_id)
            ci = descr()
        form.cleaned_data.pop('_descr_id')

        for key, value in form.cleaned_data.iteritems():
            setattr(ci, key, value)

        ci.save()

        ## Done
        return redirect("ref:instance_edit", instance_id=ci._instance.id)

    return render_to_response("ref/instance_edit.html", {'form': form})

@atomic
@permission_required('ref.scm_addcomponentinstance')
def envt_instances(request, envt_id=1):
    e = Environment.objects.get(pk=envt_id)
    # ModelChoiceIterator optim - https://code.djangoproject.com/ticket/22841
    cics = ComponentImplementationClass.objects.all()
    #iterator = ModelChoiceIterator(forms.ModelChoiceField(None, required=False, empty_label='kkkkkk'))
    #choices = [iterator.choice(obj) for obj in ComponentImplementationClass.objects.all()]
    #choices.append(iterator.choice(""))

    ffs = {}
    typ_items = {}
    for instance in e.component_instances.prefetch_related('description__field_set').prefetch_related('description__target_set').\
            prefetch_related('field_set__field', 'rel_target_set').\
            prefetch_related('rel_target_set__field').\
            order_by('description__tag'):
        # for each instance, crate a dict containing all the values
        di = {'_id': instance.pk, '__descr_id': instance.description_id, '_deleted': instance.deleted, '_instanciates' : instance.instanciates_id}

        for field_instance in instance.field_set.all():
            di[field_instance.field.name] = field_instance.value

        for field_instance in instance.rel_target_set.all():
            di[field_instance.field.name] = field_instance.target_id

        # add the dict to a list of instances with the same description
        if typ_items.has_key(instance.description):
            typ_items[instance.description].append(di)
        else:
            typ_items[instance.description] = [di, ]

    for typ, listi in typ_items.iteritems():
        cls = form_for_model(typ)
        InstanceFormSet = formset_factory(wraps(cls)(partial(cls, cics=cics)) , extra=0)
        ffs[typ] = InstanceFormSet(request.POST or None, initial=listi, prefix=typ.name)

    if request.POST:
        valid = True
        for typ, formset in ffs.iteritems():
            if not formset.is_valid():
                valid = False
                break

        if valid:
            for typ, formset in ffs.iteritems():
                if formset.has_changed():
                    for form in formset:
                        if form.has_changed():
                            instance_id = form.cleaned_data['_id'] if form.cleaned_data.has_key('_id') else None
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


    return render_to_response("ref/instance_envt.html", {'fss': ffs, 'envt': e})


#########################################
## Forms
#########################################

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

__model_form_cache = {}
def form_for_model(descr):
    if __model_form_cache.has_key(descr.id):
        return __model_form_cache[descr.id]
    attrs = {}

    # Simple fields
    for field in descr.field_set.all():
        f = forms.CharField(label=field.short_label, required=field.compulsory)
        attrs[field.name] = f

    # Relations
    for field in descr.target_set.filter(max_cardinality__lte=1).prefetch_related('target__instance_set'):
        f = forms.ModelChoiceField(queryset=field.target.instance_set, label=field.label, required=field.min_cardinality == 1)
        attrs[field.name] = f

    # deleted checkbox is last
    attrs['_deleted'] = forms.BooleanField(required=False, label="effacé")

    cls = type(str("__" + descr.name.lower() + "_form"), (MiniModelForm,), attrs)
    __model_form_cache[descr.id] = cls
    return cls


class InstanceForm(forms.Form):
    def __init__(self, *args, **kwargs):
        descr = kwargs.pop('description')
        super(InstanceForm, self).__init__(*args, **kwargs)

        for field in descr.field_set.all():
            self.fields[field.name] = forms.CharField(label=field.label)


#####################################################
## Debug form for changing types
#####################################################

class HorizontalCSM(CheckboxSelectMultiple.renderer):
    def render(self):
        id_ = self.attrs.get('id', None)
        start_tag = format_html('<div id="{0}">', id_) if id_ else '<div>'
        output = [start_tag]
        for widget in self:
            output.append(format_html(u'<span>{0}</span>', force_text(widget)))
        output.append('</span>')
        return mark_safe('\n'.join(output))

class CIForm(ModelForm):
    def __init__(self, descriptions, envts, **kwargs):
        super(CIForm, self).__init__(**kwargs)
        iterator = ModelChoiceIterator(self.fields['description'])
        choices = [iterator.choice(obj) for obj in descriptions]
        choices.append(("", self.fields['description'].empty_label))
        self.fields['description'].choices = choices

        iterator = ModelChoiceIterator(self.fields['environments'])
        choices = [iterator.choice(obj) for obj in envts]
        self.fields['environments'].choices = choices


    class Meta:
        model = ComponentInstance
        fields = ['description', 'environments', 'deleted']
        widgets = {'environments' : CheckboxSelectMultiple(renderer=HorizontalCSM)}

def edit_all_comps_meta(request):
    CIFormSet = modelformset_factory(ComponentInstance, form=CIForm, extra=0)
    CIFormSet.form = staticmethod(curry(CIForm, descriptions=ImplementationDescription.objects.all(),
                                        envts=Environment.objects.all()))

    if request.method == 'POST':
        formset = CIFormSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
            return redirect("ref:instance_all")
    else:
        formset = CIFormSet(queryset=ComponentInstance.objects.all().select_related('description').prefetch_related('environments'))

    return render_to_response("ref/instance_all.html", {"formset": formset, })
