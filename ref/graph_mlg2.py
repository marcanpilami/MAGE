# coding: utf-8

## Python imports
import unicodedata

## MAGE imports
from ref.models import ComponentInstance
from ref.models.parameters import getMyParams
from ref.graphs_helpers import MageDC
from ref.models.instances import ComponentInstanceField, \
    ComponentInstanceRelation
from django.db.models.query import Prefetch


def getNetwork(instances_to_draw, select_related={'dependsOn': 2}, collapse_threshold=2):
    ''' 
    @param cis: an iterable of component instances to represent
    @param select_related: a dictionary giving the relations to follow. E.g: {'rel_family_name': 2, 'rel_family_name2: 3}
    @param collapse_threshold: if more than this items of same type same relations, nodes will become one.
    '''

    def getNode(ci, rel_level=0, rel_type=None):
        if nodes.has_key(ci.pk):
            return

        if ci in instances_to_draw:
            rel_level = 0
            rel_type = None

        nodes[ci.pk] = {'id': ci.pk, 'value':{'label': ci.name, 'truc': 'R%MLKR%ML'}}
        types[ci.pk] = ci.implementation.name
        targets[ci.pk] = []

        for rel in ci.rel_target_set.all():
            if (rel.target in instances_to_draw) or (select_related.has_key(rel.field.link_type.name) and (rel_type is None or rel_type == rel.field.link_type.name) and rel_level < select_related[rel.field.link_type.name]):
                getNode(rel.target, rel_level + 1, rel.field.link_type.name)

                if not edges.has_key(rel.id):
                    edges[rel.id] = {'id': rel.id, 'u': ci.pk, 'v': rel.target_id, 'value': {'label': rel.field.name} }
                    targets[ci.pk].append(rel.target_id)

    ## result fields
    nodes = {}
    edges = {}
    targets = {}
    types = {}

    ## Everything is done in memory to avoid hitting the db too much - but this means the whole referential is loaded!
    rs = ComponentInstance.objects.select_related('implementation').prefetch_related('environments').\
        prefetch_related(Prefetch('field_set', queryset=ComponentInstanceField.objects.select_related('field'))).\
        prefetch_related(Prefetch('rel_target_set', queryset=ComponentInstanceRelation.objects.select_related('field')))

    all_instances = {}
    for ci in rs:
        all_instances[ci.pk] = ci

    for ci in instances_to_draw:
        getNode(ci)

    ## Collapse
    ns = nodes.values()
    removed_nodes = []
    for i in range(0, len(ns)):
        n1 = ns[i]

        if len(targets[n1['id']]) == 0:
            # never collapse CI that are at the root of the hierarchy - it's most often stupid
            continue

        nodes_to_remove = []
        for j in range(i + 1, len(ns)):
            n2 = ns[j]
            if types[n1['id']] == types[n2['id']] and targets[n1['id']] == targets[n2['id']] and not n2['id'] in removed_nodes:
                nodes_to_remove.append(n2)

        print len(nodes_to_remove)
        if len(nodes_to_remove) >= collapse_threshold - 1: # -1 because first node n1 is not in the list
            for tr in nodes_to_remove:
                for key, value in edges.items():
                    # remove the now duplicate outgoing edges
                    if value['u'] == tr['id']:
                        print 'removing link'
                        edges.pop(key)
                    # redirect the incoming edges to the collapsed node
                    if value['v'] == tr['id']:
                        print 'redirecting link'
                        value['v'] = n1['id']
                # remove node as it is collapsed into the first one
                print 'removing node %s' % tr['id']
                nodes.pop(tr['id'])
                removed_nodes.append(tr['id'])
            # change first node title to reflect collapse
            n1['value']['label'] = "% instances of %s" % (len(nodes_to_remove) + 1, types[n1['id']])


    ## Done
    return {'nodes': nodes.values(), 'edges': edges.values()}


