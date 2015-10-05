# coding: utf-8

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Group
from django.contrib.auth.views import redirect_to_login
from django.db import models
from django.conf import settings
from django.core.cache import cache
from ref.models import Environment, ComponentInstance

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
    ('change_envt_sensible', 'Modifier les informations sensibles d\'un environnement'),  # read_sensible+change?
    ('change_permissions', 'Modifier les habilitations'),
    ('read_meta', 'Consulter la modélisation des compsants'),
    ('change_meta', 'Modifier la modélisation des compsants')
)


class AdministrationUnit(models.Model):
    """
        referential objects may optionally be classified inside these, defined by a code name
        and containing a description.
        Basically, this is a folder. ACL are defined on these folders.
        A top level unit (one with parent = null) is also called a project.
    """
    name = models.CharField(max_length=100, unique=True)
    alternate_name_1 = models.CharField(max_length=100, null=True, blank=True)
    alternate_name_2 = models.CharField(max_length=100, null=True, blank=True)
    alternate_name_3 = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=500)
    parent = models.ForeignKey('AdministrationUnit', null=True, blank=True, related_name='subfolders')
    block_inheritance = models.BooleanField(default=False)

    class Meta:
        verbose_name = u'dossier'
        verbose_name_plural = u'dossiers'

    def is_empty(self):
        return len(self.environment_set.all()) + len(self.subfolders.all()) == 0
    empty = property(is_empty)

    def delete(self, using=None):
        if not self.empty:
            raise Exception('non-empty folders cannot be deleted')
        super(AdministrationUnit, self).delete(using)

    def __unicode__(self):
        return self.name

    def scope(self, aus=None, level=0):
        """
        Naive tree distance calculation. Should be enough for our needs performance-wise.
        Current node is included in the result.
        """
        if aus is None:
            aus = AdministrationUnit.objects.all()
        res = [self, ]

        for au in aus:
            if au.parent_id == self.pk:
                res += au.scope(aus, level + 1)
        return res

    def superscope(self, aus=None):
        """
        Current node is included in the result.
        """
        if aus is None:
            aus = AdministrationUnit.objects.all()
        res = []
        cur = self.pk
        while cur:
            for au in aus:
                if au.pk == cur:
                    res.append(au)
                    cur = au.parent_id
                    continue
        return res

    def get_acl(self):
        return get_acl(self)


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
                    return self.has_perm(user_obj, perm, obj.project)
                if obj.environments.count() == 0:
                    return False
                ok = True
                for envt in obj.environments.all():
                    ok = ok and self.has_perm(user_obj, perm, envt.project)
                return ok

            if isinstance(obj, AdministrationUnit):
                acl = obj.get_acl()
                cache_key = "user_groups_%s" % user_obj.pk
                user_groups = cache.get(cache_key)
                if not user_groups:
                    user_groups = user_obj.groups.all()
                    cache.set(cache_key, user_groups, 60)
                for group in user_groups:
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


def folder_permission_required(perm):
    def real_decorator(function):
        def decorator(request, *args, **kwargs):
            folder_id = int(kwargs['folder_id'])
            if not request.user.is_authenticated or not request.user.has_perm(perm, folder_id):
                return redirect_to_login(request.path)
            return function(request, *args, **kwargs)

        return decorator

    return real_decorator


def get_user_scope(folder_or_id, user, perm):
    if isinstance(folder_or_id, int) or isinstance(folder_or_id, unicode):
        folder = AdministrationUnit.objects.get(pk=int(folder_or_id))
    else:
        folder = folder_or_id
    return [f for f in folder.scope() if user.has_perm(perm, f)]


def get_acl(folder_or_id):
    # If by ID, we may simply need to query the cache
    if isinstance(folder_or_id, int):
        cache_key = "acl_folder_%s" % folder_or_id
        a = cache.get(cache_key)
        if a:
            return a
        # Not in cache => we need to do some queries
        return AdministrationUnit.objects.prefetch_related('acl').get(pk=folder_or_id).get_acl()

    # Inside cache?
    cache_key = "acl_folder_%s" % folder_or_id.pk
    a = cache.get(cache_key)
    if a:
        return a

    # Parents?
    if not folder_or_id.block_inheritance and folder_or_id.parent_id:
        acl = folder_or_id.parent.get_acl()
    else:
        acl = {}
        for perm in PERMISSIONS:
            acl[perm[0]] = []

    # Local ACE
    for ace in folder_or_id.acl.all():
        acl[ace.codename].append(ace.group_id)

    cache.set(cache_key, acl)
    return acl


def get_folder(path):
    res = AdministrationUnit.objects
    p = ''
    for seg in reversed(path.split('/')):
        if not seg:
            break
        res = res.filter(**{'%sname' % p: seg})
        p = '%sparent__' % p
    if len(res) > 1:
        raise Exception('multiple folders possible for path %s' % path)
    if len(res) == 0:
        raise Exception('folder %s does not exist' % path)
    return res[0]
