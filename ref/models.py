# coding: utf-8

from django.db import models
from django.db.models.base import ModelBase
from django.contrib.contenttypes.models import ContentType
from MAGE.exceptions import MageError
from django.core.exceptions import ValidationError
from UserDict import DictMixin
import inspect


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
    default_convention = models.ForeignKey('Convention', null=True, blank=True, related_name='used_in_projects')
    
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
    name = models.CharField(max_length=100, verbose_name='Nom')
    
    description = models.CharField(max_length=500)
    implements = models.ForeignKey(LogicalComponent, related_name='implemented_by', verbose_name=u'composant logique implémenté')
    sla = models.ForeignKey(SLA, blank=True, null=True)
    python_model_to_use = models.ForeignKey(ContentType, verbose_name=u'implémentation technique')
    ref1 = models.CharField(max_length=20, verbose_name=u'reférence 1', blank=True, null=True)
    ref2 = models.CharField(max_length=20, verbose_name=u'reférence 2', blank=True, null=True)
    ref3 = models.CharField(max_length=20, verbose_name=u'reférence 3', blank=True, null=True)
    active = models.BooleanField(default=True, verbose_name=u'utilisé')
    
    def __unicode__(self):
        return u'%s' % self.name
    
    class Meta:
        verbose_name = u'implémentation technique d\'un composant logique'
        verbose_name_plural = u'implémentations techniques des composants logiques'

class EnvironmentType(models.Model):
    """ The way logical components are instanciated"""
    name = models.CharField(max_length=100, verbose_name='Nom')
    description = models.CharField(max_length=500, verbose_name='description')
    short_name = models.CharField(max_length=10, verbose_name='code')
    sla = models.ForeignKey(SLA, blank=True, null=True)
    implementation_patterns = models.ManyToManyField(ComponentImplementationClass)
    chronological_order = models.IntegerField(default=1)
    default_convention = models.ForeignKey('Convention', null=True, blank=True, related_name='used_in_envt_types')
    default_show_sensitive_data = models.BooleanField(default = False, verbose_name = "afficher les informations sensibles")

    def __get_cic_list(self):
        return ','.join([ i.name for i in self.implementation_patterns.all()])
    cic_list = property(__get_cic_list)
    
    def __unicode__(self):
        return self.name


################################################################################
## Main notion: the environment
################################################################################

class EnvironmentManagerStd(models.Manager):
    def get_query_set(self):
        return super(EnvironmentManagerStd, self).get_query_set().filter(template_only = False, active = True)
    
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
    show_sensitive_data = models.NullBooleanField(verbose_name = "afficher les informations sensibles", null = True, blank = True)
    
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

def getCustomLink(attrtype):
    def _getCustomLink(self):
        return self.dependsOn.get(model__model__iexact=attrtype).leaf

class CompoMeta(ModelBase):
    def __init__(self, name, bases, attrs): # 'self' should conventionally be 'cls', but pyDev bugs otherwise.
        ## Add parent fields  
        
        # Get the parents field      
        if not attrs.has_key('parents'):
            return
        parents = attrs['parents'] #TODO: remove parents from the class, add it as a private field to Component # .__bases__[0]
        
        for field_name in parents.iterkeys():
            if not parents[field_name].has_key('cardinality'):
                parents[field_name]['cardinality'] = 1
            if not parents[field_name].has_key('compulsory'):
                parents[field_name]['compulsory'] = False
                
            field_card = parents[field_name]['cardinality']
            field_model = parents[field_name]['model']
            
            getter = lambda slf, model_type = field_model, field_name = field_name: slf.__getcustomlink__(model_type, field_name)
            
            if field_card == 0 or field_card > 1:
                prop = property(fget=getter)
                setattr(self, field_name, prop)
                setattr(self, field_name + '_add', lambda slf, value, model_type=field_model, field_name=field_name: slf.__addtocustomlink__(value, model_type, field_name))
                setattr(self, field_name + '_delete', lambda slf, value, field_name=field_name: slf.__deletefromcustomlink__(value, field_name))
            elif field_card == 1:
                setter = lambda slf, value, model_type = field_model, field_name = field_name: slf.__setcustomlinkcard1__(value, field_name) 
                setattr(self, field_name, property(fget=getter, fset=setter))
                
        ## Let Django do its magic
        super(CompoMeta, self).__init__(name, bases, attrs)
    

    
class ComponentInstance(models.Model):
    """Base model (class) for all components. (should never need to be instantiated)"""
    __metaclass__ = CompoMeta
    
    ## Base data for all components
    name = models.CharField(max_length=100, null=True, blank=True, verbose_name=u'nom ')
    instanciates = models.ForeignKey(ComponentImplementationClass, null=True, blank=True, verbose_name=u'implémentation de ', related_name='instances')
    deleted = models.BooleanField(default=False)
    include_in_envt_backup = models.BooleanField()
    
    ## Environments
    environments = models.ManyToManyField(Environment, blank=True, null=True, verbose_name='environnements ', related_name='component_instances')
    
    ## Connections
    connectedTo = models.ManyToManyField('self', symmetrical=True, blank=True, verbose_name=u'connecté aux composants ')
    dependsOn = models.ManyToManyField('self', blank=True, verbose_name=u'supporté par ', symmetrical=False, related_name='subscribers', through='CI2DO')
    
    ## Polymorphism
    model = models.ForeignKey(ContentType)
    __leaf = None # cache
    def _getLeafItem(self):
        if self.__leaf is None:
            self.__leaf = self.model.get_object_for_this_type(id=self.id)
        return self.__leaf
    leaf = property(_getLeafItem)
    
    ## Stuff to add the "parent" fields
    parents = {}
    def __getcustomlink__(self, field_model, field_name):
        cache_field_name = '__cache_' + field_name
        f = self.parents[field_name]
        
        if f['cardinality'] == 1:
            if not self.__dict__.has_key(cache_field_name) or self.__dict__[cache_field_name] is None:
                try:
                    self.__dict__[cache_field_name] = self.dependsOn.get(statues_ci2do__rel_name=field_name).leaf
                except ComponentInstance.DoesNotExist:
                    self.__dict__[cache_field_name] = None
            return self.__dict__[cache_field_name]
        else:
            # Don't use self.dependsOn - we want the leaf objects directly from the query
            ct = ContentType.objects.get(model__iexact=field_model)
            #return self.dependsOn.filter(statues_ci2do__rel_name=field_name)
            return ct.get_all_objects_for_this_type(statues_ci2do__rel_name=field_name, subscribers__id=self.id)
    
    def __setcustomlinkcard1__(self, value, field_name):
        cache_field_name = '__cache_' + field_name
        self.__dict__[cache_field_name] = None
        
        c = self.pedestals_ci2do.filter(rel_name=field_name)
        if len(c) == 0:
            nc = CI2DO(pedestal=value, statue=self, rel_name=field_name)
            nc.save()
        elif len(c) == 1:
            if value is None:
                c[0].delete()
            else:
                c[0].pedestal = value
                c[0].save()
        else:
            raise MageError('a field with cardinality 1 has more than one value')
    
    def __addtocustomlink__(self, value, field_type, field_name):
        f = self.dependsOn.filter(statues_ci2do__rel_name=field_name, id=value.id)
        
        if len(f) > 0:
            raise MageError('a component cannot be twice parent of another')
        
        nc = CI2DO(pedestal=value, statue=self, rel_name=field_name)
        nc.save()
    
    def __deletefromcustomlink__(self, value, field_name):   
        f = self.pedestals_ci2do.filter(rel_name=field_name, pedestal_id=value.id) 
        for r in f:
            r.delete()
    
    def __clearcustomlink__(self, field_name):
        f = self.pedestals_ci2do.filter(rel_name=field_name) 
        for r in f:
            r.delete()
            
    def check_relation_complete(self):
        """ returns a list of tuples containing errors (relation_name, cardinality, actual_length)"""
        res = []
        for r, descr in self.parents.items():
            real = self.pedestals_ci2do.filter(rel_name=r)
            card = descr['cardinality']
            if card == 0:
                continue # 0..n: whatever result is OK
            else:
                if real.count() != card:
                    res.append((r, card, real.count()))        
        return res
    
    ## Introspection helpers
    def exportable_fields(self, restricted_access = False):
        internal_attrs = ('latest_cic', 'leaf', 'pk', 'version', 'version_object_safe', 'default_convention')
        self.leaf.__dict__['component_type'] = self.model.model
        if restricted_access:
            keys = self.leaf.__dict__.keys()
            for t in inspect.getmembers(type(self.leaf), lambda x: isinstance(x, property)):
                if t[0] in internal_attrs:
                    continue
                keys.append(t[0])
        else:      
            keys = [ i for i in self.leaf.__dict__.keys() if i not in self.leaf.restricted_fields]
            for t in inspect.getmembers(type(self.leaf), lambda x: isinstance(x, property)):
                if t[0] in internal_attrs or t[0] in self.leaf.restricted_fields:
                    continue
                keys.append(t[0])
        keys.remove('model_id');keys.remove('_state');keys.remove('componentinstance_ptr_id');keys.append('environments')
        return keys
    
    ## Set the "model" field at initialization
    def __setContentType(self):
        if self.model_id is None:
            self.model = ContentType.objects.get_for_model(type(self))
    
    def __init__(self, *args, **kwargs):
        super(ComponentInstance, self).__init__(*args, **kwargs)
        self.__setContentType()
        self.extParams = ExtendedParameterDict(self)
        if self.pk is None:
            self.include_in_envt_backup = self.include_in_default_envt_backup
    
    ## Pretty print
    def __unicode__(self):
        if self.__class__ == ComponentInstance and not self.model is None:
            return self.leaf.__unicode__()
        if not self.name is None:
            return '%s' % (self.name)
        else:
            return '%s' % (self.name)
    
    restricted_fields = ('password',)
    include_in_default_envt_backup = True
    class Meta:
        permissions = (('allfields_componentinstance', 'access all fields including restricted ones'),)


class CI2DO(models.Model):
    statue = models.ForeignKey(ComponentInstance, related_name='pedestals_ci2do', verbose_name='child')
    pedestal = models.ForeignKey(ComponentInstance, related_name='statues_ci2do', verbose_name='depends on')
    rel_name = models.CharField(max_length=100, verbose_name='relation name')
    #rel_cardinality = models.IntegerField(default = 1)
    
    def clean(self):
        fd = self.statue.parents[self.rel_name]
        f_type = fd['model']
        #f_card = fd.get('card') or 1
        
        if self.pedestal.model.model.lower() != f_type.lower():
            raise ValidationError('link %s expects a %s instance - a %s was given' % (self.rel_name, self.statue.parents[self.rel_name]['model'], self.pedestal.model.model))
        
        super(CI2DO, self).clean()
         
        
    class Meta:
        verbose_name = 'link to base component'
        verbose_name_plural = 'links to base components'

class ExtendedParameterDict(DictMixin):
    def __init__(self, instance):
        self.instance = instance
    
    def __len__(self):
        return self.instance.parameters.all().count()
        
    def __getitem__(self, key): 
        try:
            return self.instance.parameters.get(key=key)
        except ExtendedParameter.DoesNotExist:
            raise KeyError
    
    def __setitem__(self, key, value):
        try:
            self.__getitem__(key).value = value
        except KeyError:
            ep = ExtendedParameter(key=key, value=value, instance=self.instance)
            ep.save()
    
    def __delitem__(self, key):
        ep = self.__getitem__(key)
        ep.delete()
        
    def keys(self):
        return self.instance.parameters.values_list('key')
    
    def values(self):
        return self.instance.parameters.values_list('value')

class ExtendedParameter(models.Model):
    key = models.CharField(max_length=50)
    value = models.CharField(max_length=100)
    instance = models.ForeignKey(ComponentInstance, related_name='parameters')
    
    
################################################################################
## Naming and linking norms
################################################################################ 

class Convention(models.Model):
    name = models.CharField(max_length=20)
    
    def __unicode__(self):
        return u'Norme %s' % self.name
    
    class Meta:
        verbose_name = 'norme'
        verbose_name_plural = 'normes'
    
    def set_field(self, model_name, field_name, pattern):
        rel = self.fields.get(model=model_name, field=field_name)
        rel.pattern = pattern
        rel.save()
    
    # def value_field() # actually monkey patched from naming.py to avoid circular imports between mcl.py and models.py
    
class ConventionField(models.Model):
    model = models.CharField(max_length=254, verbose_name=u'composant technique')
    field = models.CharField(max_length=254, verbose_name=u'champ')
    pattern = models.CharField(max_length=1023, null=True, blank=True, verbose_name=u'norme') 
    convention_set = models.ForeignKey(Convention, related_name='fields') 
    pattern_type = models.CharField(max_length=4, choices=(('MCL1', 'MCL query with only one result'),
                                                               ('MCL0', 'MCL query with 0 to * results'),
                                                               ('P', 'simple pattern'),
                                                               ('CIC', 'implementation class name'),
                                                               ('TF', 'True ou False')))
    overwrite_copy = models.BooleanField(default=False, verbose_name=u'prioritaire sur copie')
    
    class Meta:
        verbose_name = u'norme de remplissage d\'un champ de composant'
        verbose_name_plural = u'normes de remplissage des champs des composants'
        
    def __unicode__(self):
        return u'%s.%s = %s' % (self.model, self.field, self.pattern)

class ConventionCounter(models.Model):
    scope_type = models.CharField(max_length=50)
    scope_param_1 = models.CharField(max_length=50, blank=True, null=True, default=None)
    scope_param_2 = models.CharField(max_length=50, blank=True, null=True, default=None)
    val = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = u'Compteur'
    

################################################################################
## Test components
################################################################################

class Test1(ComponentInstance):
    raccoon = models.CharField(max_length=100, default='houba hop') 
    
class Test2(ComponentInstance):
    parents = {'daddy': {'model': 'Test1', 'cardinality' :1, 'compulsory': False},
               'daddies': {'model': 'Test1', 'cardinality' :3, 'compulsory': False}} 

class Test3(ComponentInstance):
    f = models.ForeignKey(Test1)
    
