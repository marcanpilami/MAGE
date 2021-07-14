# coding: utf-8
'''
    @license: Apache License, Version 2.0
    @copyright: 2007-2013 Marc-Antoine Gouillart
    @author: Marc-Antoine Gouillart
'''

## Python imports
import os
import glob

## Django imports
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.utils.timezone import now
from MAGE.settings import MEDIA_ROOT

## MAGE imports
from ref.models import ComponentInstance, LogicalComponent, ComponentImplementationClass, Environment
from scm.exceptions import MageScmUnrelatedItemsError, MageScmFailedInstanceDependencyCheck, MageScmFailedEnvironmentDependencyCheck, MageScmUndefinedVersionError
from MAGE.exceptions import MageError
from django.db.models.query import Prefetch


################################################################################
## The sets
################################################################################

def __isetdatafilename__(iset, filename):
        ext = os.path.splitext(filename)[1]
        d = now().strftime("%Y%m%d_%H%M%S")
        return 'installablesets/' + slugify(d + '_' + iset.name) + ext

class InstallableSet(models.Model):
    """Référentiel GCL : ensemble pouvant être installé 
    Destiné à servir de clase de base. (par ex pour : patch, sauvegarde...)"""
    name = models.CharField(max_length=40, verbose_name=u'référence', unique=True)
    description = models.CharField(max_length=1000, verbose_name=u'résumé du contenu', unique=False, blank=True, null=True)
    set_date = models.DateTimeField(verbose_name=u'date de réception', auto_now_add=True)
    ticket_list = models.CharField(max_length=100, verbose_name='ticket(s) lié(s) séparés par une virgule', null=True , blank=True)
    STATUS_CHOICES = ((1, 'VALIDATED'), (2, 'TESTED'), (3, 'HANDEDOFF'))
    status = models.IntegerField(choices=STATUS_CHOICES, default=3)
    location_data_1 = models.CharField(max_length=100, blank=True, null=True)
    location_data_2 = models.CharField(max_length=100, blank=True, null=True)
    location_data_3 = models.CharField(max_length=100, blank=True, null=True)
    location_data_4 = models.CharField(max_length=100, blank=True, null=True)
    datafile = models.FileField(upload_to=__isetdatafilename__, blank=True, null=True, verbose_name='fichier')
    # Through related_name: set_content

    removed = models.DateTimeField(null=True, blank=True)
    def is_available(self):
        return self.removed == None
    available = property(is_available)
    is_available.admin_order_field = 'removed'

    def __str__(self):
        return u'%s' % (self.name)

    def check_prerequisites(self, envt_name, ii_selection=()):
        failures = []
        if len(ii_selection) == 0:
            ii_selection = self.set_content.all()
        for ii in self.set_content.all():
            try:
                ii.check_prerequisites(envt_name, ii_selection)
            except MageScmFailedEnvironmentDependencyCheck as e:
                failures.extend(e.failing_dep)

        if len(failures) == 0:
            return True
        else:
            raise MageScmFailedEnvironmentDependencyCheck(envt_name, self, failures)

    class Meta:
        permissions = (('validate_installableset', 'can change the status of the set'),
                       ('install_installableset', 'can reference an installation'),)


class Delivery(InstallableSet):
    pass

class BackupSet(InstallableSet):
    from_envt = models.ForeignKey(Environment, blank=True, null=True, on_delete=models.CASCADE)


################################################################################
## The version object
################################################################################

class LogicalComponentVersion(models.Model):
    version = models.CharField(max_length=50)
    logical_component = models.ForeignKey(LogicalComponent, related_name='versions', on_delete=models.CASCADE)

    def __str__(self):
        return u'%s in version [%s]' % (self.logical_component.name, self.version)

    def compare(self, lcv2, strict=False):
        """
            Order relation between LCV objects
            
            The relation is deduced from the dependencies (as they can be seen as links between the LCV).
            This function will not detect inconsistencies in dependencies (such as loops),
            as it will return the first result it will find. (This is, among others, to prevent infinite 
            loops and fasten things.)
            
            It is possible to compare LCV of different model classes, since there can be relationships 
            between different classes.
            
            @return: 1 if the lcv1 should be installed AFTER the lcv2 (lcv1 > lcv2)
                     0 if it doesn't matter ("equality")
                    -1 if the ctv1 should be installed BEFORE the ctv2 (lcv1 < lcv2)
            
            @note: do NOT overload __cmp__ or eq with this function as they are already used by Django internals.
        """
        lcv1 = self
        if not strict:
            try: return lcv1.__compareWith(lcv2)
            except MageScmUnrelatedItemsError: return 0
        else:
            return lcv1.__compareWith(lcv2)

    def __compareWith(self, lcv2, __reverseCall=False, __alreadydone=None, before=None, level=0):
        """ 
            The function actually doing the comparison. 
        
            Here, equality (0) has a strict meaning, and if the two LCVs are unrelated an MageScmUnrelatedItemsError is raised 
            
            before == True => A <= chain (comes before)
            before == False => A >= or == chain (comes after)
        """

        ## Argument check
        lcv1 = self
        if not isinstance(lcv1, LogicalComponentVersion) or not isinstance(lcv2, LogicalComponentVersion):
            raise MageError("Arguments must be logical component version objects")

        ## No more than <param> recursion levels. Give up as if no relations existed between the two (which is likely).
        #if level > 20:
        #    raise MageScmUnrelatedItemsError(lcv1, lcv2)

        ## Loop guard & failure termination condition
        c = (lcv1.pk, lcv2.pk)
        if not __alreadydone:
            __alreadydone = []
        if c in __alreadydone:
            raise MageScmUnrelatedItemsError(lcv1, lcv2)
        __alreadydone.append(c)

        ## Trivial equality condition (success termination condition too)
        if (lcv1.logical_component_id == lcv2.logical_component_id) and (lcv1.version == lcv2.version):
            return 0

        ## Loop on all the InstallableItems that install lcv1
        for ii in lcv1.installed_by.all().prefetch_related(Prefetch('dependencies', ItemDependency.objects.select_related('depends_on_version'))):
            ## Loop on all the requirements of the installable set
            for dep in ii.dependencies.all() :
                ## Only use compatible dependencies that are part of an unbroken chain
                if before is not None:
                    if not __reverseCall and not ((before and dep.operator in ('<=',)) or (not before and dep.operator in ('==', '>='))):
                        continue
                    if __reverseCall and not ((before and dep.operator in ('==', '>=')) or (not before and dep.operator in ('<=',))):
                        continue
                else:
                    newbefore = dep.operator == '<='
                    if __reverseCall:
                        newbefore = not newbefore

                ## Success termination condition: we have found lcv2
                if dep.depends_on_version == lcv2:
                    return (-1 if dep.operator == '<=' else 1)

                ## Recursion
                try:
                    return dep.depends_on_version.__compareWith(lcv2, __reverseCall, __alreadydone, before if before is not None else newbefore, level + 1)
                except MageScmUnrelatedItemsError:
                    continue  ## Nothing can be deduced from this relation - go on to the others

                ## If here : the dependency that was analysed does not provide any useful relationship. Let's loop to the next one!

        ## If here : no relationship has given fruit. Let's try the reverse relationship analysis (loop is stopped by the loop guard)
        return -lcv2.__compareWith(lcv1, not __reverseCall, __alreadydone, before)


################################################################################
## Set contents
################################################################################

class InstallationMethod(models.Model):
    name = models.CharField(max_length=254, verbose_name=u'nom')
    halts_service = models.BooleanField(default=True, verbose_name=u'arrêt de service')
    method_compatible_with = models.ManyToManyField(ComponentImplementationClass, related_name='installation_methods', verbose_name=u'permet d\'installer')
    available = models.BooleanField(default=True, verbose_name=u'disponible')
    restoration_only = models.BooleanField(default=False, verbose_name=u'opération purement de restauration')
    checkers = models.ManyToManyField('PackageChecker', related_name='used_in', blank=True)

    def __str__(self):
        a = ""
        if not self.available:
            a = "OBSOLETE - "
        return u'%s%s' % (a, self.name)  #, ",".join([ i.name for i in self.method_compatible_with.all()]))

    def check_package(self, package_file, logical_component):
        for checker in self.checkers.all():
            checker.check_package(package_file, logical_component, self)

    class Meta:
        verbose_name = u'méthode d\'installation'
        verbose_name_plural = u'méthodes d\'installation'

class BackupItem(models.Model):
    """ Backup can contain component instances that are NOT SCM tracked.
        This object represents these contents """
    backupset = models.ForeignKey(BackupSet, related_name='all_items', on_delete=models.CASCADE)
    instance = models.ForeignKey(ComponentInstance, on_delete=models.CASCADE)
    related_scm_install = models.ForeignKey('InstallableItem', blank=True, null=True, on_delete=models.CASCADE)  # null if not SCM-tracked
    instance_configuration = models.ForeignKey('ComponentInstanceConfiguration', blank=True, null=True, on_delete=models.CASCADE)

def __iidatafilename__(ii, filename):
        ext = os.path.splitext(filename)[1]
        d = ii.belongs_to_set.set_date.strftime("%Y%m%d_%H%M%S")
        return 'installablesets/' + slugify(d + '_' + ii.belongs_to_set.name) + '/' + slugify(ii.what_is_installed.logical_component.name) + ext

class InstallableItem(models.Model):
    what_is_installed = models.ForeignKey(LogicalComponentVersion, related_name='installed_by', on_delete=models.CASCADE)
    how_to_install = models.ManyToManyField(InstallationMethod, verbose_name='peut s\'installer avec')
    belongs_to_set = models.ForeignKey(InstallableSet, related_name='set_content', on_delete=models.CASCADE)
    is_full = models.BooleanField(verbose_name='installation de zéro', default=False)
    data_loss = models.BooleanField(verbose_name=u'entraine des pertes de données', default=False)
    datafile = models.FileField(verbose_name='fichier', upload_to=__iidatafilename__, blank=True, null=True)

    def __str__(self):
        if self.id is not None:
            return u'Installation of [%s] in version [%s] (%s dependencies with other components'' versions)' % (self.what_is_installed.logical_component.name, self.what_is_installed.version, self.dependencies.count())
        else:
            return u'installable item'

    def __find_existing_file(self):
        if MEDIA_ROOT is None or MEDIA_ROOT == "":
            return
        files = glob.glob(MEDIA_ROOT + 'installablesets/*_' + slugify(self.belongs_to_set.name) + '/' + slugify(self.what_is_installed.logical_component.name) + '.*')
        if len(files) == 1:
            self.datafile = os.path.relpath(files[0], MEDIA_ROOT)

    def save(self):
        if self.pk is None and not self.datafile.name:
            self.__find_existing_file()
        super(InstallableItem, self).save()

    class Meta:
        permissions = (('download_ii', 'can download the installation file'),)

    def dependsOn(self, lcv, operator='>='):
        if not self.dependencies.filter(depends_on_version_id=lcv.id, operator=operator).exists():
            ide = ItemDependency(installable_item=self, depends_on_version=lcv, operator=operator)
            ide.save()

    def check_prerequisites(self, envt_name, installed_along_ii=()):
        installed_along_version = [i.what_is_installed for i in installed_along_ii]

        failures = []
        for dep in self.dependencies.all():
            ## Check it is not installed alongside this II - in which case it is OK
            if dep.depends_on_version in installed_along_version:
                continue

            ## Check history
            rs = ComponentInstance.objects.filter(environments__name=envt_name,
                                          instanciates__implements=dep.depends_on_version.logical_component,
                                          deleted=False)
            if rs.count() == 0:
                failures.append(MageScmFailedInstanceDependencyCheck(dep.depends_on_version.logical_component.name, dep, 'there is no compatible component in this environment [Technical data: logical component [%s], method name %s]' % (dep.depends_on_version.logical_component, self.how_to_install.all())))
                continue

            for compo in rs.all():
                ## Retrieve current version
                try:
                    ver = compo.latest_cic.result_of.what_is_installed
                except MageScmUndefinedVersionError:
                    failures.append(MageScmFailedInstanceDependencyCheck(compo, dep, 'No version is defined for this component - cannot check dependency!'))
                    continue

                ## Check current version against dependency
                try:
                    compa = ver.compare(dep.depends_on_version, strict=True)
                except MageScmUnrelatedItemsError:
                    failures.append(MageScmFailedInstanceDependencyCheck(compo, dep, 'version [%s] is unrelated to the required version' % ver.version))
                    continue

                if dep.operator == '==' and compa != 0:
                    failures.append(MageScmFailedInstanceDependencyCheck(compo, dep, 'incorrect version - it\'s [%s]' % ver.version))
                    continue

                if dep.operator == '>=' and compa < 0:
                    failures.append(MageScmFailedInstanceDependencyCheck(compo, dep, 'incorrect version - it\'s [%s]' % ver.version))
                    continue

                if dep.operator == '<=' and compa > 0:
                    failures.append(MageScmFailedInstanceDependencyCheck(compo, dep, 'incorrect version - it\'s [%s]' % ver.version))
                    continue

        if len(failures) == 0:
            return True
        else:
            raise MageScmFailedEnvironmentDependencyCheck(envt_name, self, failures)


class ItemDependency(models.Model):
    OPERATOR_CHOICES = (('>=', '>='),
                        ('<=', '<='),
                        ('==', '=='))
    installable_item = models.ForeignKey(InstallableItem, related_name='dependencies', on_delete=models.CASCADE)
    depends_on_version = models.ForeignKey(LogicalComponentVersion, on_delete=models.CASCADE)
    operator = models.CharField(max_length=2, choices=OPERATOR_CHOICES, default='==')

    def __str__(self):
        return u'dépendance de [%s] envers [%s en version %s %s]' % (self.installable_item.what_is_installed.logical_component.name, self.depends_on_version.logical_component.name,
                                                                 self.operator, self.depends_on_version.version)

class SetDependency(models.Model):
    OPERATOR_CHOICES = (('>=', '>='),
                        ('<=', '<='),
                        ('==', '=='))
    installable_set = models.ForeignKey(InstallableSet, related_name='requirements', on_delete=models.CASCADE)
    depends_on_version = models.ForeignKey(LogicalComponentVersion, on_delete=models.CASCADE)
    operator = models.CharField(max_length=2, choices=OPERATOR_CHOICES)

    def __str__(self):
        return u'IS [%s] requires [%s in version %s %s]' % (self.installable_set.name, self.depends_on_version.logical_component.name,
                                                                 self.operator, self.depends_on_version.version)

class Installation(models.Model):
    installed_set = models.ForeignKey(InstallableSet, verbose_name='livraison appliquée ', on_delete=models.CASCADE)
    asked_in_ticket = models.CharField(max_length=10, verbose_name='ticket lié ', blank=True, null=True)
    install_date = models.DateTimeField(verbose_name='date d\installation ')

    def __str__(self):
        return '%s sur %s  le %s' % (self.installed_set.name, [i.component_instance.environments.all() for i in self.modified_components.all()], self.install_date)

@receiver(post_save, sender=Installation)
def check_validation_on_install(sender, instance, raw, **kwargs):
    if raw:
        return
    if instance.installed_set.status == 3:
        instance.installed_set.status = 1
        instance.installed_set.save()

class ComponentInstanceConfiguration(models.Model):
    component_instance = models.ForeignKey(ComponentInstance, related_name='configurations', on_delete=models.CASCADE)
    result_of = models.ForeignKey(InstallableItem, on_delete=models.CASCADE)
    part_of_installation = models.ForeignKey(Installation, related_name='modified_components', on_delete=models.CASCADE)
    created_on = models.DateTimeField()
    install_failure = models.BooleanField(default=False)

    def __str__(self):
        return u'At %s, component %s was at version %s' % (self.created_on, self.component_instance.name, self.result_of.what_is_installed.version)

class Tag(models.Model):
    name = models.CharField(max_length=40, verbose_name=u'référence', unique=True)
    versions = models.ManyToManyField(LogicalComponentVersion, verbose_name=u'version des composants')
    from_envt = models.ForeignKey(Environment, on_delete=models.CASCADE)
    snapshot_date = models.DateTimeField(verbose_name=u'date de prise de la photo', auto_now_add=True)

    def __str__(self):
        return u'Tag n°%s - %s (concerne %s composants)' % (self.pk, self.name, self.versions.count())


#######################################################################################
## Backup parameters
#######################################################################################

class BackupRestoreMethod(models.Model):
    """
        BMRs are needed because there may be multiple InstallationMethods available for the same CIC. Therefore, 
        we need a mean to know which InstallationMethod to use to restore a backup.
        There cannot be more than one BMR per CIC (we are talking default restoration method - only one default!)
    """
    method = models.ForeignKey(InstallationMethod, on_delete=models.CASCADE)
    target = models.ForeignKey(ComponentImplementationClass, related_name='restore_methods', verbose_name='cible', on_delete=models.CASCADE)

    class Meta:
        verbose_name = u'méthode de restauration par défaut'
        verbose_name_plural = 'méthodes de restauration par défaut'

@receiver(post_save, sender=ComponentImplementationClass)
def create_brm(sender, instance, raw, **kwargs):
    if raw:
        # loading fixtures - this means the BRM will also be loaded, so no need to create it.
        return
    cic = instance
    im, created = InstallationMethod.objects.get_or_create(name='restore operation for ' + cic.name, halts_service=True, restoration_only=True)
    if created:
        im.save()
        im.method_compatible_with.add(instance)
    m, created = BackupRestoreMethod.objects.get_or_create(target=cic, method=im)
    if created:
        m.save()


#######################################################################################
## DSL elements
#######################################################################################

class PackageChecker(models.Model):
    module = models.CharField(max_length=200, verbose_name='Python module containing the checker class')
    name = models.CharField(max_length=200, verbose_name='Python checker class name')
    description = models.CharField(max_length=200, verbose_name='description')

    def check_package(self, package_file, logical_component, installation_method):
        checker_impl = getattr(__import__(self.module, fromlist=[self.name]), self.name)
        checker_impl.check(checker_impl(), package_file, logical_component, installation_method)

    def __str__(self):
        return self.description


class PackageCheckerBaseImpl(object):
    description = None
    def check(self, fileinfo, logical_component, installation_method):
        raise NotImplemented()


#######################################################################################
## Update Component class with GCL objects
#######################################################################################

## Add a version properties to component objects
def getLatestCIC(comp):
    """@return: the latest installed ComponentInstanceConguration (CIC) on the Component"""
    try:
        return comp.configurations.latest('pk')
    except ComponentInstanceConfiguration.DoesNotExist:
        raise MageScmUndefinedVersionError(comp)
def getCICAtDate(comp, date):
    try:
        return comp.configurations.filter(created_on__lte=date).order_by('created_on', 'pk').reverse()[0]
    except IndexError :
        raise MageScmUndefinedVersionError(comp)
def getCICAtDateSafe(comp, date):
    try:
        return getCICAtDate(comp, date)
    except MageScmUndefinedVersionError:
        return None
def getVersionObjectAtDateSafe(comp, date):
    try:
        return getCICAtDate(comp, date).result_of.what_is_installed
    except MageScmUndefinedVersionError:
        return None
def getComponentVersion(comp):
    """@return: the latest installed LCV on the Component"""
    return getLatestCIC(comp).result_of.what_is_installed
def getComponentVersionText(comp):
    try:
        return getComponentVersion(comp).version
    except MageScmUndefinedVersionError:
        return "inconnue"
def getComponentVersionObjectSafe(comp):
    try:
        return getComponentVersion(comp)
    except MageScmUndefinedVersionError:
        return None
ComponentInstance.version = property(getComponentVersionText)
ComponentInstance.version_object_safe = property(getComponentVersionObjectSafe)
ComponentInstance.latest_cic = property(getLatestCIC)
ComponentInstance.cic_at_safe = getCICAtDateSafe
ComponentInstance.version_at = getCICAtDate
ComponentInstance.version_at_safe = getVersionObjectAtDateSafe
