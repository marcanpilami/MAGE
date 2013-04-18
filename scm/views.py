# coding: utf-8

from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.db import transaction
from django.db.models import Max
from django.db.models.aggregates import Count
from django import forms
from django.forms import ModelForm
from django.forms.models import inlineformset_factory, modelformset_factory
from django.http.response import HttpResponseRedirect, HttpResponse

import re
from datetime import datetime, timedelta
import json

from ref.models import Environment, ComponentInstance, EnvironmentType, LogicalComponent, NamingConvention, Application
from cpn.tests import TestHelper
from scm.models import InstallableSet, InstallableItem, Installation, Delivery, InstallationMethod, LogicalComponentVersion, \
    ItemDependency
from scm.install import install_iset_envt
from scm.exceptions import MageScmFailedEnvironmentDependencyCheck
from scm.tests import create_test_is
from django.forms.formsets import formset_factory

def envts(request):
    envts = Environment.objects.annotate(latest_reconfiguration=Max('component_instances__configurations__created_on')).\
        annotate(configuration_modification_count=Count('component_instances__configurations')).\
        order_by('typology')
    return render(request, 'scm/envts.html', {'envts': envts, })

def all_installs(request, envt_name, limit=15):
    envt = Environment.objects.get(name=envt_name)
    dlimit = datetime.now() - timedelta(days=limit)
    installs = Installation.objects.filter(install_date__gt=dlimit).filter(modified_components__component_instance__environments=envt).distinct().order_by('-pk')
    # logical_components = envt.component_instances.all().instanciates.implements;
    logical_components = LogicalComponent.objects.filter(implemented_by__instances__environments=envt)
    
    versions = {}
    for compo in envt.component_instances.filter(instanciates__isnull=False):
        lc = logical_components.get(id=compo.instanciates.implements_id)
        versions[lc] = compo.version
        
    return render(request, 'scm/envt_all_installs.html', {'installs': installs, 'envt':envt, 'logical_components':logical_components, 'versions': versions, 'limit': limit })

def delivery_list(request):
    deliveries = Delivery.objects.order_by('pk').select_related('set_content__what_is_installed__logical_component')
    return render(request, 'scm/all_deliveries.html', {'deliveries': deliveries})

def delivery(request, delivery_id):
    delivery = Delivery.objects.get(pk=delivery_id)
    return render(request, 'scm/delivery_detail.html', {'delivery': delivery, 'envts': Environment.objects.all()})

def delivery_test(request, delivery_id, envt_id):
    delivery = Delivery.objects.get(pk=delivery_id)
    envt = Environment.objects.get(pk=envt_id)
    try:
        delivery.check_prerequisites(envt.name)
        return render(request, 'scm/delivery_prereqs.html', {'delivery': delivery, 'envt': envt, 'error': None})
    except MageScmFailedEnvironmentDependencyCheck, e:
        return render(request, 'scm/delivery_prereqs.html', {'delivery': delivery, 'envt': envt, 'error': e})
 
def delivery_apply_envt(request, delivery_id, envt_id):    
    delivery = Delivery.objects.get(pk=delivery_id)
    envt = Environment.objects.get(pk=envt_id)   
    
    install_iset_envt(delivery, envt)
    return redirect('scm:envtinstallhist', envt_name=envt.name)


class DeliveryForm(ModelForm):
    def clean_ticket_list(self):
        data = self.cleaned_data['ticket_list']
        if len(data) == 0:
            return data
        p = re.compile('(\d+,?)+$')
        if p.match(data) is None:
            raise forms.ValidationError("This field must be a comma-separated list of integers")
        return data
    
    class Meta:
        model = Delivery
        exclude = ['removed', ]

class IIForm(ModelForm):
    target = forms.ModelChoiceField(queryset=LogicalComponent.objects.filter(scm_trackable=True, implemented_by__installation_methods__isnull=False).distinct(), label='Composant livré')
    version = forms.CharField(label='Version livrée')
    
    def save(self, commit=True):
        print self.__dict__
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
   
    class Meta:
        model = InstallableItem
        #exclude = ['what_is_installed',]
        fields = ('target', 'version', 'how_to_install', 'is_full', 'data_loss',)#'what_is_installed')


def delivery_edit(request, iset_id=None):
    ## Out model formset, linked to its parent
    InstallableItemFormSet = inlineformset_factory(Delivery, InstallableItem, form=IIForm, extra=1)
    
    ## Already bound?
    instance = None
    if iset_id is not None:
        instance = InstallableSet.objects.get(pk=iset_id)
    
    ## Helper for javascript
    lc_im = {}
    for lc in LogicalComponent.objects.all():
        r = []
        for cic in lc.implemented_by.all():
            r.extend([i.id for i in cic.installation_methods.all()])
        lc_im[lc.id] = r
    
    ## Bind form
    if request.method == 'POST': # If the form has been submitted...
        form = DeliveryForm(request.POST) # A form bound to the POST data
        iiformset = InstallableItemFormSet(request.POST, request.FILES, prefix='iis', instance=form.instance)
        
        if form.is_valid() and iiformset.is_valid(): # All validation rules pass
            instance = form.save()
        
            iiformset = InstallableItemFormSet(request.POST, request.FILES, prefix='iis', instance=instance)
            if iiformset.is_valid():
                iiformset.save()
                
                ## Done
                return redirect('scm:delivery_edit_dep', iset_id=instance.id)
    else:
        form = DeliveryForm(instance=instance) # An unbound form
        iiformset = InstallableItemFormSet(prefix='iis', instance=instance)

    return render(request, 'scm/delivery_edit.html', {
        'form': form,
        'iisf' : iiformset,
        'lc_im' : lc_im,
    })

class IDForm(ModelForm):   
    target = forms.ModelChoiceField(queryset=LogicalComponent.objects.filter(scm_trackable=True, implemented_by__installation_methods__isnull=False).distinct(), label='dépend de ', required=False)
    class Meta:
        model = ItemDependency
        fields = ('target', 'depends_on_version', 'operator',)

def delivery_edit_dep(request, iset_id):
    iset = InstallableSet.objects.get(pk=iset_id)
    ItemDependencyFormSet = inlineformset_factory(InstallableItem, ItemDependency, form=IDForm, extra=1)
    fss = {}
    
    if request.method == 'POST': # If the form has been submitted...
        # Bound formsets to POST data
        valid = True
        for ii in iset.set_content.all():
            fss[ii] = ItemDependencyFormSet(request.POST, request.FILES, instance=ii, prefix='ii%s' % ii.pk)
            valid = valid and fss[ii].is_valid()
            
        if valid:
            for fs in fss.values():
                fs.save()
            return redirect('scm:delivery_detail', delivery_id=iset_id)
    else:
        for ii in iset.set_content.all():
            fss[ii] = ItemDependencyFormSet(instance=ii, prefix='ii%s' % ii.pk)
        
    return render(request, 'scm/delivery_edit_dep.html', {
        'fss' : fss,
        'iset' : iset,
    })

def get_lc_versions(request, lc_id):
    lc = LogicalComponent.objects.get(pk=lc_id)
    res = []
    for v in lc.versions.all():
        res.append((v.id, v.version))
    
    return HttpResponse(json.dumps(res))
    
@transaction.commit_on_success
def demo(request):
    for IS in InstallableSet.objects.all():
        IS.delete()
    for ii in InstallableItem.objects.all():
        ii.delete()
    for ii in InstallationMethod.objects.all():
        ii.delete()
    for envt in Environment.objects.all():
        envt.delete()
    for ci in ComponentInstance.objects.all():
        ci.delete()
    for et in EnvironmentType.objects.all():
        et.delete()
    for lc in LogicalComponent.objects.all():
        lc.delete()
    for nc in NamingConvention.objects.all():
        nc.delete()
    for ap in Application.objects.all():
        ap.delete()
    is_list = create_test_is()
    
    ref = TestHelper()
    install_iset_envt(is_list[0], ref.envt_prd1)
    install_iset_envt(is_list[1], ref.envt_prd1)
    install_iset_envt(is_list[2], ref.envt_prd1)
    install_iset_envt(is_list[3], ref.envt_prd1)
    install_iset_envt(is_list[5], ref.envt_prd1)
    
    return HttpResponseRedirect(reverse('welcome'))
    
