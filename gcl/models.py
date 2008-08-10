# coding: utf-8

###########################################################
## GCL
###########################################################

from django.db import models
from MAGE.ref.models import Composant
from MAGE.ref.models import MageModelType
from MAGE.ref.models import Environment
from django.contrib import admin
from datetime import date
from time import strftime
from MAGE.gcl.exceptions import *


class ComponentTypeVersion(models.Model):
    """Référentiel GCL : contenu d'un IS (ou d'un tag)"""
    version = models.CharField(max_length=40, core=True)
    component_type = models.ForeignKey(MageModelType, core=True)
    component_name = models.CharField(max_length=200, core=True, blank=True, null=True) 
    def __unicode__(self):
        return u'%s %s version %s' %(self.component_type, self.component_name, self.version)

class ComponentTypeVersionAdmin(admin.ModelAdmin):
    """Admin : for manual referencing of patchs and saves 
    @todo: should it remain editable in the admin ?"""
    list_display = ('version', 'component_type')    

    
class InstallableSet(models.Model):
    """Référentiel GCL : ensemble pouvant être installé 
    Destiné à servir de clase de base. (par ex pour : patch, sauvegarde...)"""
    name = models.CharField(max_length=40, verbose_name='Référence', unique=True)
    set_date = models.DateTimeField(verbose_name='Date de réception', auto_now_add=True)
    acts_on = models.ManyToManyField(ComponentTypeVersion, verbose_name='Composants installés')
    ticket = models.IntegerField(max_length=6, verbose_name='Ticket lié', null=True ,blank=True)
    requirements = models.ManyToManyField(ComponentTypeVersion, verbose_name='Version de composants requises', related_name='requires', blank=True)
    is_full = models.BooleanField(verbose_name='Livraison annule et remplace (ou livraison initiale)', default='true')
    
    def __unicode__(self):
        return u'%s' %(self.name)
        
    def __cmp__(self):
        return 0


class Installation(models.Model):
    """Every time an [IS] is used on an environmnent (or a set of [Components] inside an [Environmnent]),
    an [Installation] objet is created to register it"""    
    installed_set = models.ForeignKey(InstallableSet, verbose_name='Livraison appliquée ')
    target_envt = models.ForeignKey(Environment, verbose_name='Environnement ' )
    target_components = models.ManyToManyField(Composant, through='ComponentVersion', verbose_name='Résultats ')
    install_date = models.DateTimeField(verbose_name='Date d\'installation ')
    ticket = models.IntegerField(max_length=6, verbose_name='Ticket lié ', blank=True, null=True)
    
    def _getNbTargetComponents(self):
        return self.target_components.count()
    nb_modified_components = property(_getNbTargetComponents)
    def _getInstallableSetName(self):
        return self.installed_set.name
    installable_set_name = property(_getInstallableSetName)
    
    def __unicode__(self):
        return '%s sur %s le %s' %(self.installed_set.name, self.target_envt.name, self.install_date)


class ComponentVersion(models.Model):
    """GCL - exploitation. 
    The link (i.e. a ManyToMany intermediate) between [environment components] and [installations].
    Version is also directly referenced here as a helper, to avoid having to navigate through
    [Installation] -> [InstallableSet] -> [ComponentTypeVersion] to find it.""" 
    version = models.ForeignKey(ComponentTypeVersion, core=True)
    component = models.ForeignKey(Composant, core=True)
    installation = models.ForeignKey(Installation, core=True)
    def _getVersion(self):
        return self.version.version
    component_version = property(_getVersion)
    def __unicode__(self):
        return u'%s version %s' %(self.component.__unicode__(), self.component_version)

                
    
class Tag(models.Model):
    name = models.CharField(max_length=40, verbose_name='Référence', unique=True)
    versions = models.ManyToManyField(ComponentTypeVersion, verbose_name='Version des composants')
    from_envt = models.ForeignKey(Environment)
    snapshot_date = models.DateTimeField(verbose_name='Date de prise de la photo', auto_now_add=True)
    
    @staticmethod
    def snapshot(tag_name, envt_name):
        e = Environment.objects.get(name=envt_name)
        types_to_save = Composant.objects.filter(environments=e).values('type').distinct()
        t = Tag(name=tag_name, from_envt = e)
        t.save()
        
        for type_id in types_to_save:
            ## Take the first component of that type; only one entry per type in a tag
            comp_type = MageModelType.objects.get(pk=type_id['type'])
            c = Composant.objects.filter(environments=e, type=comp_type)[0]
            try:
                v = getComponentVersion(c)
            except UndefinedVersion:
                ## Version is undefined: this component type won't be referenced in the tag.
                ##   (we assume the user wants to reference the versions he knows of)
                continue
            t.versions.add(v)   
        t.save()
        return t





#######################################################################################
## Update Composant class with GCL objects
#######################################################################################

## Add a version property to component objects   
def getComponentVersion(comp):
    try:
        return comp.componentversion_set.latest('installation__install_date').version
    except:
        raise UndefinedVersion(comp)
def getComponentVersionText(comp):
    try:
        return getComponentVersion(comp).version
    except UndefinedVersion:
        return "inconnue"
Composant.version = property(getComponentVersionText)    


## Add a update base function
def update(comp):
    raise ComponentCannotBeUpgraded(comp)
Composant.update=update


## Register into the admin interface (debug only)
admin.site.register(ComponentTypeVersion, ComponentTypeVersionAdmin)