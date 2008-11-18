# coding: utf-8


###########################################################
## REF
###########################################################

from django.db import models
from django.contrib import admin
#from django.utils.translation import ugettext as _


    
class MageModelType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=500)
    model = models.CharField(max_length=100, unique=True)
    def __unicode__(self):
        return u'%s' %(self.name)
    
class MageModelTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    ordering = ('name',)


class Environment(models.Model):
    name = models.CharField(max_length=100, verbose_name='Nom')
    buildDate = models.DateField(verbose_name='Date de création')
    destructionDate = models.DateField(verbose_name='Date de suppression')
    description = models.CharField(max_length=500)
    
    def __unicode__(self):
        return "%s" %(self.name)

class EnvironmentAdmin(admin.ModelAdmin):
    fields = ['name', 'description', 'buildDate', 'destructionDate']
    list_display = ('name', 'description',)
    ordering = ('name',)

class Component(models.Model):
    """Base model (class) for all components. (cannot be instanciated)"""
    def __init__(self, *args, **kwargs):
        models.Model.__init__(self,  *args, **kwargs)
        if self.model is None:
            self.model = MageModelType.objects.get(model=self.__class__.__name__.lower())
        if self.class_name is None or self.class_name == "":         
            self.class_name = self.model.name # default: class name = model
    
    ## Base data for all components
    model = models.ForeignKey(MageModelType, blank=True, null=True)
    class_name = models.CharField(max_length=100, verbose_name='Classe du composant ')
    instance_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='Nom du composant ')
    
    ## Environments
    environments = models.ManyToManyField(Environment, blank=True, null=True, verbose_name='Environnements ')
    
    ## Connections
    connectedTo = models.ManyToManyField('self', symmetrical=True, blank=True, verbose_name='Connecté aux composants ')
    dependsOn = models.ManyToManyField('self', blank=True, verbose_name='Supporté par ', symmetrical=False, related_name='subscribers')
    
    def isLeaf(self):
        return self.__class__.__name__.lower() == self.model.model
    
    def _getLeafItem(self):
        if not self.isLeaf():
            return getattr(self, self.model.model)
        else:
            return self
    leaf = property(_getLeafItem)
    
    def __unicode__(self):
        if type(self) == Component:
            return self.leaf.__unicode__()
        
        if not self.instance_name is None:
            return '%s (%s)' %(self.instance_name, self.class_name)
        else:
            return '%s (%s)' %(self.class_name, self.model.name)


#admin.site.register(Environment, EnvironmentAdmin)
#admin.site.register(MageModelType,MageModelTypeAdmin)