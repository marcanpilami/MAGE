# coding: utf-8
""" Logical components and service offers """

## Django imports
from django.db import models


################################################################################
## SLA object
################################################################################

class SLA(models.Model):
    rto = models.IntegerField()
    rpo = models.IntegerField()
    avalability = models.FloatField()
    #closed =
    open_at = models.TimeField()
    closes_at = models.TimeField()

    class Meta:
        verbose_name = 'SLA'
        verbose_name_plural = 'SLA'


################################################################################
## Constraints on environment instantiation
################################################################################

class LogicalComponent(models.Model):
    name = models.CharField(max_length=100, verbose_name='nom')
    description = models.CharField(max_length=500)
    application = models.ForeignKey('Application', on_delete=models.CASCADE)
    scm_trackable = models.BooleanField(default=True)
    active = models.BooleanField(default=True, verbose_name=u'utilisé')
    ref1 = models.CharField(max_length=20, verbose_name=u'reférence 1', blank=True, null=True)
    ref2 = models.CharField(max_length=20, verbose_name=u'reférence 2', blank=True, null=True)
    ref3 = models.CharField(max_length=20, verbose_name=u'reférence 3', blank=True, null=True)

    def __str__(self):
        return u'%s' % (self.name)

    class Meta:
        verbose_name = u'composant logique'
        verbose_name_plural = u'composants logiques'

class ComponentImplementationClass(models.Model):
    """ An implementation offer for a given service. """
    name = models.CharField(max_length=100, verbose_name='code')

    description = models.CharField(max_length=500)
    implements = models.ForeignKey(LogicalComponent, related_name='implemented_by', verbose_name=u'composant logique implémenté', on_delete=models.CASCADE)
    sla = models.ForeignKey(SLA, blank=True, null=True, on_delete=models.CASCADE)
    technical_description = models.ForeignKey('ImplementationDescription', related_name='cic_set', verbose_name=u'description technique', on_delete=models.CASCADE)
    ref1 = models.CharField(max_length=20, verbose_name=u'reférence 1', blank=True, null=True)
    ref2 = models.CharField(max_length=20, verbose_name=u'reférence 2', blank=True, null=True)
    ref3 = models.CharField(max_length=20, verbose_name=u'reférence 3', blank=True, null=True)
    active = models.BooleanField(default=True, verbose_name=u'utilisé')

    def __str__(self):
        return u'%s' % self.name

    class Meta:
        verbose_name = u'offre implémentant un composant logique'
        verbose_name_plural = u'offres implémentant des composants logiques'
