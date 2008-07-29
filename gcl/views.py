

from django.http import HttpResponse
from django.shortcuts import render_to_response
from MAGE.gcl.models import Installation
from MAGE.gcl.models import Tag  

def installs_list_envt(request, envt_name):
    install_list = Installation.objects.filter(target_envt__name = envt_name).order_by('install_date')
    return render_to_response('gcl/install_list.html', { 'install_list' : install_list, 'envt_name': envt_name})


def tag_list(request):
    tag_list = Tag.objects.order_by('snapshot_date')
    return render_to_response('gcl/tags_list.html', { 'tag_list' : tag_list })