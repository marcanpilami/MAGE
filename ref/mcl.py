'''
Created on 11 mars 2013

@author: Marc-Antoine
'''
from pyparsing import Suppress, Optional, Token, Word, Or , alphanums , QuotedString , oneOf, OneOrMore, ZeroOrMore, delimitedList, Group, Forward
from django.contrib.contenttypes.models import ContentType
from ref.models import ComponentInstance

#def create_component_instance(instance_type, instance_name, **):

class MclEngine:
    def __init__(self):
        """ Defines the MCL grammar"""
        
        mcl_query = Forward()
        
        # Key="value"
        attribute_name = Word(alphanums + '_').setResultsName("attribute_name")   
        attribute_value_quoted = QuotedString('"', escQuote='""')
        attribute_value_reference = '@' + attribute_name
        attribute_value = (attribute_value_quoted | attribute_value_reference | mcl_query).setResultsName("attribute_value")
        
        attribute_filter = Group(attribute_name + Suppress('=') + attribute_value)('attribute_filter')
        attribute_filter_list = Group(delimitedList(attribute_filter))("attribute_filter_list")
        
        # Self filters - (S,name="toto")
        self_query = Group(Suppress('(S,') + attribute_filter_list + Suppress(')'))('self_query')
        
        # Self Type - (T,"modelname")
        model_type = Word(alphanums)
        type_query = Group(Suppress('(T,') + model_type + Suppress(')'))("type_query")
        
        # Related components connections - (P,(S,name="marsu",description="houba"))
        parent_query = Group(Suppress('(P,') + Optional(attribute_name + ',') + mcl_query + Suppress(')'))('parent_query')
        connected_query = Group(Suppress('(C,') + mcl_query + Suppress(')'))('connected_query')
        all_links_queries = Group(ZeroOrMore(connected_query | parent_query))('all_links_queries')
        
        mcl_query << Group(Suppress('(') + Optional(type_query) + Optional(self_query) + all_links_queries + Suppress(')'))('mcl')
    
        self.mcl_query = mcl_query
        
        
    def __parseLevel0(self, type_name, self_query, prefix='', rs=None):
        filters = {}
        if rs is None:
            rs_l = ComponentInstance.objects
        else:
            rs_l = rs
        
        if type_name:
            t = ContentType.objects.get(model=type_name)
            if rs is None:
                rs_l = t.model_class().objects
            if rs is not None:
                prefix = "%s%s__" % (prefix, type_name.lower())
            filters[prefix + 'model'] = t

        if self_query:
            for att in self_query:
                attrname = prefix + att.attribute_name
                attrvalue = att.attribute_value
                filters[attrname] = attrvalue
        
        return rs_l.filter(**filters)

    
    def __parseQuery(self, tree, prefix="", rs=None):                 
        ## Use T and S      
        if len(tree.mcl.type_query) > 0:
            type_name = tree.mcl.type_query[0]
        else:
            type_name = None 
        if len(tree.mcl.self_query) > 0:
            self_query = tree.mcl.self_query[0]
        else:
            self_query = None 
        rs = self.__parseLevel0(type_name, self_query, prefix=prefix, rs=rs)
        
        ## Use P
        for pq in tree.mcl.all_links_queries:
            if pq.getName() == 'parent_query':
                pr = prefix
                if pq.attribute_name:
                    filter_relationship_name = {pr + 'pedestals_ci2do__rel_name': pq.attribute_name}
                    rs = rs.filter(**filter_relationship_name)
                pr = pr + "dependsOn__"
                rs = self.__parseQuery(tree=pq, prefix=pr, rs=rs)
                
            if pq.getName() == 'connected_query':
                pr = prefix
                pr = pr + "connectedTo__"
                rs = self.__parseQuery(tree=pq, prefix=pr, rs=rs)
                    
        return rs
    
    def get_components(self, mcl):
        results = self.mcl_query.parseString(mcl)        
        res =  self.__parseQuery(results)
        return res.distinct()
        

parser = MclEngine()        
