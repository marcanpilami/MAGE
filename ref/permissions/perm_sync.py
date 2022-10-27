
from ast import Delete
from ref.models.classifier import Project
from django.contrib.auth.models import Permission
from django.db.models import Q
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from django.dispatch.dispatcher import receiver

from ref.models.instances import ComponentInstance
from scm.models import Delivery, InstallableSet
from django.db.models.signals import post_save, post_delete

@receiver(post_delete, sender=Project)
@receiver(post_save, sender=Project)
@transaction.atomic
def sync_project_perms(**kwargs):
    """Synchronize project-level permissions. Must keep ID stability for PK with user models"""
    projects = Project.objects.all()
    permissions = Permission.objects.filter(Q(codename__startswith='allfields_componentinstance_', content_type__app_label='ref') |
                                            Q(codename__startswith='modify_delivery_', content_type__app_label='scm') |
                                            Q(codename__startswith='view_project_', content_type__app_label='ref') |
                                            Q(codename__startswith='modify_project_', content_type__app_label='ref') |
                                            Q(codename__startswith='install_installableset_', content_type__app_label='scm') |
                                            Q(codename__startswith='validate_installableset_', content_type__app_label='scm'))
    permissions = list(permissions)

    # Create or update permissions for the existing projects
    for project in projects:
        upsert_project_perm(permissions, project)

    # remove leftover from deleted projects
    project_ids = [project.id for project in projects]
    for perm in [perm for perm in permissions if not int(perm.codename.split('_')[-1]) in project_ids]:
        perm.delete()


def upsert_project_perm(permissions, project):
    view_perm = None
    view_perm_code = f'view_project_{project.id}'
    view_perm_label = f'Can view project {project.name} - {project.id} content'
    change_perm = None
    change_perm_code = f'modify_project_{project.id}'
    change_perm_label = f'Can modify project {project.name} - {project.id} content'
    allfields_perm = None
    allfields_perm_code = f'allfields_componentinstance_{project.id}'
    allfields_perm_label = f'Can view project {project.name} - {project.id} secure data'
    moddel_perm = None
    moddel_perm_code = f'modify_delivery_{project.id}'
    moddel_perm_label = f'Can modify project {project.name} - {project.id} deliveries'
    install_perm = None
    install_perm_code = f'install_installableset_{project.id}'
    install_perm_label = f'Can install deliveries inside project {project.name} - {project.id}'
    validate_delivery_perm = None
    validate_delivery_perm_code = f'validate_installableset_{project.id}'
    validate_delivery_perm_label = f'Can validate deliveries inside project {project.name} - {project.id}'

    for perm in permissions:
        if perm.codename == view_perm_code:
            view_perm = perm
        if perm.codename == change_perm_code:
            change_perm = perm
        if perm.codename == allfields_perm_code:
            allfields_perm = perm
        if perm.codename == moddel_perm_code:
            moddel_perm = perm
        if perm.codename == install_perm_code:
            install_perm = perm
        if perm.codename == validate_delivery_perm_code:
            validate_delivery_perm = perm

    if view_perm:
        view_perm.name = view_perm_label
        view_perm.save()
    else:
        Permission.objects.create(codename=view_perm_code,
                                  name=view_perm_label,
                                  content_type=ContentType.objects.get_for_model(Project))

    if change_perm:
        change_perm.name = change_perm_label
        change_perm.save()
    else:
        Permission.objects.create(codename=change_perm_code,
                                  name=change_perm_label,
                                  content_type=ContentType.objects.get_for_model(Project))

    if allfields_perm:
        allfields_perm.name = allfields_perm_label
        allfields_perm.save()
    else:
        Permission.objects.create(codename=allfields_perm_code,
                                  name=allfields_perm_label,
                                  content_type=ContentType.objects.get_for_model(ComponentInstance))

    if moddel_perm:
        moddel_perm.name = moddel_perm_label
        moddel_perm.save()
    else:
        Permission.objects.create(codename=moddel_perm_code,
                                  name=moddel_perm_label,
                                  content_type=ContentType.objects.get_for_model(Delivery))

    if install_perm:
        install_perm.name = install_perm_label
        install_perm.save()
    else:
        Permission.objects.create(codename=install_perm_code,
                                  name=install_perm_label,
                                  content_type=ContentType.objects.get_for_model(InstallableSet))

    if validate_delivery_perm:
        validate_delivery_perm.name = validate_delivery_perm_label
        validate_delivery_perm.save()
    else:
        Permission.objects.create(codename=validate_delivery_perm_code,
                                  name=validate_delivery_perm_label,
                                  content_type=ContentType.objects.get_for_model(InstallableSet))
