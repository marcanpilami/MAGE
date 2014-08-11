# coding: utf-8
'''
    @license: Apache License, Version 2.0
    @copyright: 2007-2013 Marc-Antoine Gouillart
    @author: Marc-Antoine Gouillart
'''

## Python imports
from datetime import timedelta
import json
from functools import cmp_to_key
import csv
import importlib

## Django imports
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.db import transaction
from django.db.models import Max
from django.db.models.aggregates import Count
from django.forms.models import inlineformset_factory
from django.http.response import HttpResponseRedirect, HttpResponse,\
    HttpResponseBadRequest
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.timezone import now
from django.views.decorators.cache import cache_control

## MAGE imports
from ref.models import Environment, ComponentInstance, EnvironmentType, Convention, Application, LogicalComponent, \
    Project, ConventionCounter
from ref.conventions import nc_sync_naming_convention
from ref.old_cpn_tests import TestHelper
from scm.models import InstallableSet, Installation, InstallationMethod, Delivery, LogicalComponentVersion, InstallableItem, ItemDependency, Tag, \
    BackupSet, BackupItem
from scm.install import install_iset_envt, install_ii_single_target_envt
from scm.exceptions import MageScmFailedEnvironmentDependencyCheck
from scm.tests import create_test_is
from forms import DeliveryForm, IDForm, IIForm
from scm.backup import register_backup, register_backup_envt_default_plan
from scm.forms import BackupForm
from ref.models.parameters import getParam
from django.utils.datastructures import SortedDict
from django.utils.datetime_safe import datetime
from django.utils import timezone


def envts(request):
    envts = Environment.objects_active.annotate(latest_reconfiguration=Max('component_instances__configurations__created_on')).\
        annotate(configuration_modification_count=Count('component_instances__configurations')).\
        order_by('typology')
    return render(request, 'scm/envts.html', {'envts': envts, })

def all_installs(request, envt_name, limit):
    '''All installs on a given environment'''
    if isinstance(limit, unicode):
        limit = int(limit) 
    envt = Environment.objects.get(name=envt_name)
    envt.potential_tag = now().strftime('%Y%M%d') + "_" + envt_name
    dlimit = now() - timedelta(days=limit)
    installs = Installation.objects.filter(install_date__gt=dlimit).filter(modified_components__component_instance__environments=envt).distinct().order_by('-pk')
    # logical_components = envt.component_instances.all().instanciates.implements;
    logical_components = LogicalComponent.objects.filter(scm_trackable=True, active=True, implemented_by__instances__environments=envt).distinct()
    
    versions = {}
    for compo in envt.component_instances.filter(deleted = False, instanciates__isnull=False, instanciates__implements__scm_trackable=True):
        try:
            lc = logical_components.get(id=compo.instanciates.implements_id)
        except LogicalComponent.DoesNotExist:
            continue
        if versions.has_key(lc):
            versions[lc]  += (compo.version,)
        else:
            versions[lc]  =(compo.version,)
    
    return render(request, 'scm/envt_all_installs.html', {'installs': installs, 'envt':envt, 'logical_components':logical_components, 'versions': versions, 'limit': limit })

@cache_control(must_revalidate=True, max_age=600)
def delivery_list(request):
    deliveries = Delivery.objects.order_by('set_date').reverse().select_related('set_content__what_is_installed__logical_component')
    lis = LogicalComponent.objects.filter(scm_trackable = True, active = True).order_by('pk').select_related('versions')
    return render(request, 'scm/all_deliveries.html', {'deliveries': deliveries, 'lis': lis})

@cache_control(no_cache=True)
def delivery(request, iset_id):
    delivery = InstallableSet.objects.get(pk=iset_id)
    return render(request, 'scm/delivery_detail.html', {'delivery': delivery, 'envts': Environment.objects_active.filter(managed = True).order_by('typology__chronological_order', 'name')})

@permission_required('scm.validate_installableset')
def delivery_validate(request, iset_id):
    delivery = Delivery.objects.get(pk=iset_id)
    delivery.status = 1
    delivery.save()
    return redirect('scm:delivery_detail', iset_id=iset_id)

@cache_control(no_cache=True)
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

def delivery_test_script(request, delivery_id, envt_id_or_name):
    delivery = InstallableSet.objects.get(pk=delivery_id)
    try:
        envt = Environment.objects.get(name=envt_id_or_name)
    except Environment.DoesNotExist:
        envt = Environment.objects.get(pk=int(envt_id_or_name))
        
    try:
        delivery.check_prerequisites(envt.name)
        return HttpResponse("<html><body>OK</body></html>")
    except MageScmFailedEnvironmentDependencyCheck, e:
        return HttpResponse("<html><body>%s</body></html>" %e, status=424)

@permission_required('scm.install_installableset')
def delivery_apply_envt(request, delivery_id, envt_id_or_name, force_prereqs = False):    
    delivery = InstallableSet.objects.get(pk=delivery_id)
    try:
        envt = Environment.objects.get(name=envt_id_or_name)
    except Environment.DoesNotExist:
        envt = Environment.objects.get(pk=int(envt_id_or_name))
    
    install_iset_envt(delivery, envt, force_prereqs = force_prereqs)
    return redirect('scm:envtinstallhist', envt_name=envt.name)

@permission_required('scm.install_installableset')
def delivery_ii_apply_envt(request, ii_id, instance_id, envt_name, install_id = None):    
    ii = InstallableItem.objects.get(pk=ii_id)
    instance = ComponentInstance.objects.get(pk = instance_id)
    install = Installation.objects.get(pk = install_id) if install_id is not None else None
    envt = Environment.objects.get(name=envt_name)

    install = install_ii_single_target_envt(ii = ii, instance = instance, envt = envt, force_prereqs = True, install = install)
    
    response = HttpResponse(content_type='text/text')
    response.write(install.id)
    return response

def delivery_ii_test_envt(request, ii_id, envt_name, full_delivery = False):    
    ii = InstallableItem.objects.get(pk=ii_id)
    envt = Environment.objects.get(name=envt_name)
  
    try:
        ii.check_prerequisites(envt.name, ii.belongs_to_set.set_content.all() if full_delivery else ())
        return HttpResponse("<html><body>OK</body></html>")
    except MageScmFailedEnvironmentDependencyCheck, e:
        return HttpResponse("<html><body>%s</body></html>" %e, status=424)

def lc_versions_per_environment(request):
    Installation.objects.filter()
    envts = Environment.objects_active.filter(managed = True).order_by('typology__chronological_order', 'name')
    res = SortedDict()
    for lc in LogicalComponent.objects.filter(scm_trackable=True, active=True).select_related('application').order_by('application__name', 'name') :
        lc_list = []
        for envt in envts:
            compo_instances = envt.component_instances.filter(instanciates__implements__id=lc.id)
            versions = [i.latest_cic for i in compo_instances if i.version_object_safe]
            if len(versions) > 0:
                versions.sort(key=lambda x : x.created_on, reverse=True)
                lc_list.append(versions[0].result_of.what_is_installed)
            else:
                lc_list.append(None)
        res[lc] = lc_list
    
    return render(request, 'scm/lc_installs_envt.html', {'res': res, 'envts': envts})


def lc_list(request):
    lcs = LogicalComponent.objects.filter(active=True, scm_trackable = True).order_by('application', 'name')
    return render(request, 'scm/lc_versions.html', {'lcs': lcs})

@cache_control(must_revalidate=True)
def lc_versions(request, lc_id):
    lc = LogicalComponent.objects.get(pk = lc_id)
    return render(request, 'scm/lc_versions_detail.html', {'lc': lc})



@login_required
@permission_required('scm.add_delivery')
@cache_control(no_cache=True)
def delivery_edit(request, iset_id=None):
    if iset_id is None:
        extra=4
    else:
        extra=0
    
    ## Out model formset, linked to its parent
    InstallableItemFormSet = inlineformset_factory(Delivery, InstallableItem, form=IIForm, extra=extra)
    
    ## Already bound?
    instance = None
    if iset_id is not None:
        instance = InstallableSet.objects.get(pk=iset_id)
        ## A dev can only modify an unvalidated delivery
        if not request.user.has_perm('scm.modify_delivery') and instance.status != 3:
            return redirect(reverse('login') + '?next=%s' % request.path)
    
    ## General parameters
    level = int(getParam('DELIVERY_FORM_DATA_FIELDS'))
    display = { 'd1': False, 'd2': False, 'd3':False, 'd4':False, 'globalfile':False, 'iifile': False }
    if level >= 1:
        display['d1'] = True
    if level >= 2:
        display['d2'] = True
    if level >= 3:
        display['d3'] = True
    if level >= 4:
        display['d4'] = True
    mode = getParam('DELIVERY_FORM_DATAFILE_MODE')
    if mode == 'ONE_FILE_PER_SET':
        display['globalfile']= True
    if mode == 'ONE_FILE_PER_ITEM':
        display['iifile'] = True 
    
    ## Helper for javascript
    lc_im = {}
    for lc in LogicalComponent.objects.all():
        r = []
        for cic in lc.implemented_by.all():
            r.extend([i.id for i in cic.installation_methods.all()])
        lc_im[lc.id] = r
    
    ## Bind form
    if request.method == 'POST':
        form = DeliveryForm(request.POST, request.FILES, instance=instance)  # A form bound to the POST data
        iiformset = InstallableItemFormSet(request.POST, request.FILES, prefix='iis', instance=form.instance)
        
        if form.is_valid() and iiformset.is_valid():  # All validation rules pass
            instance = form.save()
        
            iiformset = InstallableItemFormSet(request.POST, request.FILES, prefix='iis', instance=instance)
            if iiformset.is_valid():
                iiformset.save()
                
                ## Done
                return redirect('scm:delivery_edit_dep', iset_id=instance.id)
    else:
        form = DeliveryForm(instance=instance)
        iiformset = InstallableItemFormSet(prefix='iis', instance=instance)

    ## Remove partially completed removed forms
    for ff in iiformset.forms:
        if hasattr(ff, "cleaned_data"):
            if ff.cleaned_data["DELETE"] if ff.cleaned_data.has_key("DELETE") else False and ff.instance.pk is None:
                iiformset.forms.remove(ff)
    
    return render(request, 'scm/delivery_edit.html', {
        'form': form,
        'iisf' : iiformset,
        'lc_im' : lc_im,
        'display' : display
    })


@login_required
@permission_required('scm.add_delivery')
@cache_control(no_cache=True)
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
    for v in lc.versions.all().order_by('pk'):
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

def backup_list(request, archive = False):
    return render(request, 'scm/backup_list.html', {'backups': BackupSet.objects.filter(removed__isnull=not archive).order_by('from_envt', 'set_date').select_related('all_items'), 'archive' : archive})

def backup_detail(request, bck_id):
    return render(request, 'scm/backup_detail.html', {'bck': BackupSet.objects.get(pk=bck_id)})

@permission_required('scm.add_backupset')
def backup_envt(request, envt_name):
    b = register_backup_envt_default_plan(envt_name, now())
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

@permission_required('scm.add_backupset')
def backup_script(request, envt_name, ci_id, bck_id = None):
    try:
        bs = register_backup(envt_name, now(), bck_id, ComponentInstance.objects.get(pk = ci_id), description = 'script backup')
        return HttpResponse(bs.id, content_type='text/text')
    except Exception, e:
        return HttpResponseBadRequest(e, content_type='text/text')
    

@permission_required('scm.del_backupset')
def is_archive(request, is_id):
    """Remove does not mean delete - just means it's not available anymore"""
    i_s = InstallableSet.objects.get(pk = is_id)
    i_s.removed = now()
    i_s.save()
    return redirect('welcome')

@permission_required('scm.del_backupset')
def is_unarchive(request, is_id):
    """Remove does not mean delete - just means it's not available anymore"""
    i_s = InstallableSet.objects.get(pk = is_id)
    i_s.removed = None
    i_s.save()
    print request
    return redirect('welcome')

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

def iset_content_shell(request, isetid):
    iset = InstallableSet.objects.get(pk=int(isetid))
    return render(request, 'scm/shell_ii_detail_ksh.html', {'is': iset}, content_type="text/text")

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

def backup_latest_age(request, ci_id):
    response = HttpResponse(content_type='text/text')
    try:
        ci = ComponentInstance.objects.get(pk = ci_id)
        bis = BackupSet.objects.filter(all_items__instance__id = ci.id)
        if bis.count() == 0:
            response.write("-1")
        else:
            bis = bis.latest('set_date')
            response.write(int(round((timezone.now() - bis.set_date).seconds / 60, 0)))
    except ComponentInstance.DoesNotExist, BackupSet.DoesNotExist:
        response.write("-1")
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
@staff_member_required
def demo_internal(request):
    reset()
    
    is_list = create_test_is()
    default = Convention(name='default convention')
    default.save()
    nc_sync_naming_convention(default)
    
    ref = TestHelper()
    install_iset_envt(is_list[0], ref.envt_prd1)
    install_iset_envt(is_list[1], ref.envt_prd1)
    #install_iset_envt(is_list[2], ref.envt_prd1)
    #install_iset_envt(is_list[3], ref.envt_prd1)
    #install_iset_envt(is_list[5], ref.envt_prd1)
    
    bs1 = register_backup('PRD1', now(), "no descr", *ref.envt_prd1.component_instances.all())
    register_backup_envt_default_plan('PRD1', now())
    install_iset_envt(bs1, ref.envt_tec2)
    
    return HttpResponseRedirect(reverse('welcome'))
    
@transaction.commit_on_success
@staff_member_required
def bootstrap(request):
    reset()
    default = Convention(name='default convention')
    default.save()
    nc_sync_naming_convention(default)
    
    from MAGE.settings import INSTALLED_APPS
    for app in [ i for i in INSTALLED_APPS if not i.startswith('django.')]:
        try:
            importlib.import_module(app + '.bootstrap')
        except ImportError:
            continue
    
    return HttpResponseRedirect(reverse('welcome'))
