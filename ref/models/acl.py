# coding: utf-8

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Group
from django.db import models
from django.conf import settings
from ref.models.classifier import AdministrationUnit, PERMISSIONS, get_acl
from ref.models.instances import Environment, ComponentInstance

try:
    group_model = settings.AUTH_GROUP_MODEL
except AttributeError:
    group_model = Group


# DEFAULT_PERMISSIONS = ('add', 'change', 'delete')



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
                acl = obj.get_acl()
                for group in user_obj.groups.all():
                    if group.pk in acl[perm]:
                        return True

            if isinstance(obj, int):
                acl = get_acl(obj)
                for group in user_obj.groups.all():
                    if group.pk in acl[perm]:
                        return True

            return False

        return super(InternalAuthBackend, self).has_perm(user_obj, perm, obj)

    def has_module_perms(self, user_obj, app_label):
        return False
