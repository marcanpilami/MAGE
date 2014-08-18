# coding: utf-8

from ref.models.models import ComponentInstance
from ref.csvi import get_components_csv
from django.http.response import HttpResponse


def csv(request, url_end):
    comps = ComponentInstance.objects.filter(pk__in=url_end.split(','))
    return HttpResponse(get_components_csv(comps, displayRestricted=(request.user.is_authenticated() and request.user.has_perm('ref.allfields_componentinstance'))), mimetype="text/csv")

