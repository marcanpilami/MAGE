# coding: utf-8

"""
    Library for the gph module. These functions are not part of the API and 
    shouldn't be used outside of the gph module.
    
    @author: Marc-Antoine Gouillart
    @contact: marsu_pilami@msn.com
    @license: GNU GVL v3
"""

## Python imports
import unicodedata

## MAGE imports
from MAGE.prm.models import getParam

## PYDOT imports
from pydot import *


class MageDC(Dot):
    """Generic drawing context for graphviz"""
    
    ####################################################
    ## Init
    def __init__(self, overlap="false", graph_type='digraph', splines="true"):
        Dot.__init__(self, overlap = overlap, graph_type = graph_type, splines = splines)
        
        ## Local variables #TODO: parameter
        self.format = getParam('IMAGE_TYPE')
        self.prog = getParam('GRAPHVIZ_PRG')
        
        ## For helpers
        self.cur_colour = 0
        self.object_colours = {}
    
    
    ####################################################
    ## Rendering
    def render(self):
        return self.create(format=self.format, prog=self.prog)
    
    def writeFile(self, filepath):
        return self.write(path=filepath, format=self.format, prog=self.prog)
    
    
    ####################################################
    ## Colour sequence
    colours = ['bisque1', 'darkorange', 'gold1', 'mediumseagreen', 'skyblue', 'orchid', 'gray']
    def getObjectColour(self,object_name):
        try:
            return self.object_colours[object_name]
        except:
            pass
        self.object_colours[object_name] = self.colours[self.cur_colour]
        if self.cur_colour == self.colours.__len__() - 1:
            self.cur_colour = 0
        else:
            self.cur_colour += 1
        return self.object_colours[object_name]
    
    
    ####################################################
    ## Graph manipulations
        
    
    ####################################################
    ## Strings
    def encode(self, unicodestring):
        return unicodedata.normalize('NFKD', unicodestring).encode('ascii','ignore')