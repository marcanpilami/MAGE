# coding: utf-8

###############################################################################
##
## Minimalist parameters handling
##    
###############################################################################


## Python imports
import sys

## Django imports
from django.db import models
from django.contrib import admin
from django.conf import settings
from django.contrib.contenttypes.models import ContentType



##########################################################################
## Exceptions
##########################################################################

class ParamNotFound(Exception):
    def __init__(self, kwargs):
        self.query = kwargs
    def __str__(self):
        return 'Parametre mal specifie : %s' %self.query

class DuplicateParam(Exception):
    def __init__(self, param):
        self.param = param
    def __str__(self):
        return 'il existe deja un parametre repondant a cette definition : %s' %self.param



##########################################################################
## Model
##########################################################################

# Funny hack to create a "dynamic" static list...
def choice_list():
    for application in settings.INSTALLED_APPS:
        app_name = application.split('.')[1]
        if app_name == 'contrib': continue
        yield (app_name, app_name)
        
class MageParam(models.Model):
    key = models.CharField(max_length = 30, verbose_name = u'clé')
    app = models.CharField(max_length = 5, verbose_name = u'application', choices = choice_list())
    value = models.CharField(max_length = 100, verbose_name = u'valeur')
    
    description = models.CharField(max_length = 200, blank = True, null = True, verbose_name = u'description')
    default_value = models.CharField(max_length = 100, blank = True, null = True, verbose_name = u'valeur par défaut')
    model = models.ForeignKey(ContentType, blank = True, null = True, verbose_name = u'modèle concerné')
    axis1 = models.CharField(max_length = 30, verbose_name = u'classification optionnelle', blank = True, null = True)
    
    def __unicode__(self):
        return u'[%s] %s : %s' %(self.app, self.key, self.value)
    
    class Meta():
        verbose_name = u'paramètre'
        verbose_name_plural = u'paramètres'
        ordering = ['app', 'key',]
        unique_together = [('key', 'app', 'model', 'axis1'),]
    

class MageParamAdmin(admin.ModelAdmin):
    list_display = ['app', 'key', 'value', 'model', 'axis1', 'description',]
    search_fields = ['app', 'key', 'value', 'axis1', ]
    list_filter = ['app', ]#'model',]

admin.site.register(MageParam, MageParamAdmin)



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
    if others and others.has_key('app'): app = others['app']
    else: app = sys._getframe(1).f_globals['__name__'].split('.')[1]
    filter = others or {}
    filter['app'] = app  
    filter['key'] = key
    
    try:
        return MageParam.objects.get(**filter).value
    except (MageParam.DoesNotExist, MageParam.MultipleObjectsReturned):
        raise ParamNotFound(filter)


def setParam(key, value, **others):
    """ 
        Creates a new parameter
        
        @return: nothing.
        @raise DjangoExceptions: many Django model exceptions may be raised in this function
        @raise DuplicateParam:  in case of unicity constraint violation
    """
    if others and others.has_key('app'): app = others['app']
    else: app = sys._getframe(1).f_globals['__name__'].split('.')[1]
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
    app = sys._getframe(1).f_globals['__name__'].split('.')[1]
    return MageParam.objects.filter(app = app)
