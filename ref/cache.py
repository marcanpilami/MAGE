# coding: utf-8
from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from ref.models.ou import AclAuthorization

from ref.models.instances import ComponentInstance, ComponentInstanceField
from ref.models.description import ImplementationComputedFieldDescription, \
    ImplementationRelationDescription, ImplementationFieldDescription


@receiver(post_save, sender=ComponentInstanceField)
def empty_computed_cache(sender, instance, created, raw, using, update_fields, **kwargs):
    if not instance.pk or created or raw:
        return
    ci_id = instance.instance_id
    cis = ComponentInstance.objects.prefetch_related(
        'reverse_relationships__reverse_relationships__reverse_relationships').get(pk=ci_id)
    computed_fields = ImplementationComputedFieldDescription.objects.all()
    d = {}
    for cf in computed_fields:
        try:
            d[cf.description_id].append(cf.id)
        except KeyError:
            d[cf.description_id] = [cf.id, ]

    clean_ci(cis, d, 3)


def clean_ci(ci, d, rec_level):
    i = 0
    try:
        for field_id in d[ci.description_id]:
            cache.delete('computed_%s_%s' % (field_id, ci.pk))
            i += 1
    except KeyError:
        # Types without computed fields
        pass

    cache.delete('computed_id_%s_%s' % (ci.description_id, ci.pk))

    if rec_level > 0:
        for cc in ci.reverse_relationships.all():
            i += clean_ci(cc, d, rec_level - 1)
    return i


@receiver(post_save, sender=ImplementationComputedFieldDescription)
def empty_commuted_cache_on_description(sender, instance, created, raw, using, update_fields, **kwargs):
    if not instance.pk or created or raw:
        return
    for ci in ComponentInstance.objects.filter(description_id=instance.description_id):
        cache.delete('computed_%s_%s' % (instance.pk, ci.pk))


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


@receiver(post_save, sender=AclAuthorization)
def invalidate_acl_ace_cache(sender, instance, created, raw, using, update_fields, **kwargs):
    """Invalidate: ACL related to modified ACE + children that do not block inheritance.
    Done recursively - horrible for perfs, but rare."""
    if raw:
        return
    invalidate_acl_folder_cache(instance.target)


def invalidate_acl_folder_cache(folder):
    cache_key = "acl_folder_%s" % folder.pk
    cache.delete(cache_key)
    for child in folder.subfolders.filter(block_inheritance=False):
        invalidate_acl_folder_cache(child)
