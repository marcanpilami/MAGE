'''
Created on 8 mars 2013

@author: Marc-Antoine
'''

from django.contrib import admin
from models import MageParam

class MageParamAdmin(admin.ModelAdmin):
    list_display = ['app', 'key', 'value', 'model', 'axis1', 'description',]
    search_fields = ['app', 'key', 'value', 'axis1', ]
    list_filter = ['app', ]#'model',]

admin.site.register(MageParam, MageParamAdmin)

