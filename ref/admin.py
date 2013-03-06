
from django.contrib import admin
from ref.models import Project, Environment, LogicalComponent, Application, SLA

admin.site.register(Project)
admin.site.register(Application)
admin.site.register(LogicalComponent)
admin.site.register(SLA)

class EnvironmentAdmin(admin.ModelAdmin):
    fields = ['name', 'description', 'buildDate', 'destructionDate']
    list_display = ('name', 'description',)
    ordering = ('name',)

admin.site.register(Environment, EnvironmentAdmin)

