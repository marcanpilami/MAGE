# coding: utf-8

## Django imports
from django.contrib.auth.decorators import permission_required
from django.views.decorators.cache import cache_control
from django.shortcuts import redirect, render
from django.http.response import HttpResponse
from django.utils.timezone import now

## MAGE imports
from scm.models import Delivery, InstallableSet, InstallableItem, Installation
from ref.models import Environment, ComponentInstance
from scm.exceptions import MageScmFailedEnvironmentDependencyCheck
from scm.install import install_iset_envt, install_ii_single_target_envt


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
        return HttpResponse("<html><body>%s</body></html>" % e, status=424)

@permission_required('scm.install_installableset')
def delivery_apply_envt(request, delivery_id, envt_id_or_name, force_prereqs=False):
    delivery = InstallableSet.objects.get(pk=delivery_id)
    try:
        envt = Environment.objects.get(name=envt_id_or_name)
    except Environment.DoesNotExist:
        envt = Environment.objects.get(pk=int(envt_id_or_name))

    install_iset_envt(delivery, envt, force_prereqs=force_prereqs)
    return redirect('scm:envtinstallhist', envt_name=envt.name)

@permission_required('scm.install_installableset')
def delivery_ii_apply_envt(request, ii_id, instance_id, envt_name, install_id=None):
    ii = InstallableItem.objects.get(pk=ii_id)
    instance = ComponentInstance.objects.get(pk=instance_id)
    install = Installation.objects.get(pk=install_id) if install_id is not None else None
    envt = Environment.objects.get(name=envt_name)

    install = install_ii_single_target_envt(ii=ii, instance=instance, envt=envt, force_prereqs=True, install=install)

    response = HttpResponse(content_type='text/text')
    response.write(install.id)
    return response

def delivery_ii_test_envt(request, ii_id, envt_name, full_delivery=False):
    ii = InstallableItem.objects.get(pk=ii_id)
    envt = Environment.objects.get(name=envt_name)

    try:
        ii.check_prerequisites(envt.name, ii.belongs_to_set.set_content.all() if full_delivery else ())
        return HttpResponse("<html><body>OK</body></html>")
    except MageScmFailedEnvironmentDependencyCheck, e:
        return HttpResponse("<html><body>%s</body></html>" % e, status=424)


@permission_required('scm.del_backupset')
def is_archive(request, is_id):
    """Remove does not mean delete - just means it's not available anymore"""
    i_s = InstallableSet.objects.get(pk=is_id)
    i_s.removed = now()
    i_s.save()
    return redirect('welcome')

@permission_required('scm.del_backupset')
def is_unarchive(request, is_id):
    """Remove does not mean delete - just means it's not available anymore"""
    i_s = InstallableSet.objects.get(pk=is_id)
    i_s.removed = None
    i_s.save()
    print request
    return redirect('welcome')
