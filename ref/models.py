# coding: utf-8

###########################################################
## REF
###########################################################

from django.db import models
from django.contrib import admin
#from django.utils.translation import ugettext as _


class MageModelType(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    model = models.CharField(max_length=100)
    def __unicode__(self):
        return u'%s' %(self.name)
    
class MageModelTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    ordering = ('name',)


class Environment(models.Model):
    name = models.CharField(max_length=30, verbose_name='Nom')
    buildDate = models.DateField(verbose_name='Date de création')
    destructionDate = models.DateField(verbose_name='Date de suppression')
    description = models.CharField(max_length=200)
    
    def __unicode__(self):
        return "Environnement %s" %(self.name)

class EnvironmentAdmin(admin.ModelAdmin):
    fields = ['name', 'description', 'buildDate', 'destructionDate']
    list_display = ('name', 'description',)
    ordering = ('name',)

class Composant(models.Model):
    def __init__(self, *args, **kwargs):
        models.Model.__init__(self,  *args, **kwargs)
        if self.type is None:
            self.type = MageModelType.objects.get(model=self.__class__.__name__.lower())
    
    name = models.CharField(max_length=100, verbose_name='Nom ')
    environments = models.ManyToManyField(Environment, blank=True, null=True, verbose_name='Environnements ')
    type = models.ForeignKey(MageModelType, blank=True, null=True)
    connectedTo = models.ManyToManyField("self", blank=True, null=True, verbose_name='Connecté aux composants ', symmetrical=True, related_name='connected_components')
    dependsOn = models.ManyToManyField("self", blank=True, null=True, verbose_name='Supporté par ', symmetrical=False, related_name='relies_on')
    
    description_view = None ## Exp 1
    detail_template = None  ## Exp 2
    
    parents = {}
    
    def isLeaf(self):
        return self.__class__.__name__.lower() == self.type.model
    
    def _getLeafItem(self):
        if not self.isLeaf():
            return getattr(self, self.type.model)
        else:
            return self
    leaf = property(_getLeafItem)
    
    def __unicode__(self):
        if not self.isLeaf():
            return self.leaf.__unicode__()
        else:
            return '%s' %(self.name)


admin.site.register(Environment, EnvironmentAdmin)
admin.site.register(MageModelType,MageModelTypeAdmin)