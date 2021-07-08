# coding: utf-8

## Python imports

## Django imports
from django.db.models.query import Prefetch

## MAGE imports
from ref.models import ComponentInstance
from ref.models.instances import ComponentInstanceRelation
from ref.models.parameters import getParam


def getNetwork(instances_to_draw, select_related={'dependsOn': 2}, collapse_threshold=2):
    ''' 
    @param cis: an iterable of component instances to represent
    @param select_related: a dictionary giving the relations to follow. E.g: {'rel_family_name': 2, 'rel_family_name2: 3}
    @param collapse_threshold: if more than this items of same type same relations, nodes will become one.
    '''

    def getNode(ci, rel_level=0, rel_type=None):
        if ci.pk in nodes:
            return

        if ci in instances_to_draw:
            rel_level = 0
            rel_type = None

        ## Only use CIs from the cache with preloaded relationships
        ci = all_instances[ci.pk]

        nodes[ci.pk] = {'id': ci.pk, 'value':{'label': ci.name or "null", 'style': "fill: " + colourGen.getNodeColour(ci), 'labelStyle': 'stroke: white; fill: white; stroke-width: 0; kerning: 2'}}
        types[ci.pk] = ci.description.name
        targets[ci.pk] = []

        for rel in ci.rel_target_set.all():
            if (rel.target in instances_to_draw) or (rel.field.link_type.name in select_related and (rel_type is None or rel_type == rel.field.link_type.name) and rel_level < select_related[rel.field.link_type.name]):
                getNode(rel.target, rel_level + 1, rel.field.link_type.name)

                if not rel.id in edges:
                    edges[rel.id] = {'id': rel.id, 'u': ci.pk, 'v': rel.target_id, 'value': {'label': rel.field.name} }
                    targets[ci.pk].append(rel.target_id)

    class ColourCounter:
        def __init__(self):
            self.colours = getParam('LINK_COLORS').split(',')
            self.colour_index = 0
            self.colour_envt = {}

        def getNodeColour(self, ci):
            if ci.first_environment() != None:
                if not ci.first_environment().id in self.colour_envt:
                    self.colour_index = self.colour_index + 1
                    if self.colour_index > len(self.colours) - 1:
                        self.colour_index = -1
                    self.colour_envt[ci.first_environment().id] = self.colours[self.colour_index]
                return self.colour_envt[ci.first_environment().id]
            elif ci.environments.count() > 1:
                return '#333'
            return '#AAA'

    ## result fields
    nodes = {}
    edges = {}
    targets = {}
    types = {}
    colourGen = ColourCounter()

    ## Everything is done in memory to avoid hitting the db too much - but this means the whole referential is loaded!
    rs = ComponentInstance.objects.select_related('description').prefetch_related('environments').\
        prefetch_related(Prefetch('rel_target_set', queryset=ComponentInstanceRelation.objects.select_related('field__link_type', 'target')))

    all_instances = {}
    for ci in rs.all():
        all_instances[ci.pk] = ci

    for ci in instances_to_draw:
        getNode(ci)

    ## Collapse
    ns = list(nodes.values())
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

        if len(nodes_to_remove) >= collapse_threshold - 1:  # -1 because first node n1 is not in the list
            for tr in nodes_to_remove:
                for key, value in edges.items():
                    # remove the now duplicate outgoing edges
                    if value['u'] == tr['id']:
                        edges.pop(key)
                    # redirect the incoming edges to the collapsed node
                    if value['v'] == tr['id']:
                        value['v'] = n1['id']
                # remove node as it is collapsed into the first one
                nodes.pop(tr['id'])
                removed_nodes.append(tr['id'])
            # change first node title to reflect collapse
            n1['value']['label'] = "%s instances de %s" % (len(nodes_to_remove) + 1, types[n1['id']])


    ## Done
    return {'nodes': list(nodes.values()), 'edges': list(edges.values())}


