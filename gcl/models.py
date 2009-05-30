# coding: utf-8

###########################################################
## GCL
###########################################################

## Python imports
from datetime import date
from time import strftime

## Django imports
from django.db import models
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType

## MAGE imports
from MAGE.ref.models import Component
from MAGE.ref.models import Environment
from MAGE.ref.helpers import component_models_generator
from MAGE.gcl.exceptions import *


class ComponentTypeVersion(models.Model):
    """Référentiel GCL : contenu d'un IS (ou d'un tag)"""
    version = models.CharField(max_length=40)
    model = models.ForeignKey(ContentType)
    class_name = models.CharField(max_length=200, blank=True, null=True) 
    def __unicode__(self):
        return u'%s %s version %s' %(self.model.model_class()._meta.verbose_name, self.class_name, self.version)
    
    class Meta:
        verbose_name = u"Description mise à jour composant (CTV)"
        verbose_name_plural = u"Descriptions mise à jour composant (CTV)"
        
    def compare(ctv1, ctv2):
        """
            Order relation between CTV objects
            
            The relation is deduced from the IS (as they can be seen as links between the CTV).
            This function will not detect inconsistencies in IS dependencies (such as loops),
            as it will return the first result it will find. (This is, among others, to prevent infinite 
            loops and fasten things.)
            
            It is possible to compare CTV of different model classes, since an IS can draw relationships 
            between different classes.
            
            @return: 1 if the ctv1 should be installed AFTER the ctv2 (ctv1 > ctv2)
                     0 if it doesn't matter ("equality")
                    -1 if the ctv1 should be installed BEFORE the ctv2 (ctv1 < ctv2)
            
            @note: do NOT overload __cmp__ or eq with this function as they are already used by Django internals.
        """
        try: return ctv1.__compareWith(ctv2)
        except UnrelatedCTV: return 0
    
    def __compareWith(ctv1, ctv2, __reverseCall = False):
        """ The function actually doing the comparison. Here, equality (0) has a strict meaning. """
        ## Initial checks
        if not isinstance(ctv1, ComponentTypeVersion) or not isinstance(ctv2, ComponentTypeVersion):
            raise Exception("La fonction ctvOrder ne peut gerer que des objets CTV")
        if (ctv1.class_name == ctv2.class_name) and (ctv1.model == ctv2.model) and (ctv1.version == ctv2.version):
            return 0
        
        ## Loop on all the InstallableSets that install ctv1
        for ist in ctv1.installableset_set.all():
            ## Loop on all the requirements of the installable set
            for dep in ist.dependency_set.all():#filter(type_version__class_name = ctv1.class_name):              
                ## Terminaison condition: we have found ctv2
                if dep.type_version == ctv2:
                    if dep.operator == '>=' or dep.operator == '==': return 1
                    else: return 0
                
                ## Recursion
                try:
                    tmp = dep.type_version.__compareWith(ctv2)
                except UnrelatedCTV:
                    continue ## Nothing can be deduced from this result.
                
                ## Analysis of the recursion result
                if (tmp == 1 or tmp == 0) and (dep.operator == '>=' or dep.operator == '=='):
                    return 1    ## Transitivity on >
                if (tmp == -1 or tmp == 0) and (dep.operator == '<='):
                    return -1   ## Transitivity on <
                
                ## If here : the dependency that was analysed does not provide any useful relationship. Let's loop to the next one!
                
            ## If here : no relationship has given fruit. Let's try the reverse relationhip analysis.
            if not __reverseCall:
                return -ctv2.__compareWith(ctv1, True)
            
        ## If here : there is really nothing to say between ctv1 and ctv2, so say it : no order relationship
        raise UnrelatedCTV(ctv1, ctv2)   


class CTVAdmin(admin.ModelAdmin):
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name=='model':
            kwargs['queryset'] = ContentType.objects.filter(pk__in=(i.pk for i in component_models_generator()))
        return super(CTVAdmin, self).formfield_for_dbfield(db_field, **kwargs)

class InstallableSet(models.Model):
    """Référentiel GCL : ensemble pouvant être installé 
    Destiné à servir de clase de base. (par ex pour : patch, sauvegarde...)"""
    name = models.CharField(max_length=40, verbose_name='Référence', unique=True)
    set_date = models.DateTimeField(verbose_name='Date de réception', auto_now_add=True)
    acts_on = models.ManyToManyField(ComponentTypeVersion, verbose_name='Composants installés')
    ticket = models.IntegerField(max_length=6, verbose_name='Ticket lié', null=True ,blank=True)
    requirements = models.ManyToManyField(ComponentTypeVersion, verbose_name='Version de composants requises',
                                          related_name='required_by_is', blank=True, through='Dependency')
    
    is_full = models.BooleanField(verbose_name='Livraison annule et remplace (ou livraison initiale)', default='true')
    #data_loss = models.BooleanField(verbose_name=u'Entraine des pertes de données', default='false')
    
    def __unicode__(self):
        return u'%s' %(self.name)
    

class Dependency(models.Model):
    OPERATOR_CHOICES = (('>=', '>='),
                        ('<=', '<='),
                        ('==', '=='))
    installable_set = models.ForeignKey(InstallableSet)
    type_version = models.ForeignKey(ComponentTypeVersion)
    operator = models.CharField(max_length=2, choices=OPERATOR_CHOICES)
    
    def __unicode__(self):
        return u'dépendance de [%s] envers [%s en version %s]' %(self.installable_set, self.type_version.class_name,
                                                                 self.type_version.version)

class Installation(models.Model):
    """Every time an [IS] is used on an environmnent (or a set of [Components] inside an [Environmnent]),
    an [Installation] objet is created to register it"""    
    installed_set = models.ForeignKey(InstallableSet, verbose_name='Livraison appliquée ')
    #target_envt = models.ForeignKey(Environment, verbose_name='Environnement ' )
    target_components = models.ManyToManyField(Component, through='ComponentVersion', verbose_name='Résultats ')
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
    version = models.ForeignKey(ComponentTypeVersion)
    component = models.ForeignKey(Component)
    installation = models.ForeignKey(Installation)
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

    def __unicode__(self):
        return u'Tag n°%s - %s (concerne %s composants)' %(self.pk, self.name, self.versions.count())



#######################################################################################
## Update Component class with GCL objects
#######################################################################################

## Add a version property to component objects   
def getCV(comp):
    """@return: the latest installed CV on the Component"""
    try:
        return comp.componentversion_set.latest('pk') #installation__install_date').version
    except:
        raise UndefinedVersion(comp)
def getComponentVersion(comp):
    """@return: the latest installed CTV on the Component"""
    return getCV(comp).version
def getComponentVersionText(comp):
    try:
        return getComponentVersion(comp).version
    except UndefinedVersion:
        return "inconnue"
Component.version = property(getComponentVersionText)  
Component.latest_ctv = property(getComponentVersion)  
Component.latest_cv = property(getCV)  
Component.parents = {}



#admin.site.register(Tag)
admin.site.register(ComponentTypeVersion, CTVAdmin)