# coding: utf-8
from django.core.cache import cache
from ref.models.instances import ComponentInstance, ComponentInstanceField
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from ref.models.description import ImplementationComputedFieldDescription, \
    ImplementationRelationDescription, ImplementationFieldDescription


@receiver(post_save, sender=ComponentInstanceField)
@receiver(post_save, sender=ImplementationComputedFieldDescription)
def empty_computed_cache(sender, instance, created, raw, using, update_fields, **kwargs):
    if not instance.pk or created or raw:
        return
    # key is 'computed_%s_%s' % (field_id, instance.pk)
    for ci in ComponentInstance.objects.prefetch_related('description__computed_field_set').all():
        key = 'computed_id_%s_%s' % (ci.description_id, ci.pk)
        cache.delete(key)

        for compf in ci.description.computed_field_set.all():
            cache.delete('computed_%s_%s' % (compf.pk, ci.pk))


@receiver(post_save, sender=ImplementationFieldDescription)
@receiver(post_save, sender=ImplementationRelationDescription)
def empty_form_cache(sender, instance, created, raw, using, update_fields, **kwargs):
    if not instance.pk or created or raw:
        return
    
    # remove from cache the form class for the description that was just modified
    # Note: not a standard cache call because these object are not pickable. Cache is simply used as
    # a reference to allow global purge.
    if isinstance(instance, ImplementationRelationDescription):
        descrid = instance.source_id
    else:
        descrid = instance.description_id
    cache.delete('descr_terseformset_%s' % descrid)
