# coding: utf-8
""" models structuring the others: applicaion, project... """

# Django imports
from django.db import models
from django.core.cache import cache

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
    ('change_envt_sensible', 'Modifier les informations sensibles d\'un environnement'), # read_sensible+change?
    ('change_permissions', 'Modifier les habilitations')
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


class Application(models.Model):
    name = models.CharField(max_length=100, unique=True)
    alternate_name_1 = models.CharField(max_length=100, null=True, blank=True)
    alternate_name_2 = models.CharField(max_length=100, null=True, blank=True)
    alternate_name_3 = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=500)
    project = models.ForeignKey(AdministrationUnit, related_name='applications')

    def __unicode__(self):
        return self.name


class EnvironmentType(models.Model):
    """ The way logical components are instanciated"""
    name = models.CharField(max_length=100, verbose_name='Nom', unique=True)
    description = models.CharField(max_length=500, verbose_name='description')
    short_name = models.CharField(max_length=10, verbose_name='code', db_index=True)
    sla = models.ForeignKey('SLA', blank=True, null=True)
    implementation_patterns = models.ManyToManyField('ComponentImplementationClass', blank=True)
    chronological_order = models.IntegerField(default=1, verbose_name='ordre d\'affichage')
    default_show_sensitive_data = models.BooleanField(default=False, verbose_name="afficher les informations sensibles")

    def __get_cic_list(self):
        return ','.join([i.name for i in self.implementation_patterns.all()])

    cic_list = property(__get_cic_list)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'classification des environnements'
        verbose_name_plural = u'classifications des environnements'
