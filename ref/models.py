# coding: utf-8

""" 
    The referential is the foundation of MAGE, and thus the only required component.
    
    This file contains every referential class.
    
    @author: Marc-Antoine Gouillart
    @contact: marsu_pilami@msn.com
    @license: GNU GVL v3
"""

## Django imports
from django.db import models
from django.db.models.base import ModelBase
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType



#########################################################
## Projects & environments
#########################################################

class Project(models.Model):
    """ 
        referential objects may optionally be classified inside projects, defined by a code name
        and contaiing a description
    """
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500)

class ProjectAdmin(admin.ModelAdmin):
    pass

class Environment(models.Model):
    """ 
        A set of components forms an environment
    """
    name = models.CharField(max_length=100, verbose_name='Nom')
    buildDate = models.DateField(verbose_name=u'Date de création')
    destructionDate = models.DateField(verbose_name=u'Date de suppression')
    description = models.CharField(max_length=500)
    handler = models.CharField(max_length=100, verbose_name='responsable')
    project = models.ForeignKey(Project, null=True, blank=True)
    
    def __unicode__(self):
        return "%s (%s)" %(self.name, self.description)

class EnvironmentAdmin(admin.ModelAdmin):
    fields = ['name', 'description', 'buildDate', 'destructionDate']
    list_display = ('name', 'description',)
    ordering = ('name',)



#########################################################
## Component base definition
#########################################################

class CompoMeta(ModelBase):
    def __new__(cls, name, bases, attrs):
        ## Get Django metaclass instance (= true model class)
        modelclass = super(CompoMeta, cls).__new__(cls, name, bases, attrs)
        
        ## Add parent fields
        try:
            for field in modelclass.parents.iterkeys():
                modelclass.add_to_class(field, property(fget = lambda self: self.__getattr__(field),))
        except AttributeError:
            pass
        
        ## Return the class
        return modelclass

class Component(models.Model):
    __metaclass__ = CompoMeta
    
    """Base model (class) for all components. (cannot be instanciated)"""
    ## Base data for all components
    class_name = models.CharField(max_length=100, blank=True, verbose_name='Classe du composant ')
    instance_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='Nom du composant ')
    
    ## Environments
    environments = models.ManyToManyField(Environment, blank=True, null=True, verbose_name='Environnements ')
    
    ## Connections
    connectedTo = models.ManyToManyField('self', symmetrical=True, blank=True, verbose_name=u'Connecté aux composants ')
    dependsOn = models.ManyToManyField('self', blank=True, verbose_name=u'Supporté par ', symmetrical=False, related_name='subscribers')
    
    ## Polymorphism
    model = models.ForeignKey(ContentType)
    def save(self, *args, **kwargs) :
        ## Model type
        if type(self) == Component:
            raise Exception("Impossible d'instancier un Component")
        self.model = ContentType.objects.get_for_model(type(self))
        
        ## Class (sub classification of components) default
        if self.class_name is None or self.class_name == "":         
            self.class_name = self.model.__unicode__() # default: class name = model
        
        ## Save to base for real
        super(Component, self).save(*args, **kwargs) 
            
    def _getLeafItem(self):
        return self.model.get_object_for_this_type(id=self.id)
    leaf = property(_getLeafItem)

    ## Pretty print
    def __unicode__(self):
        if self.__class__ == Component:
            return self.leaf.__unicode__()
        if not self.instance_name is None:
            return '%s' %(self.instance_name)
        else:
            return '%s' %(self.class_name)

    class Meta:
        verbose_name = u'composant'
        verbose_name_plural = u'composants'

    def __getattr__(self, item):
        """
            Overload the get function so as to enable getting parent attributes 
            (if 'parents' fields is defined in the model class)
        """
        try: return self.dependsOn.get(model__model=self.parents[item].lower()).leaf
        except: pass
        try: return super(Component, self).__getattr__(self, item)
        except: pass
        raise AttributeError(item)     



#########################################################
## Note : all admin classes are disabled to avoid endless import loop caused by admin.autodiscover 
#admin.site.register(Environment, EnvironmentAdmin)
#admin.site.register(MageModelType,MageModelTypeAdmin)
#admin.site.register(Project,ProjectAdmin)
