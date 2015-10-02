# coding: utf-8
'''
    @license: Apache License, Version 2.0
    @copyright: 2007-2013 Marc-Antoine Gouillart
    @author: Marc-Antoine Gouillart
'''

## Python imports
from UserDict import DictMixin

## Django imports
from django.db import models
from django.dispatch.dispatcher import receiver
from django.db.models.signals import pre_save


################################################################################
## Main notion: the environment
################################################################################=

class EnvironmentManagerStd(models.Manager):
    def get_queryset(self):
        return super(EnvironmentManagerStd, self).get_queryset().filter(template_only=False, active=True)


class Environment(models.Model):
    """ 
        A set of component instances forms an environment
    """
    name = models.CharField(max_length=100, verbose_name='Nom', unique=True)
    buildDate = models.DateField(verbose_name=u'Date de création', auto_now_add=True)
    destructionDate = models.DateField(verbose_name=u'Date de suppression prévue', null=True, blank=True)
    description = models.CharField(max_length=500)
    manager = models.CharField(max_length=100, verbose_name='responsable', null=True, blank=True)
    project = models.ForeignKey('AdministrationUnit', verbose_name='dossier')
    typology = models.ForeignKey('EnvironmentType', verbose_name=u'typologie')
    template_only = models.BooleanField(default=False)
    active = models.BooleanField(default=True, verbose_name=u'utilisé')
    show_sensitive_data = models.NullBooleanField(verbose_name="toujours afficher les informations sensibles",
                                                  null=True, blank=True, choices=(
            (None, u'défini par la typologie'), (False, 'cacher'), (True, 'montrer')))
    managed = models.BooleanField(default=True, verbose_name=u'administré')

    def __protected(self):
        if self.show_sensitive_data is not None:
            return not self.show_sensitive_data
        elif self.typology is not None:
            return not self.typology.default_show_sensitive_data
        else:
            return True

    protected = property(__protected)

    def __unicode__(self):
        return "%s" % (self.name,)

    def ci_id_list(self):
        return ','.join([str(ci.id) for ci in self.component_instances.filter(deleted=False)])

    objects = models.Manager()
    objects_active = EnvironmentManagerStd()

    class Meta:
        verbose_name = 'environnement'
        verbose_name_plural = 'environnements'


@receiver(pre_save, sender=Environment)
def disable_cis(sender, instance, raw, using, update_fields, **kwargs):
    """ mark all CI as delete when the envt is disabled """
    if instance.pk is None or raw or instance.active:
        return
    for ci in instance.component_instances.all():
        # only mark single envt instances.
        if ci.environments.count() == 1:
            ci.deleted = True
            ci.save()


################################################################################
## Environment components (actual instances of technical items)
################################################################################

class RichManager(models.Manager):
    """ Standard manager with a few helper methods"""

    def get_or_none(self, *args, **kwargs):
        try:
            return self.get(*args, **kwargs)
        except self.model.DoesNotExist:
            return None


class ComponentInstanceRelation(models.Model):
    source = models.ForeignKey('ComponentInstance', related_name='rel_target_set', verbose_name='instance source')
    target = models.ForeignKey('ComponentInstance', related_name='rel_targeted_by_set', verbose_name='instance cible')
    field = models.ForeignKey('ImplementationRelationDescription', verbose_name=u'champ implémenté',
                              related_name='field_set')

    class Meta:
        verbose_name = u'valeur de relation'
        verbose_name_plural = u'valeurs des relations'

    def __unicode__(self):
        return 'valeur de %s' % self.field.name


class ComponentInstanceField(models.Model):
    objects = RichManager()

    value = models.CharField(max_length=255, verbose_name='valeur', db_index=True)
    field = models.ForeignKey('ImplementationFieldDescription', verbose_name=u'champ implémenté')
    instance = models.ForeignKey('ComponentInstance', verbose_name=u'instance de composant', related_name='field_set')

    class Meta:
        verbose_name = u'valeur de champ'
        verbose_name_plural = u'valeurs des champs'

    def __unicode__(self):
        return 'valeur de %s' % self.field.name


class ComponentInstance(models.Model):
    """Instances! Usually used through its proxy object"""

    ## Base data for all components
    instanciates = models.ForeignKey('ComponentImplementationClass', null=True, blank=True,
                                     verbose_name=u'implémentation de ', related_name='instances')
    description = models.ForeignKey('ImplementationDescription', related_name='instance_set',
                                    verbose_name=u'décrit par l\'implémentation')
    deleted = models.BooleanField(default=False)
    include_in_envt_backup = models.BooleanField(default=False)

    ## Environments
    environments = models.ManyToManyField(Environment, blank=True, verbose_name='environnements ',
                                          related_name='component_instances')
    project = models.ForeignKey('AdministrationUnit', null=True, blank=True,
                                verbose_name='si hors environnement classer dans')

    ## Connections
    # TODO: symmetrical
    relationships = models.ManyToManyField('self', verbose_name='relations', through=ComponentInstanceRelation,
                                           symmetrical=False, related_name='reverse_relationships')

    ## Proxy object for easier handling
    __proxy = None

    def build_proxy(self, force=False):
        if self.description_id is None:
            return
        if self.__proxy is None or force:
            self.__proxy = self.description.proxy_class()(base_instance=self)
        return self.__proxy

    proxy = property(build_proxy)

    ## First environment (helper)
    def first_environment(self):
        if self.environments.count() > 0:
            return self.environments.all()[0]
        return None

    first_environment.short_description = u'notamment dans'
    first_environment.admin_order_field = 'environments__name'

    def _environments_str(self):
        if not self.environments or self.environments.count() == 0:
            return ""
        return ','.join([e.name for e in self.environments.all()])

    environments_str = property(_environments_str)

    ## Pretty print
    def __unicode__(self):
        if self.description:
            return '%s' % self.description.resolve_self_description(self)
        else:
            return '%s' % self.pk

    name = property(__unicode__)

    ## Pretty admin deleted field
    def active(self):
        return not self.deleted

    active.admin_order_field = 'deleted'
    active.boolean = True

    class Meta:
        permissions = (('allfields_componentinstance', 'access all fields including restricted ones'),)
        verbose_name = 'instance de composant'
        verbose_name_plural = 'instances de composant'


################################################################################
## Extended parameters
################################################################################

class ExtendedParameterDict(DictMixin):
    def __init__(self, instance):
        self.instance = instance

    def __len__(self):
        return self.instance.parameter_set.all().count()

    def __getitem__(self, key):
        try:
            return self.instance.parameter_set.get(key=key).value
        except ExtendedParameter.DoesNotExist:
            raise KeyError

    def __setitem__(self, key, value):
        ExtendedParameter.objects.update_or_create(defaults={'value': value}, key=key, instance=self.instance)

    def __delitem__(self, key):
        ep = self.__getitem__(key)
        ep.delete()

    def keys(self):
        return self.instance.parameter_set.values_list('key', flat=True)

    def values(self):
        return self.instance.parameter_set.values_list('value', flat=True)


class ExtendedParameter(models.Model):
    key = models.CharField(max_length=50, verbose_name='clef')
    value = models.CharField(max_length=100, verbose_name='valeur')
    instance = models.ForeignKey(ComponentInstance, related_name='parameter_set')

    def __unicode__(self):
        return '%s on %s' % (self.key, self.instance.name)

    class Meta:
        verbose_name = u'paramètre étendu'
        verbose_name_plural = u'paramètres étendus'
