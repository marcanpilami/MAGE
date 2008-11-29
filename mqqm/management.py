# coding: utf-8

## Python imports

## Django imports
from django.db.models.signals import post_syncdb
from django.contrib.contenttypes.models import ContentType

## MAGE imports
import models
from MAGE.prm.models import setParam, getParam, ParamNotFound
from models import QueueManager

def post_syncdb_handler(sender, **kwargs):
    ct = ContentType.objects.get_for_model(QueueManager)
    try:
        getParam(key='node_shape', model = ct, app='gph')
    except ParamNotFound:
        setParam(key = u'node_shape', app = 'gph', model = ct, value = 'box')
        setParam(key = u'node_style', app = 'gph', model = ct, value = 'filled')
        
## Listen to the syncdb signal
post_syncdb.connect(post_syncdb_handler, sender=models)