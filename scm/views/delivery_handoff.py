# coding: utf-8

# Python imports

# Django imports
from django.shortcuts import redirect, render
from django.urls import reverse
from django.forms.models import inlineformset_factory
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
from ref.permissions.perm_check import permission_required_project_aware

# MAGE imports
from scm.models import InstallableSet, InstallableItem, ItemDependency, Delivery
from scm.views.delivery_handoff_forms import IDForm, DeliveryForm, IIForm
from ref.models import LogicalComponent, getParam


@login_required
@permission_required_project_aware('scm.modify_delivery')
@cache_control(no_cache=True)
def delivery_edit(request, iset_id=None):
    if iset_id is None:
        extra = 4
    else:
        extra = 0

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
        display['globalfile'] = True
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
        iiformset = InstallableItemFormSet(request.POST, request.FILES, prefix='iis', instance=form.instance, form_kwargs={'project':request.project})

        if form.is_valid() and iiformset.is_valid():  # All validation rules pass
            form.instance.project = request.project # security important.
            instance = form.save()

            iiformset = InstallableItemFormSet(request.POST, request.FILES, prefix='iis', instance=instance, form_kwargs={'project':request.project})
            if iiformset.is_valid():
                iiformset.save()

                ## Done
                return redirect('scm:delivery_edit_dep', project_id=request.project.pk, iset_id=instance.id)
    else:
        form = DeliveryForm(instance=instance, initial={"project": request.project})
        iiformset = InstallableItemFormSet(prefix='iis', instance=instance, form_kwargs={'project':request.project})

    ## Remove partially completed removed forms
    for ff in iiformset.forms:
        if hasattr(ff, "cleaned_data"):
            if ff.cleaned_data["DELETE"] if "DELETE" in ff.cleaned_data else False and ff.instance.pk is None:
                iiformset.forms.remove(ff)

    return render(request, 'scm/delivery_edit.html', {
        'form': form,
        'iisf' : iiformset,
        'lc_im' : lc_im,
        'display' : display,
    })


@login_required
@permission_required_project_aware('scm.modify_delivery')
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
            fss[ii] = ItemDependencyFormSet(request.POST, request.FILES, instance=ii, prefix='ii%s' % ii.pk, form_kwargs={'project':request.project})
            valid = valid and fss[ii].is_valid()

        if valid:
            for fs in fss.values():
                fs.save()
            return redirect('scm:delivery_detail', iset_id=iset_id, project_id=request.project.pk)
    else:
        for ii in iset.set_content.all():
            fss[ii] = ItemDependencyFormSet(instance=ii, prefix='ii%s' % ii.pk, form_kwargs={'project':request.project})

    return render(request, 'scm/delivery_edit_dep.html', {
        'fss' : fss,
        'iset' : iset,
    })
