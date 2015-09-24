# coding: utf-8

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.conf import settings
from ref.models.classifier import AdministrationUnit
from ref.models.instances import Environment, ComponentInstance

try:
    group_model = settings.AUTH_GROUP_MODEL
except AttributeError:
    group_model = Group

# DEFAULT_PERMISSIONS = ('add', 'change', 'delete')

PERMISSIONS = (
    ('read_folder', 'Afficher les caractéristiques du dossier'),
    ('modify_folder', 'Modifier les caractéristiques du dossier'),
    ('list_envt', 'Afficher la liste des environnements contenus'),
    ('list_folders', 'Afficher la liste des sous dossiers contenus'),
    ('add_envt', 'Créer un environnement'),
    ('delete_envt', 'Supprimer un environnement'),
    ('add_folder', 'Ajouter un sous dossier'),
    ('delete_folder', 'Supprimer un sous-dossier vide'),
    ('read_envt', 'Afficher le détail des environnements (sauf informations sensibles)'),
    ('read_envt_sensible', 'Afficher les information sensibles des environnements'),
    ('change_envt', 'Modifier un environnement (sauf informations sensibles)'),
    ('change_envt_sensible', 'Modifier les informations sensibles d\'un environnement'),
    ('change_permissions', 'Modifier les habilitations')
)


class AclAuthorization(models.Model):
    target = models.ForeignKey(AdministrationUnit, verbose_name='cible', related_name='acl')
    # Note: inheritance is implicit. Settings an ACE to inheritance means deleting the ACE.
    grant = models.IntegerField(choices=((0, 'Allow'), (1, 'Forbid')), default=0)
    codename = models.CharField(max_length=20, db_index=True, choices=PERMISSIONS)
    group = models.ForeignKey(group_model)


class InternalAuthBackend(ModelBackend):
    def has_perm(self, user_obj, perm, obj=None):
        if not user_obj.is_active:
            return False
        if user_obj.is_superuser:
            return True

        if obj:
            if isinstance(obj, Environment):
                return self.has_perm(user_obj, perm, obj.project)

            if isinstance(obj, ComponentInstance):
                # CI  may belong to many environments. Must be OK on all.
                if obj.project:
                    return self.has_perm(user_obj, perm.obj.project)
                if obj.environments.count() == 0:
                    return False
                ok = True
                for envt in obj.environments.all():
                    ok = ok and self.has_perm(user_obj, perm, envt.project)
                return ok

            if isinstance(obj, AdministrationUnit):
                for group in user_obj.groups.all():
                    try:
                        ace = AclAuthorization.objects.get(codename=perm, grant=0, group=group, target=obj)
                        return True
                    except AclAuthorization.DoesNotExist:
                        pass
                if obj.parent is not None and not obj.block_inheritance:
                    return self.has_perm(user_obj, perm, obj.parent)

            return False

        return super(InternalAuthBackend, self).has_perm(user_obj, perm, obj)

    def has_module_perms(self, user_obj, app_label):
        return False

