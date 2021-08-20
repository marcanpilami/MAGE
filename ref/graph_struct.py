# coding: utf-8

## Python imports

## Django imports

## MAGE imports
from ref.models.parameters import getParam
from ref.models.description import ImplementationDescription, ImplementationRelationDescription


def getStructureTree():
    class ColourCounter:
        def __init__(self):
            self.colours = getParam('LINK_COLORS').split(',')
            self.colour_index = 0
            self.colour_tag = {}

        def getNodeColour(self, rn):
            if not rn.tag in self.colour_tag:
                self.colour_index = self.colour_index + 1
                if self.colour_index > len(self.colours) - 1:
                    self.colour_index = -1
                self.colour_tag[rn.tag] = self.colours[self.colour_index]
            return self.colour_tag[rn.tag]

    colourGen = ColourCounter()
    repre = {}
    edges = {}

    for r in ImplementationDescription.objects.all():
        repre[r.id] = {'id': r.pk, 'value':{'label': r.name, 'style': "fill: " + colourGen.getNodeColour(r), 'labelStyle': 'stroke: white; fill: white; stroke-width: 0; kerning: 2'}}

    for rel in ImplementationRelationDescription.objects.all():
        card = ""
        if rel.max_cardinality == 1 and rel.min_cardinality == 1:
            card = "*"
        if rel.max_cardinality == 1 and rel.min_cardinality == 0:
            card = ""
        elif rel.max_cardinality > 1:
            card = " [%s;%s]" % (rel.min_cardinality, rel.max_cardinality)
        elif rel.min_cardinality == 0:
            card = " [%s;%s]" % (rel.min_cardinality, rel.max_cardinality)
        edges[rel.id] = {'id': rel.id, 'u': rel.source_id, 'v': rel.target_id, 'value': {'label': rel.name + card} }

    ## Done
    return {'nodes': list(repre.values()), 'edges': list(edges.values())}
