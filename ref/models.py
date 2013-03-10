# coding: utf-8

from django.db import models
from django.db.models.base import ModelBase
from django.contrib.contenttypes.models import ContentType


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
    
     
################################################################################
## Classifiers
################################################################################

class Project(models.Model):
    """ 
        referential objects may optionally be classified inside projects, defined by a code name
        and containing a description
    """
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500)

class Application(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    project = models.ForeignKey(Project, null=True, blank=True)
    
    
################################################################################
## Constraints on environment instantiation
################################################################################
    
class LogicalComponent(models.Model):
    name = models.CharField(max_length=100, verbose_name='Nom')
    description = models.CharField(max_length=500)
    application = models.ForeignKey(Application)
    
class ComponentImplementationClass(models.Model):
    """ An implementation offer for a given service. Automatically created. """
    name = models.CharField(max_length=100, verbose_name='Nom')
    description = models.CharField(max_length=500)
    implements = models.ForeignKey(LogicalComponent)
    sla = models.ForeignKey(SLA, blank=True, null=True)
    python_model_to_use = models.ForeignKey(ContentType)

class EnvironmentType(models.Model):
    """ The way logical components are instanciated"""
    name = models.CharField(max_length=100, verbose_name='Nom')
    description = models.CharField(max_length=500, verbose_name='Nom')
    short_name = models.CharField(max_length=10, verbose_name='Nom')
    sla = models.ForeignKey(SLA, blank=True, null=True)
    implementation_patterns = models.ManyToManyField(ComponentImplementationClass)


################################################################################
## Main notion: the environment
################################################################################

class Environment(models.Model):
    """ 
        A set of components forms an environment
    """
    name = models.CharField(max_length=100, verbose_name='Nom')
    buildDate = models.DateField(verbose_name=u'Date de création', auto_now_add=True)
    destructionDate = models.DateField(verbose_name=u'Date de suppression', null=True, blank=True)
    description = models.CharField(max_length=500)
    manager = models.CharField(max_length=100, verbose_name='responsable', null=True, blank=True)
    project = models.ForeignKey(Project, null=True, blank=True)
    typology = models.ForeignKey(EnvironmentType)
    
    def __unicode__(self):
        return "%s (%s)" % (self.name, self.description)  
    

################################################################################
## Environment components (actual instances of technical items)
################################################################################    

class CompoMeta(ModelBase):
    def __new__(cls, name, bases, attrs):
        ## Get Django metaclass instance (= true model class)
        modelclass = super(CompoMeta, cls).__new__(cls, name, bases, attrs)
        
        ## Add parent fields
        try:
            parents = modelclass.parents #TODO: remove parents from the class, add it as a private field to Component # .__bases__[0]
            for field in parents.iterkeys():
                modelclass.add_to_class(field, property(fget=lambda self: self.__getcustomattr__(field)))
                a = modelclass._meta.__getattribute__(field)
                a.null = True
                a.blank = True
        except AttributeError:
            pass
        
        ## Return the class
        return modelclass
    
class ComponentInstance(models.Model):
    """Base model (class) for all components. (should never need to be instantiated)"""
    __metaclass__ = CompoMeta
    
    ## Base data for all components
    name = models.CharField(max_length=100, null=True, blank=True, verbose_name=u'Nom de cette instance de composant ')
    instanciates = models.ForeignKey(ComponentImplementationClass, null=True, blank=True, verbose_name=u'Solution d\'implémentation retenue')
    
    ## Environments
    environments = models.ManyToManyField(Environment, blank=True, null=True, verbose_name='Environnements ', related_name='component_instances')
    
    ## Connections
    connectedTo = models.ManyToManyField('self', symmetrical=True, blank=True, verbose_name=u'Connecté aux composants ')
    dependsOn = models.ManyToManyField('self', blank=True, verbose_name=u'Supporté par ', symmetrical=False, related_name='subscribers')
    
    ## Polymorphism
    model = models.ForeignKey(ContentType)
    __leaf = None # cache
    def _getLeafItem(self):
        if self.__leaf is None:
            self.__leaf = self.model.get_object_for_this_type(id=self.id)
        return self.__leaf
    leaf = property(_getLeafItem)
    
    ## Stuff to add the "parent" fields
    def __getcustomattr__(self, item):
        """
            Overload the get function so as to enable getting parent attributes 
            (if 'parents' fields is defined in the model class)
        """
        ## Parent field
        if self.parents.has_key(item):
            try: 
                return self.dependsOn.get(model__model__iexact=self.parents[item]).leaf
            except:
                return None         ## The field is defined but not its value
        
        ## Standard field - call Django accessor (should never be called except in debug tests)
        return super(ComponentInstance, self).__getattribute__(item)
        
    ## Set the "model" field at initialization
    def __setContentType(self):
        if self.model_id is None:
            self.model = ContentType.objects.get_for_model(type(self))
    
    def __init__(self, *args, **kwargs):
        super(ComponentInstance, self).__init__(*args, **kwargs)
        self.__setContentType()
    
    ## Pretty print
    def __unicode__(self):
        if self.__class__ == ComponentInstance and not self.model is None:
            return self.leaf.__unicode__()
        if not self.name is None:
            return '%s' % (self.name)
        else:
            return '%s' % (self.name)
