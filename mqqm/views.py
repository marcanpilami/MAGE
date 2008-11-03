# coding: utf-8

from MAGE.mqqm.models import QueueManager
from django.shortcuts import render_to_response
from django.template.loader import render_to_string


def detail(qm):
    qmo = None
    if isinstance(qm,  (str, unicode,)):
        qmo = QueueManager.objects.get(name=qm)
    elif isinstance(qm, QueueManager):
        qmo = qm
    elif isinstance(qm, int):
        qmo = QueueManager.objects.get(pk=qm)
    else:
        raise Exception()    
    return render_to_string('details.html', {'comp':qmo})
