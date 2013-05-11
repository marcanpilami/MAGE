# coding: utf-8

from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.db import transaction
from django.db.models import Max
from django.db.models.aggregates import Count
from django.forms.models import inlineformset_factory
from django.http.response import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required, permission_required

from datetime import datetime, timedelta
import json
from functools import cmp_to_key

from ref.models import Environment, ComponentInstance, EnvironmentType, Convention, Application, LogicalComponent, \
    Project, ConventionCounter
from cpn.tests import TestHelper
from scm.models import InstallableSet, Installation, InstallationMethod, Delivery, LogicalComponentVersion, InstallableItem, ItemDependency, Tag, \
    BackupSet, BackupItem
from scm.install import install_iset_envt
from scm.exceptions import MageScmFailedEnvironmentDependencyCheck
from scm.tests import create_test_is

from forms import DeliveryForm, IDForm, IIForm
from scm.backup import register_backup, register_backup_envt_default_plan
from scm.forms import BackupForm
from ref.conventions import nc_sync_naming_convention
import csv


def envts(request):
    envts = Environment.objects_active.annotate(latest_reconfiguration=Max('component_instances__configurations__created_on')).\
        annotate(configuration_modification_count=Count('component_instances__configurations')).\
        order_by('typology')
    return render(request, 'scm/envts.html', {'envts': envts, })

def all_installs(request, envt_name, limit=15):
    envt = Environment.objects.get(name=envt_name)
    envt.potential_tag = datetime.today().strftime('%Y%M%d') + "_" + envt_name
    dlimit = datetime.now() - timedelta(days=limit)
    installs = Installation.objects.filter(install_date__gt=dlimit).filter(modified_components__component_instance__environments=envt).distinct().order_by('-pk')
    # logical_components = envt.component_instances.all().instanciates.implements;
    logical_components = LogicalComponent.objects.filter(scm_trackable=True, implemented_by__instances__environments=envt)
    
    versions = {}
    for compo in envt.component_instances.filter(instanciates__isnull=False, instanciates__implements__scm_trackable=True):
        lc = logical_components.get(id=compo.instanciates.implements_id)
        versions[lc] = compo.version
        
    return render(request, 'scm/envt_all_installs.html', {'installs': installs, 'envt':envt, 'logical_components':logical_components, 'versions': versions, 'limit': limit })

def delivery_list(request):
    deliveries = Delivery.objects.order_by('pk').select_related('set_content__what_is_installed__logical_component')
    return render(request, 'scm/all_deliveries.html', {'deliveries': deliveries})

def delivery(request, iset_id):
    delivery = InstallableSet.objects.get(pk=iset_id)
    return render(request, 'scm/delivery_detail.html', {'delivery': delivery, 'envts': Environment.objects_active.all().order_by('typology__chronological_order', 'name')})

@permission_required('scm.validate_installableset')
def delivery_validate(request, iset_id):
    delivery = Delivery.objects.get(pk=iset_id)
    delivery.status = 1
    delivery.save()
    return redirect('scm:delivery_detail', iset_id=iset_id)

def delivery_test(request, delivery_id, envt_id_or_name):
    delivery = InstallableSet.objects.get(pk=delivery_id)
    try:
        envt = Environment.objects.get(name=envt_id_or_name)
    except Environment.DoesNotExist:
        envt = Environment.objects.get(pk=int(envt_id_or_name))
        
    try:
        delivery.check_prerequisites(envt.name)
        return render(request, 'scm/delivery_prereqs.html', {'delivery': delivery, 'envt': envt, 'error': None})
    except MageScmFailedEnvironmentDependencyCheck, e:
        return render(request, 'scm/delivery_prereqs.html', {'delivery': delivery, 'envt': envt, 'error': e})

@permission_required('scm.install_installableset')
def delivery_apply_envt(request, delivery_id, envt_id_or_name):    
    delivery = InstallableSet.objects.get(pk=delivery_id)
    try:
        envt = Environment.objects.get(name=envt_id_or_name)
    except Environment.DoesNotExist:
        envt = Environment.objects.get(pk=int(envt_id_or_name))
    
    install_iset_envt(delivery, envt)
    return redirect('scm:envtinstallhist', envt_name=envt.name)

def lc_versions_per_environment(request):
    Installation.objects.filter()
    envts = Environment.objects_active.all().order_by('typology__chronological_order', 'name')
    res = {}
    for lc in LogicalComponent.objects.filter(scm_trackable=True):
        lc_list = []
        for envt in envts:
            compo_instances = envt.component_instances.filter(instanciates__implements__id=lc.id)
            versions = [i.version_object_safe for i in compo_instances]
            if len(versions) > 0:
                lc_list.append(max(versions, key=cmp_to_key(LogicalComponentVersion.compare)))
            else:
                lc_list.append(None)
        res[lc] = lc_list
    
    return render(request, 'scm/lc_installs_envt.html', {'res': res, 'envts': envts})


@login_required
@permission_required('scm.add_delivery')
def delivery_edit(request, iset_id=None):
    ## Out model formset, linked to its parent
    InstallableItemFormSet = inlineformset_factory(Delivery, InstallableItem, form=IIForm, extra=1)
    
    ## Already bound?
    instance = None
    if iset_id is not None:
        instance = InstallableSet.objects.get(pk=iset_id)
        ## A dev can only modify an unvalidated delivery
        if not request.user.has_perm('scm.modify_delivery') and instance.status != 3:
            return redirect(reverse('login') + '?next=%s' % request.path)
    
    ## Helper for javascript
    lc_im = {}
    for lc in LogicalComponent.objects.all():
        r = []
        for cic in lc.implemented_by.all():
            r.extend([i.id for i in cic.installation_methods.all()])
        lc_im[lc.id] = r
    
    ## Bind form
    if request.method == 'POST':
        form = DeliveryForm(request.POST, instance=instance)  # A form bound to the POST data
        iiformset = InstallableItemFormSet(request.POST, prefix='iis', instance=form.instance)
        
        if form.is_valid() and iiformset.is_valid():  # All validation rules pass
            instance = form.save()
        
            iiformset = InstallableItemFormSet(request.POST, prefix='iis', instance=instance)
            if iiformset.is_valid():
                iiformset.save()
                
                ## Done
                return redirect('scm:delivery_edit_dep', iset_id=instance.id)
    else:
        form = DeliveryForm(instance=instance)
        iiformset = InstallableItemFormSet(prefix='iis', instance=instance)

    return render(request, 'scm/delivery_edit.html', {
        'form': form,
        'iisf' : iiformset,
        'lc_im' : lc_im,
    })


@login_required
@permission_required('scm.add_delivery')
def delivery_edit_dep(request, iset_id):
    iset = InstallableSet.objects.get(pk=iset_id)
    ItemDependencyFormSet = inlineformset_factory(InstallableItem, ItemDependency, form=IDForm, extra=1)
    fss = {}
    
    ## A dev can only modify an unvalidated delivery
    if not request.user.has_perm('scm.modify_delivery') and iset.status != 3:
        return redirect(reverse('login') + '?next=%s' % request.path)

    if request.method == 'POST':  # If the form has been submitted...
        # Bound formsets to POST data
        valid = True
        for ii in iset.set_content.all():
            fss[ii] = ItemDependencyFormSet(request.POST, request.FILES, instance=ii, prefix='ii%s' % ii.pk)
            valid = valid and fss[ii].is_valid()
            
        if valid:
            for fs in fss.values():
                fs.save()
            return redirect('scm:delivery_detail', iset_id=iset_id)
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

@permission_required('scm.add_tag')
def tag_create(request, envt_name, tag_name):
    e = Environment.objects.get(name=envt_name)
    
    tt = Tag.objects.filter(name__contains=tag_name).count()
    if tt > 0:
        tag_name = "%s_%s " % (tag_name, tt)
    
    t = Tag(name=tag_name, from_envt=e)
    t.save()
    
    for instance in e.component_instances.all():
        v = instance.version_object_safe
        if v is not None:
            t.versions.add(v)
            
    return redirect('scm:tag_detail', tag_id=t.id)
 
def tag_detail(request, tag_id):
    t = Tag.objects.get(pk=tag_id)
    return render(request, 'scm/tag_detail.html', {'tag': t})
 
def tag_list(request):
    return render(request, 'scm/tag_list.html', {'tags': Tag.objects.all()}) 

def backup_list(request):
    return render(request, 'scm/backup_list.html', {'backups': BackupSet.objects.filter(removed__isnull=True)})

def backup_detail(request, bck_id):
    return render(request, 'scm/backup_detail.html', {'bck': BackupSet.objects.get(pk=bck_id)})

@permission_required('scm.add_backupset')
def backup_envt(request, envt_name):
    b = register_backup_envt_default_plan(envt_name, datetime.now())
    return redirect('scm:backup_detail', bck_id=b.id)

@permission_required('scm.add_backupset')
def backup_envt_manual(request, envt_name):
    e = Environment.objects.get(name=envt_name)
    
    if request.method == 'POST':  # If the form has been submitted...
        f = BackupForm(request.POST, envt=e)
        
        if f.is_valid():
            instances = ComponentInstance.objects.filter(pk__in=f.cleaned_data['instances'])
            bs = register_backup(e, f.cleaned_data['date'], "MANUAL - %s" % f.cleaned_data['description'], *instances)
            return redirect('scm:backup_detail', bck_id=bs.id)
    else:
        f = BackupForm(envt=e)
    
    return render(request, 'scm/backup_create_manual.html', {'form': f, 'envt': e})

def iset_content_csv(request, iset):
    if isinstance(iset, unicode):
        try:
            i = int(iset)
            iset = InstallableSet.objects.get(pk=i)
        except:
            iset = InstallableSet.objects.get(name=iset)
    
    response = HttpResponse(content_type='text/csv')
    wr = csv.DictWriter(response, fieldnames=('id', 'target', 'target_id', 'version', 'is_full', 'data_loss'), restval="", extrasaction='ignore', dialect='excel', delimiter=";")    
    wr.writeheader()
    
    for ii in iset.set_content.all():
        wr.writerow({'id': ii.id, 'target': ii.what_is_installed.logical_component.name, 'target_id': ii.what_is_installed.logical_component.id, 'version': ii.what_is_installed.version, 'is_full': ii.is_full, 'data_loss': ii.data_loss})
    
    return response

def iset_id(request, iset_name):
    res = 0
    try:
        iset = InstallableSet.objects.get(name=iset_name)
        res = iset.id
    except InstallableSet.DoesNotExist:
        res = 0
    
    response = HttpResponse(content_type='text/text')
    response.write(res)
    return response

def reset():
    for ta in Tag.objects.all():
        ta.delete()
    for bi in BackupItem.objects.all():
        bi.delete()
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
    for nc in Convention.objects.all():
        nc.delete()
    for cc in ConventionCounter.objects.all():
        cc.delete()
    for ap in Application.objects.all():
        ap.delete()
    for pr in Project.objects.all():
        pr.delete()
    
@transaction.commit_on_success
def demo_internal(request):
    reset()
    
    is_list = create_test_is()
    default = Convention(name='default convention')
    default.save()
    nc_sync_naming_convention(default)
    
    ref = TestHelper()
    install_iset_envt(is_list[0], ref.envt_prd1)
    install_iset_envt(is_list[1], ref.envt_prd1)
    install_iset_envt(is_list[2], ref.envt_prd1)
    install_iset_envt(is_list[3], ref.envt_prd1)
    install_iset_envt(is_list[5], ref.envt_prd1)
    
    bs1 = register_backup('PRD1', datetime.now(), "no descr", *ref.envt_prd1.component_instances.all())
    register_backup_envt_default_plan('PRD1', datetime.now())
    install_iset_envt(bs1, ref.envt_tec2)
    
    return HttpResponseRedirect(reverse('welcome'))
    
@transaction.commit_on_success
def demo(request):
    reset()
    default = Convention(name='default convention')
    default.save()
    nc_sync_naming_convention(default)
    
    from MAGE.settings import INSTALLED_APPS
    for app in [ i for i in INSTALLED_APPS if not i.startswith('django.')]:
        try:
            demo_data = getattr(__import__(app + '.models', fromlist=['demo_data']), 'demo_data')
        except:
            continue
        
        demo_data()
        
    return HttpResponseRedirect(reverse('welcome'))
