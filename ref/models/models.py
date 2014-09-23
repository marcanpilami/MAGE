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
from django.core.cache import cache

## MAGE imports
from ref.naming_language import resolve



################################################################################
## Helpers
################################################################################

class SLA(models.Model):
    rto = models.IntegerField()
    rpo = models.IntegerField()
    avalability = models.FloatField()
    #closed =
    open_at = models.TimeField()
    closes_at = models.TimeField()

    class Meta:
        verbose_name = 'SLA'
        verbose_name_plural = 'SLA'


################################################################################
## Classifiers
################################################################################

class Project(models.Model):
    """ 
        referential objects may optionally be classified inside projects, defined by a code name
        and containing a description
    """
    name = models.CharField(max_length=100, unique=True)
    alternate_name_1 = models.CharField(max_length=100, null=True, blank=True)
    alternate_name_2 = models.CharField(max_length=100, null=True, blank=True)
    alternate_name_3 = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=500)

    class Meta:
        verbose_name = u'projet'
        verbose_name_plural = u'projets'

    def __unicode__(self):
        return self.name

class Application(models.Model):
    name = models.CharField(max_length=100, unique=True)
    alternate_name_1 = models.CharField(max_length=100, null=True, blank=True)
    alternate_name_2 = models.CharField(max_length=100, null=True, blank=True)
    alternate_name_3 = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=500)
    project = models.ForeignKey(Project, null=True, blank=True, related_name='applications')

    def __unicode__(self):
        return self.name


################################################################################
## Constraints on environment instantiation
################################################################################

class LogicalComponent(models.Model):
    name = models.CharField(max_length=100, verbose_name='nom')
    description = models.CharField(max_length=500)
    application = models.ForeignKey(Application)
    scm_trackable = models.BooleanField(default=True)
    active = models.BooleanField(default=True, verbose_name=u'utilisé')
    ref1 = models.CharField(max_length=20, verbose_name=u'reférence 1', blank=True, null=True)
    ref2 = models.CharField(max_length=20, verbose_name=u'reférence 2', blank=True, null=True)
    ref3 = models.CharField(max_length=20, verbose_name=u'reférence 3', blank=True, null=True)

    def __unicode__(self):
        return u'%s' % (self.name)

    class Meta:
        verbose_name = u'composant logique'
        verbose_name_plural = u'composants logiques'

class ComponentImplementationClass(models.Model):
    """ An implementation offer for a given service. """
    name = models.CharField(max_length=100, verbose_name='code')

    description = models.CharField(max_length=500)
    implements = models.ForeignKey(LogicalComponent, related_name='implemented_by', verbose_name=u'composant logique implémenté')
    sla = models.ForeignKey(SLA, blank=True, null=True)
    technical_description = models.ForeignKey('ImplementationDescription', related_name='cic_set', verbose_name=u'description technique')
    ref1 = models.CharField(max_length=20, verbose_name=u'reférence 1', blank=True, null=True)
    ref2 = models.CharField(max_length=20, verbose_name=u'reférence 2', blank=True, null=True)
    ref3 = models.CharField(max_length=20, verbose_name=u'reférence 3', blank=True, null=True)
    active = models.BooleanField(default=True, verbose_name=u'utilisé')

    def __unicode__(self):
        return u'%s' % self.name

    class Meta:
        verbose_name = u'déclinaison technique d\'un CL'
        verbose_name_plural = u'déclinaisons techniques des CL'

class EnvironmentType(models.Model):
    """ The way logical components are instanciated"""
    name = models.CharField(max_length=100, verbose_name='Nom')
    description = models.CharField(max_length=500, verbose_name='description')
    short_name = models.CharField(max_length=10, verbose_name='code')
    sla = models.ForeignKey(SLA, blank=True, null=True)
    implementation_patterns = models.ManyToManyField(ComponentImplementationClass, blank=True)
    chronological_order = models.IntegerField(default=1, verbose_name='ordre d\'affichage')
    default_show_sensitive_data = models.BooleanField(default=False, verbose_name="afficher les informations sensibles")

    def __get_cic_list(self):
        return ','.join([ i.name for i in self.implementation_patterns.all()])
    cic_list = property(__get_cic_list)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'classification des environnements'
        verbose_name_plural = u'classifications des environnements'


################################################################################
## Description of the component instances
################################################################################

class ImplementationRelationType(models.Model):
    name = models.CharField(max_length=20, verbose_name='type relation')
    label = models.CharField(max_length=100, verbose_name='label')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'classification des relations'
        verbose_name_plural = 'classifications des relations'

class ImplementationFieldBase(models.Model):
    name = models.CharField(max_length=100, verbose_name='nom court du champ')
    label = models.CharField(max_length=150, verbose_name='label')
    label_short = models.CharField(max_length=30, verbose_name='label court', help_text=u'si vide, label sera utilisé', null=True, blank=True)
    help_text = models.CharField(max_length=254, verbose_name='aide descriptive du champ', null=True, blank=True)
    sensitive = models.BooleanField(default=False, verbose_name='sensible')

    class Meta:
        abstract = True

class ImplementationFieldDescription(ImplementationFieldBase):
    """ The description of a standard (i.e. that must be completed by the user) field inside a technical implementation """
    compulsory = models.BooleanField(default=True)
    default = models.CharField(max_length=500, verbose_name='défaut', null=True, blank=True)
    datatype = models.CharField(max_length=20, default='str', choices=(('str', 'chaîne de caractères'), ('int', 'entier')), verbose_name=u'type')
    widget_row = models.PositiveSmallIntegerField(blank=True, null=True)

    implementation = models.ForeignKey('ImplementationDescription', related_name='field_set', verbose_name=u'implémentation mère')

    def __unicode__(self):
        return '%s (%s)' % (self.name, self.implementation.name)

    def __short_label(self):
        return self.label_short or self.label
    short_label = property(__short_label)

    class Meta:
        verbose_name = u'champ simple'
        verbose_name_plural = u'champs simples'

class ImplementationComputedFieldDescription(ImplementationFieldBase):
    """ The description of a calculated field inside a technical implementation """
    pattern = models.CharField(max_length=500, verbose_name='chaîne de calcul')
    widget_row = models.PositiveSmallIntegerField(blank=True, null=True)

    implementation = models.ForeignKey('ImplementationDescription', verbose_name=u'implémentation mère', related_name='computed_field_set')

    def __unicode__(self):
        return '%s' % (self.name)

    def resolve(self, instance):
        return resolve(self.pattern, instance)

    class Meta:
        verbose_name = u'champ calculé'
        verbose_name_plural = u'champs calculés'

class ImplementationRelationDescription(ImplementationFieldBase):
    source = models.ForeignKey('ImplementationDescription', related_name='target_set', verbose_name='type source')
    target = models.ForeignKey('ImplementationDescription', related_name='is_targeted_by_set', verbose_name=u'type cible')
    min_cardinality = models.IntegerField(default=0)
    max_cardinality = models.IntegerField(blank=True, null=True)
    link_type = models.ForeignKey(ImplementationRelationType)

    def __unicode__(self):
        return '%s (%s)' % (self.name, self.source.name)

    class Meta:
        verbose_name = u'relation'
        verbose_name_plural = u'relations'

class ProxyRelSequence:
    '''
        Sequence type for handling relationships inside a proxy instance object.
        Some sequence methods are not implemented: 
            __setitem__: cannot change link - only add/delete links
            insert: relationships are not ordered, so no need to insert at specific position
            sort: see above
            reverse: see above
    '''

    def __init__(self, proxy, rel_descr):
        self.proxy = proxy
        self.rel_descr = rel_descr

    def __djangoseq__(self):
        return [i.target for i in ComponentInstanceRelation.objects.select_related('target').filter(source=self.proxy._instance, field=self.rel_descr).order_by('id')]

    def __delitem__(self, key):
        ''' for deletion of self[key]'''
        self.remove(self[key])

    def __getitem__(self, key):
        return self.__djangoseq__().__getitem__(key)

    def __iter__(self):
        return self.__djangoseq__().__iter__()

    def __len__(self):
        return len(self.__djangoseq__())

    def __str__(self):
        return self.__djangoseq__().__str__()

    def __eq__(self, other_seq):
        return other_seq.proxy._instance._id == self.proxy._instance.id and self.rel_descr.id == other_seq.rel_descr.id

    def __contains__(self, instance):
        return ComponentInstanceRelation.objects.filter(source=self.proxy._instance, target=instance if isinstance(instance, ComponentInstance) else instance._instance, field=self.rel_descr).count() > 0

    def append(self, target_instance):
        r = ComponentInstanceRelation(source=self.proxy._instance, target=target_instance if isinstance(target_instance, ComponentInstance) else target_instance._instance, field=self.rel_descr)
        r.save()

    def count(self, instance):
        return ComponentInstanceRelation.objects.select_related('target').filter(source=self.proxy._instance, target=instance, field=self.rel_descr).count()

    def index(self, instance):
        return self.__djangoseq__().index(instance if isinstance(instance, ComponentInstance) else instance._instance)

    def extend(self, instance_list):
        for item in instance_list:
            self.append(item)

    def pop(self, i=None):
        if not i:
            i = self.__len__() - 1
        rel_instance = ComponentInstanceRelation.objects.select_related('target').filter(source=self.proxy._instance, field=self.rel_descr).order_by('id')[i]
        item = rel_instance.target
        rel_instance.delete()
        return item

    def remove(self, target_instance):
        ComponentInstanceRelation.objects.filter(source=self.proxy._instance, target=target_instance if isinstance(target_instance, ComponentInstance) else target_instance._instance, field=self.rel_descr).delete()


def _proxyinit(self, base_instance=None, _cic=None, _env=None, _noconventions=False, **kwargs):
    self._descr_id = None
    self._id = None

    if not base_instance is None:
        self._instance = base_instance
        self._id = self._instance.pk
    elif not self.__class__._related_impl is None:
        self._instance = ComponentInstance(implementation=self.__class__._related_impl)
        self._instance.save()

    if not self.__class__._related_impl is None:
        self._descr_id = self.__class__._related_impl.pk

    ## Logical component (through CIC): either a CIC is given as an object, as a string or there is just no choice.
    if _cic and isinstance(_cic, ComponentImplementationClass):
        self._instance.instanciates = _cic
    elif _cic and isinstance(_cic, str):
        self._instance.instanciates = ComponentImplementationClass.objects.get(name=_cic)
    elif self.__class__._related_impl and not self._instance.pk and self.__class__._related_impl.cic_set.count() == 1:
        self._instance.instanciates = self.__class__._related_impl.cic_set.all()[0]

    ## Envts
    if _env and type(_env) is list:
        for env in _env:
            self._instance.environments.add(env)
    elif _env and type(_env) is str:
        self._instance.environments.add(Environment.objects.get(name=_env))
    elif _env and type(_env) is Environment:
        self._instance.environments.add(_env)

    ## Fields
    if not _noconventions:
        from ref.conventions import value_instance_fields, value_instance_graph_fields
        value_instance_fields(self._instance, force=False)
    for name, value in kwargs.items():
        setattr(self, name, value)
    if not _noconventions:
        value_instance_graph_fields(self._instance, force=False)

    ## helper accessor to extended parameters
    self.extended_parameters = ExtendedParameterDict(self._instance)

def _proxy_single_rel_accessor(instance, field_id):
    try:
        return instance._instance.rel_target_set.select_related('target__implementation').get(field_id=field_id).target
    except ComponentInstanceRelation.DoesNotExist:
        return None

def _proxy_simple_accessor(proxy, field_id):
    try:
        field = proxy._instance.field_set.get(field_id=field_id)
    except ComponentInstanceField.DoesNotExist:
        return None
    return field.value

_classes = {}
class ImplementationDescription(models.Model):
    """ The description of a technical implementation """
    name = models.CharField(max_length=100, verbose_name='nom', db_index=True)
    description = models.CharField(max_length=500, verbose_name='description')
    tag = models.CharField(max_length=100, verbose_name=u'catégorie', null=True, blank=True, db_index=True)
    relationships = models.ManyToManyField('ImplementationDescription', through=ImplementationRelationDescription)
    include_in_default_envt_backup = models.BooleanField(default=False, verbose_name=u'inclure dans les backups par défaut')
    self_description_pattern = models.CharField(max_length=500, verbose_name='motif d\'auto description', help_text=u'sera utilisé pour toutes les descriptions par défaut des instances de composant. Utilise les même motifs (patterns) que les champs dynamiques.')

    def __unicode__(self):
        return self.name

    def resolve_self_description(self, instance):
        return resolve(self.self_description_pattern, instance)

    class Meta:
        verbose_name = u'paramétres d\'implémentation'
        verbose_name_plural = u'paramétres des implémentations'

    def proxy_class(self):
        try:
            return _classes[self.name]
        except:
            #TODO: datatype!
            attrs = {'__init__': _proxyinit, 'save': lambda slf: slf._instance.save(), 'get' : lambda slf, attr, x : getattr(slf, attr)}

            ## Standard fields
            for field in self.field_set.all():
                getter = lambda slf, field_id = field.id: _proxy_simple_accessor(slf, field_id)
                setter = lambda slf, value, lfield = field: ComponentInstanceField.objects.update_or_create(defaults={'value': value} , field=lfield, instance=slf._instance)
                attrs[field.name] = property(fget=getter, fset=setter, doc=field.label)

            ## Self to others relationships
            for field in self.target_set.all():
                if not field.max_cardinality or field.max_cardinality > 1:
                    ## In this case, list manipulation through a proxy object
                    getter = lambda slf, field = field: ProxyRelSequence(proxy=slf, rel_descr=field)
                else:
                    ## Direct get/set on a field
                    getter = lambda slf, field_id = field.id: _proxy_single_rel_accessor(slf, field_id)
                    setter = lambda slf, value, field_id = field.id:  ComponentInstanceRelation.objects.update_or_create(defaults={'target': value._instance if not isinstance(value, ComponentInstance) else value}, source=slf._instance, field_id=field_id)
                attrs[field.name] = property(fget=getter, fset=setter, doc=field.label)

            ## Other to self relationships
            #...

            ## Computed fields (read only)
            for field in self.computed_field_set.all():
                getter = lambda slf, pfield = field: pfield.resolve(slf)
                attrs[field.name] = property(fget=getter, doc=field.label)

            ## Create the class
            cls = type(str("__" + self.name.lower() + "_proxy"), (), attrs)
            cls._related_impl = self
            _classes[self.name] = cls
            return cls

    @staticmethod
    def class_for_name(name):
        descr = ImplementationDescription.objects.get(name=name)
        return descr.proxy_class()

    @staticmethod
    def class_for_id(pk):
        descr = ImplementationDescription.objects.get(pk=pk)
        return descr.proxy_class()

    @staticmethod
    def create_or_update(name, description, self_description_pattern, tag=None, include_in_default_envt_backup=False):
        try:
            idn = ImplementationDescription.objects.get(name=name)
            idn.description = description
            idn.self_description_pattern = self_description_pattern
            idn.tag = tag
            idn.include_in_default_envt_backup = include_in_default_envt_backup
            idn.save()
            return idn
        except:
            idn = ImplementationDescription(name=name, description=description, self_description_pattern=self_description_pattern, tag=tag, include_in_default_envt_backup=include_in_default_envt_backup)
            idn.save()
            return idn

    def add_field_simple(self, name, label, default=None, label_short=None, help_text=None, compulsory=True, sensitive=False, datatype='str', widget_row=0):
        self.field_set.add(ImplementationFieldDescription(name=name, label=label, sensitive=sensitive, datatype=datatype, default=default, implementation=self, label_short=label_short, help_text=help_text, compulsory=compulsory, widget_row=widget_row))
        return self

    def add_field_computed(self, name, label, pattern, sensitive=False, widget_row=0):
        self.computed_field_set.add(ImplementationComputedFieldDescription(name=name, label=label, pattern=pattern, sensitive=sensitive, implementation=self, widget_row=widget_row))
        return self

    def add_relationship(self, name, label, target, link_type, min_cardinality=0, max_cardinality=1):
        self.target_set.add(ImplementationRelationDescription(name=name, label=label, source=self, target=target, min_cardinality=min_cardinality, max_cardinality=max_cardinality, link_type=link_type))
        return self

    def field_count(self):
        return self.field_set.count() + self.computed_field_set.count() + self.relationships.count()


################################################################################
## Main notion: the environment
################################################################################

class EnvironmentManagerStd(models.Manager):
    def get_queryset(self):
        return super(EnvironmentManagerStd, self).get_query_set().filter(template_only=False, active=True)

class Environment(models.Model):
    """ 
        A set of components forms an environment
    """
    name = models.CharField(max_length=100, verbose_name='Nom')
    buildDate = models.DateField(verbose_name=u'Date de création', auto_now_add=True)
    destructionDate = models.DateField(verbose_name=u'Date de suppression prévue', null=True, blank=True)
    description = models.CharField(max_length=500)
    manager = models.CharField(max_length=100, verbose_name='responsable', null=True, blank=True)
    project = models.ForeignKey(Project, null=True, blank=True)
    typology = models.ForeignKey(EnvironmentType)
    template_only = models.BooleanField(default=False)
    active = models.BooleanField(default=True, verbose_name=u'utilisé')
    show_sensitive_data = models.NullBooleanField(verbose_name="afficher les informations sensibles", null=True, blank=True)
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

    objects = models.Manager()
    objects_active = EnvironmentManagerStd()

    class Meta:
        verbose_name = 'environnement'
        verbose_name_plural = 'environnements'


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
    field = models.ForeignKey(ImplementationRelationDescription, verbose_name=u'champ implémenté', related_name='field_set')

    class Meta:
        verbose_name = u'valeur de relation'
        verbose_name_plural = u'valeurs des relations'

    def __unicode__(self):
        return 'valeur de %s' % self.field.name

class ComponentInstanceField(models.Model):
    objects = RichManager()

    value = models.CharField(max_length=255, verbose_name='valeur')
    field = models.ForeignKey(ImplementationFieldDescription, verbose_name=u'champ implémenté')
    instance = models.ForeignKey('ComponentInstance', verbose_name=u'instance de composant', related_name='field_set')

    class Meta:
        verbose_name = u'valeur de champ'
        verbose_name_plural = u'valeurs des champs'

    def __unicode__(self):
        return 'valeur de %s' % self.field.name

class ComponentInstance(models.Model):
    """Instances! Usually used through its proxy object"""

    ## Base data for all components
    instanciates = models.ForeignKey(ComponentImplementationClass, null=True, blank=True, verbose_name=u'implémentation de ', related_name='instances')
    implementation = models.ForeignKey(ImplementationDescription, related_name='instance_set', verbose_name=u'décrit par l\'implémentation')
    deleted = models.BooleanField(default=False)
    include_in_envt_backup = models.BooleanField(default=False)

    ## Environments
    environments = models.ManyToManyField(Environment, blank=True, null=True, verbose_name='environnements ', related_name='component_instances')

    ## Connections
    #TODO: symmetrical
    relationships = models.ManyToManyField('self', verbose_name='relations', through=ComponentInstanceRelation, symmetrical=False, related_name='reverse_relationships')

    ## Proxy object for easier handling
    __proxy = None
    def build_proxy(self, force=False):
        if self.implementation_id is None:
            return
        if self.__proxy is None or force:
            self.__proxy = self.implementation.proxy_class()(base_instance=self)
        return self.__proxy
    proxy = property(build_proxy)

    ## First environment (helper)
    def first_environment(self):
        if self.environments.count() > 0:
            return self.environments.all()[0]
        return None
    first_environment.short_description = u'notamment dans'

    ## Pretty print
    def __unicode__(self):
        key = "selfdescr_%s" % self.pk
        cached = cache.get(key)
        if cached:
            return cached
        if self.implementation:
            val = self.implementation.resolve_self_description(self)
            cache.set(key, val, None)
            return val
        else:
            return '%s' % self.pk
    name = property(__unicode__)

    ## Pretty admin deelted field
    def active(self):
        return not self.deleted
    active.admin_order_field = 'deleted'
    active.boolean = True

    class Meta:
        permissions = (('allfields_componentinstance', 'access all fields including restricted ones'),)
        verbose_name = 'instance de composant'
        verbose_name_plural = 'instances de composant'


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


################################################################################
## Naming norms
################################################################################

class ConventionCounter(models.Model):
    scope_environment = models.ForeignKey(Environment, blank=True, null=True, default=None)
    scope_project = models.ForeignKey(Project, blank=True, null=True, default=None)
    scope_application = models.ForeignKey(Application, blank=True, null=True, default=None)
    scope_type = models.ForeignKey(ImplementationDescription, blank=True, null=True, default=None)
    scope_instance = models.IntegerField(blank=True, null=True, default=None)
    val = models.IntegerField(default=0, verbose_name='valeur courante')

    class Meta:
        verbose_name = u'Compteur convention nommage'
        verbose_name_plural = u'Compteurs convention nommage'

