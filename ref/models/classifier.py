# coding: utf-8
""" models structuring the others: applicaion, project... """

## Django imports
from django.db import models


class Project(models.Model):
    """ 
        referential objects may optionally be classified inside projects, defined by a code name
        and containing a description
    """
    name = models.CharField(max_length=100, unique=True)
    alternate_name_1 = models.CharField(max_length=100, null=True, blank=True)
    alternate_name_2 = models.CharField(max_length=100, null=True, blank=True)
    alternate_name_3 = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=500)

    class Meta:
        verbose_name = u'projet'
        verbose_name_plural = u'projets'

    def __str__(self):
        return self.name

class Application(models.Model):
    name = models.CharField(max_length=100, unique=True)
    alternate_name_1 = models.CharField(max_length=100, null=True, blank=True)
    alternate_name_2 = models.CharField(max_length=100, null=True, blank=True)
    alternate_name_3 = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=500)
    project = models.ForeignKey(Project, null=True, blank=True, related_name='applications', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class EnvironmentType(models.Model):
    """ The way logical components are instanciated"""
    name = models.CharField(max_length=100, verbose_name='Nom', unique=True)
    description = models.CharField(max_length=500, verbose_name='description')
    short_name = models.CharField(max_length=10, verbose_name='code', db_index=True)
    sla = models.ForeignKey('SLA', blank=True, null=True, on_delete=models.CASCADE)
    implementation_patterns = models.ManyToManyField('ComponentImplementationClass', blank=True)
    chronological_order = models.IntegerField(default=1, verbose_name='ordre d\'affichage')
    default_show_sensitive_data = models.BooleanField(default=False, verbose_name="afficher les informations sensibles")

    def __get_cic_list(self):
        return ','.join([ i.name for i in self.implementation_patterns.all()])
    cic_list = property(__get_cic_list)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = u'classification des environnements'
        verbose_name_plural = u'classifications des environnements'
