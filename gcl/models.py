# coding: utf-8
from django.db import models
from MAGE.ref.models import Composant
from MAGE.ref.models import MageModelType
from MAGE.ref.models import Environment
from django.contrib import admin
from datetime import date

###########################################################
## GCL
###########################################################

class ComponentTypeVersion(models.Model):
    version = models.CharField(max_length=40, core=True)
    component_type = models.ForeignKey(MageModelType, core=True)
    def __unicode__(self):
        return u'%s version %s' %(self.component_type, self.version)

class ComponentTypeVersionAdmin(admin.ModelAdmin):
    list_display = ('version', 'component_type')    


    
class InstallableSet(models.Model):
    name = models.CharField(max_length=40, verbose_name='Référence', unique=True)
    set_date = models.DateField(verbose_name='Date de réception', auto_now_add=True)
    acts_on = models.ManyToManyField(ComponentTypeVersion, verbose_name='Composants installés')
    ticket = models.IntegerField(max_length=6, verbose_name='Ticket lié', null=True ,blank=True)
    requirements = models.ManyToManyField(ComponentTypeVersion, verbose_name='Version de composants requises', related_name='requires', blank=True)
    is_full = models.BooleanField(verbose_name='Livraison annule et remplace (ou livraison initiale)', default='true')
    
    def __unicode__(self):
        return u'%s' %(self.name)
    
    def installOn(self, envt):
        """Full installation of the patch on an environment. All components patched/installed by the installableset
        must already be referenced, or this function will exit"""
        i = Installation(installed_set=self, target_envt=envt, install_date=date.today())
        for compver in self.acts_on.all():
            ## Type of component ty, patch to version ver
            ver = compver.version
            ty = compver.component_type
            
            ## Are there components of the right type in this envt ?
            envt_comps = Composant.objects.filter(type=ty, environments=envt)
            if envt_comps.count() == 0:
                return
                
            ## Create the installation object, so as to get its PK
            i.save()
            
            ## Retrieve all components of this type in this envt
            for comp_to_patch in envt_comps:
                ## Retrieve version <-> component association
                cv = ComponentVersion.objects.filter(version=ver, component = comp_to_patch)
                if cv.all().count() == 0:
                    cv = ComponentVersion(version = compver, component = comp_to_patch, installation = i)
                    cv.save()
                    
        
        
    def __cmp__(self):
        return 0



class Installation(models.Model):
    installed_set = models.ForeignKey(InstallableSet, verbose_name='Livraison appliquée ')
    target_envt = models.ForeignKey(Environment, verbose_name='Environnement ' )
    target_components = models.ManyToManyField(Composant, through='ComponentVersion', verbose_name='Résultats ')
    install_date = models.DateField(verbose_name='Date d\'installation ')
    ticket = models.IntegerField(max_length=6, verbose_name='Ticket lié ', blank=True, null=True)
    def _getNbTargetComponents(self):
        return self.target_components.count()
    nb_modified_components = property(_getNbTargetComponents)
    def _getInstallableSetName(self):
        return self.installed_set.name
    installable_set_name = property(_getInstallableSetName)
    
    def __unicode__(self):
        return '%s sur %s le %s' %(self.installed_set.name, self.target_envt.name, self.install_date)


class ChoiceInline(admin.StackedInline):
    model = Composant
    extra = 3
    
class InstallationAdmin(admin.ModelAdmin):    
    list_display = ('installable_set_name', 'target_envt', 'install_date', 'nb_modified_components')
    inline = ChoiceInline



class ComponentVersion(models.Model):
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
    snapshot_date = models.DateField(verbose_name='Date de prise de la photo', auto_now_add=True)
    
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





class UndefinedVersion(Exception):
    def __init__(self, comp):
        self.comp = comp
    def __str__(self):
        return 'Version non definie pour le composant %s' %(self.comp)


"""Add a version property to component objects"""
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


## Register into admin interface
admin.site.register(Installation, InstallationAdmin)
admin.site.register(ComponentTypeVersion, ComponentTypeVersionAdmin)