# Create your views here.

from MAGE.ref.models import *

from django.shortcuts import render_to_response

def page_de_garde(request):
    envts = Environment.objects.all()
    return render_to_response('pda/accueil.html', {'envts':envts})