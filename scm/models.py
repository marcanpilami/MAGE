# coding: utf-8

## GCL

from django.db import models
from ref.models import ComponentInstance, LogicalComponent, ComponentImplementationClass, Environment
from exceptions import MageScmUndefinedVersionError

class InstallableSet(models.Model):
    """Référentiel GCL : ensemble pouvant être installé 
    Destiné à servir de clase de base. (par ex pour : patch, sauvegarde...)"""
    name = models.CharField(max_length=40, verbose_name=u'référence', unique=True)
    description = models.CharField(max_length=1000, verbose_name=u'résumé du contenu', unique=True)
    set_date = models.DateTimeField(verbose_name=u'date de réception', auto_now_add=True)
    # Through related_name: set_content
    #ticket = models.IntegerField(max_length=6, verbose_name='ticket lié', null=True , blank=True)
    
    is_full = models.BooleanField(verbose_name='livraison annule et remplace (ou livraison initiale)', default='true')
    #data_loss = models.BooleanField(verbose_name=u'Entraine des pertes de données', default='false')
    
    def __unicode__(self):
        return u'%s' % (self.name)


    
class LogicalComponentVersion(models.Model):
    version = models.CharField(max_length=50)
    logical_component = models.ForeignKey(LogicalComponent)

class InstallationMethod(models.Model):
    script_to_run = models.CharField(max_length=254)
    halts_service = models.BooleanField(default=True)
    method_compatible_with = models.ManyToManyField(ComponentImplementationClass)
    
class InstallableItem(models.Model):
    what_is_installed = models.ForeignKey(LogicalComponentVersion, related_name='installed_by')
    how_to_install = models.ForeignKey(InstallationMethod)
    belongs_to_set = models.ForeignKey(InstallableSet, related_name='set_content')
    # Add a property to access compatible envt types
    
    def __unicode__(self):
        return u'Installation of [%s] in version [%s] (%s dependencies with other components'' versions)' % (self.what_is_installed.logical_component.name, self.what_is_installed.version, self.dependencies.count())

class ItemDependency(models.Model):
    OPERATOR_CHOICES = (('>=', '>='),
                        ('<=', '<='),
                        ('==', '=='))
    installable_item = models.ForeignKey(InstallableItem, related_name='dependencies')
    depends_on_version = models.ForeignKey(LogicalComponentVersion)
    operator = models.CharField(max_length=2, choices=OPERATOR_CHOICES)
    
    def __unicode__(self):
        return u'dépendance de [%s] envers [%s en version %s %s]' % (self.installable_item.what_is_installed.logical_component.name, self.depends_on_version.logical_component.name,
                                                                 self.operator, self.depends_on_version.version)

class SetDependency(models.Model):
    OPERATOR_CHOICES = (('>=', '>='),
                        ('<=', '<='),
                        ('==', '=='))
    installable_set = models.ForeignKey(InstallableSet, related_name='requirements')
    depends_on_version = models.ForeignKey(LogicalComponentVersion)
    operator = models.CharField(max_length=2, choices=OPERATOR_CHOICES)
    
    def __unicode__(self):
        return u'IS [%s] requires [%s in version %s %s]' % (self.installable_set.name, self.depends_on_version.logical_component.name,
                                                                 self.operator, self.depends_on_version.version)

class Installation(models.Model):
    installed_set = models.ForeignKey(InstallableSet, verbose_name='livraison appliquée ')
    asked_in_ticket = models.IntegerField(max_length=6, verbose_name='ticket lié ', blank=True, null=True)
    install_date = models.DateTimeField(verbose_name='date d\installation ')

    def __unicode__(self):
        return '%s sur %s le %s' % (self.installed_set.name, self.target_envt.name, self.install_date)
        
class ComponentInstanceConfiguration(models.Model):
    component_instance = models.ForeignKey(ComponentInstance, related_name='configurations')
    result_of = models.ForeignKey(InstallableItem)
    part_of_installation = models.ForeignKey(Installation, related_name='modified_components')
    created_on = models.DateTimeField()
    install_failure = models.BooleanField(default=False)
    
    def __unicode__(self):
        return u'At %s, component %s was at version %s' % (self.created_on, self.component_instance.name, self.result_of.version.version)
    
class Tag(models.Model):
    name = models.CharField(max_length=40, verbose_name=u'référence', unique=True)
    versions = models.ManyToManyField(LogicalComponentVersion, verbose_name=u'version des composants')
    from_envt = models.ForeignKey(Environment)
    snapshot_date = models.DateTimeField(verbose_name=u'date de prise de la photo', auto_now_add=True)

    def __unicode__(self):
        return u'Tag n°%s - %s (concerne %s composants)' % (self.pk, self.name, self.versions.count())



#######################################################################################
## Update Component class with GCL objects
#######################################################################################

## Add a version property to component objects   
def getLatestCIC(comp):
    """@return: the latest installed LogicalComponentVersion (LCV) on the Component"""
    try:
        return comp.configurations.latest('pk')
    except:
        raise MageScmUndefinedVersionError(comp)
def getComponentVersion(comp):
    """@return: the latest installed ICV on the Component"""
    return getLatestCIC(comp).result_of.what_is_installed
def getComponentVersionText(comp):
    try:
        return getComponentVersion(comp).version
    except MageScmUndefinedVersionError:
        return "inconnue"
ComponentInstance.version = property(getComponentVersionText)  
ComponentInstance.latest_cic = property(getLatestCIC)
