# coding: utf-8

"""
    MAGE parameter module models and helpers file.
    Useful functions (part of the API) are :
        - getParam
        - setParam
        - getMyParams
        - setOrCreateParam

    @license: Apache License, Version 2.0
    @copyright: 2007-2013 Marc-Antoine Gouillart
    @author: Marc-Antoine Gouillart
"""

###############################################################################
##
## Minimalist parameters handling
##
###############################################################################


## Python imports
import sys

## Django imports
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType



##########################################################################
## Exceptions
##########################################################################

class ParamNotFound(Exception):
    def __init__(self, kwargs):
        self.query = kwargs
    def __str__(self):
        return u'Parametre mal specifié : %s' % self.query

class DuplicateParam(Exception):
    def __init__(self, param):
        self.param = param
    def __str__(self):
        return u'il existe deja un parametre répondant a cette définition : %s' % self.param



##########################################################################
## Model
##########################################################################

# Funny hack to create a "dynamic" static list...
def choice_list():
    for application in settings.INSTALLED_APPS:
        app_name = application.split('.')[0]
        if app_name in ('django', 'crispy_forms', 'debug_toolbar', 'django_extensions', 'mozilla_django_oidc'): continue
        yield (app_name, app_name)

class MageParamManager(models.Manager):
    def get_by_natural_key(self, key, app, model_app_label, model, axis1):
        return self.get(key=key, app=app, model__app_label=model_app_label, model__model=model, axis1=axis1)

class MageParam(models.Model):
    key = models.CharField(max_length=30, verbose_name=u'clé')
    app = models.CharField(max_length=5, verbose_name=u'application', choices=choice_list())
    value = models.CharField(max_length=100, verbose_name=u'valeur')

    description = models.CharField(max_length=200, blank=True, null=True, verbose_name=u'description')
    default_value = models.CharField(max_length=100, blank=True, null=True, verbose_name=u'valeur par défaut')
    model = models.ForeignKey(ContentType, blank=True, null=True, verbose_name=u'modèle concerné', on_delete=models.CASCADE)
    axis1 = models.CharField(max_length=30, verbose_name=u'classification optionnelle', blank=True, null=True)

    restricted = models.BooleanField(default=False)

    def __str__(self):
        return u'[%s] %s : %s' % (self.app, self.key, self.value)

    def natural_key(self):
        return (self.key, self.app) +  (self.model.natural_key() if self.model else (None, None)) + (self.axis1,)

    objects = MageParamManager()

    class Meta:
        verbose_name = u'paramètre global'
        verbose_name_plural = u'paramètres globaux'
        ordering = ['app', 'key', ]
        unique_together = [('key', 'app', 'model', 'axis1'), ]


##########################################################################
## API
##########################################################################

def getParam(key, **others):
    """
        Retrieves a parameter.
        This function hits the database, so it should be called as little as possible.
        
        @return: the parameter value as a string (unicode).
        @raise ParamNotFound: if the param cannot be found, or if multiple params were found. 
    """
    if others and 'app' in others: app = others['app']
    else: app = sys._getframe(1).f_globals['__name__'].split('.')[0]
    filters = others or {}
    filters['app'] = app
    filters['key'] = key

    try:
        return MageParam.objects.get(**filters).value
    except (MageParam.DoesNotExist, MageParam.MultipleObjectsReturned):
        raise ParamNotFound(filters)

def setOrCreateParam(key, value, **others):
    if others and 'app' in others: app = others['app']
    else: app = sys._getframe(1).f_globals['__name__'].split('.')[0]
    args = others or {}
    args['key'] = key
    args['app'] = app

    prm = MageParam.objects.get_or_create(**args)[0]
    prm.value = value
    prm.save()

def setParam(key, value, **others):
    """ 
        Creates a new parameter
        
        @return: nothing.
        @raise DjangoExceptions: many Django model exceptions may be raised in this function
        @raise DuplicateParam:  in case of unicity constraint violation
    """
    if others and 'app' in others: app = others['app']
    else: app = sys._getframe(1).f_globals['__name__'].split('.')[0]
    args = others or {}
    args['key'] = key
    args['app'] = app
    args['value'] = value

    try:
        prm = getParam(**args) # Compulsory, as constraints on nullable fields may not be implemented in the db.
    except ParamNotFound:
        p = MageParam(**args)
        p.save()
        return
    raise DuplicateParam(prm)


def getMyParams():
    """
        @return: all the parameters of an application
    """
    app = sys._getframe(1).f_globals['__name__'].split('.')[0]
    return MageParam.objects.filter(app=app)

def getAllParams():
    """
        @return: all the parameters of all applications
    """
    return MageParam.objects.all()
