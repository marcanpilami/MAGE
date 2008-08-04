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
    
    
    def installOn(self, target_components, environment, fail_dep = False):
        """
        @author: mag
        @param fail_dep: set to True if you want a FailedDependenciesCheckException to be raised if check fails.
        @param environment: the name, or the Environment object, of the environment on which to install the IS.
        @param target_components: either
            *A list of component objects on which to apply the IS: [C1, C2, C3]
            *If you want to create new components during the installation (@note: it has to be a FULL IS)
             a list [(compo_name, compo_model, optArgs),] where :
                 *compo_name is the name (unicode) of the new component
                 *compo_model is the model (django.db.models.Model) of the new component
                 *optArg is a dictionary of optional arguments that may be needed by this type of Component.
                  Missing arguments will cause a MissingFieldException to be raised.
                  Arguments connected_to (Component list) and depends_on are always used.
             If such a component actually already exists (same name, type, environment), it will NOT be reused. (there can be multiple instances)
        @raise MissingFieldException: you tried to create a new component without giving all the necesssary values.
        @raise FailedDependenciesCheckException: the target envt is not at the adequate version for this IS to be applied.
        @raise InconsistentComponentsException: the components do not all belong to the same environment.
        @raise NotAFullIS: only a full IS can create new components.
        @raise InadequateIS: at least one component given in target_components is not updated by this IS. 
        
        Example:
            to install an IS (FULL) on 2 existing IFPC folders and a new one :
            installOn([folder1, ('@FOLDER_COMMUN', IFPCFolder, {dependsOn: [ifpcproject1]}), folder3)    
        """
        create_mode = False
        
        ## Check arguments
        if type(target_components) != list or not isinstance(self, InstallableSet):
            raise Exception('Arguments incorrects ou incomplets %s' %(type(target_components)))
        
        for compo in target_components:
            if type(compo) == 'tuple':
                create_mode = True
                break
        
        ## Check envt
        envt = None
        if type(environment) == str:
            envt = Environment.objects.get(name=environment)
        elif type(environment) == Environment:
            envt = environment            
                              
        for compo in target_components:
            if isinstance(compo, Composant):
                if not envt in compo.environments.all():
                    raise InconsistentComponentsException(compo, envt)
        
        ## Check FULL if new components are to be created.
        if (create_mode and not self.is_full):
            raise NotAFullIS(self)
        
        
        ## Check : does the IS update those components ?
        for compo in target_components:
            name=None
            typec=None
            if isinstance(compo, Composant):
                name=compo.name
                typec=compo.type
            else:
                name=compo[0]
                print type(compo[1])
                typec=MageModelType.objects.get(name=type(compo[1]).__name__.lower())
            if self.acts_on.filter(component_name=name).filter(component_type=typec).count() != 1:
                raise InadequateIS(compo.leaf, self)
        
        ## Dep
        # TODO
        
        ## Build missing components
        # @todo : try/catch
        newCompo=[]                     ## Store new components : in case of error, they should be erased.
        endCompo=[]
        for compo in target_components:
            if isinstance(compo, Composant):
                endCompo.append(compo)
                continue
            
            c = compo[1](name=compo[0])
            for field, value in compo[2]:
                setattr(c, field, value)
            c.save()
            endCompo.append(c)
            newCompo.append(c)
            
        ## Register installation...
        i = Installation(installed_set=self, target_envt=envt, install_date=strftime('%Y-%m-%d %H:%M'))
        i.save()
        for compo in endCompo:
            ctv = self.acts_on.filter(component_name=compo.name).get(component_type=compo.type)
            cv = ComponentVersion(version = ctv, component = compo, installation = i)
            cv.save()
            
        i.save()
        
        return i
        
        
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

    
class InstallationAdmin(admin.ModelAdmin):    
    """Debug only. Installations should only be created through dedicated functions"""
    list_display = ('installable_set_name', 'target_envt', 'install_date', 'nb_modified_components')


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
admin.site.register(Installation, InstallationAdmin)
admin.site.register(ComponentTypeVersion, ComponentTypeVersionAdmin)