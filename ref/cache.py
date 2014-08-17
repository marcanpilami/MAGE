# coding: utf-8
from django.core.cache import cache
from ref.models.models import ComponentInstance, ComponentInstanceRelation, \
    ComponentInstanceField
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver


@receiver(post_save, sender=ComponentInstance)
@receiver(post_save, sender=ComponentInstanceRelation)
@receiver(post_save, sender=ComponentInstanceField)
def refresh_cache(sender, instance, created, raw, using, update_fields, **kwargs):
    cache.delete_many(['selfdescr_%s' %a.pk for a in ComponentInstance.objects.all()])
    
