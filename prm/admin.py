# coding: utf-8
'''
    @license: Apache License, Version 2.0
    @copyright: 2007-2013 Marc-Antoine Gouillart
    @author: Marc-Antoine Gouillart
'''

from ref import admin
from models import MageParam

class MageParamAdmin(admin.ModelAdmin):
    list_display = ['app', 'key', 'value', 'model', 'axis1', 'description',]
    search_fields = ['app', 'key', 'value', 'axis1', ]
    list_filter = ['app', ]#'model',]

admin.site.register(MageParam, MageParamAdmin)

