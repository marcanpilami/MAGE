# coding: utf-8

from pyparsing import Suppress, Optional, Token, Word, Or , alphanums , QuotedString , oneOf, OneOrMore, ZeroOrMore, delimitedList, Group, Forward, ParseException
from django.contrib.contenttypes.models import ContentType
from django.db.models.fields.related import ManyToManyField, ForeignKey  
from ref.models import ComponentInstance, CI2DO
from MAGE.exceptions import MageError
from ref.exceptions import MageMclAttributeNameError, MageMclSyntaxError

#def create_component_instance(instance_type, instance_name, **):

class MclEngine:
    def __init__(self):
        """ Defines the MCL grammar"""
        mcl_query = Forward()
        
        # Key="value"
        attribute_name = Word(alphanums + '_' + '.').setResultsName("attribute_name")   
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
        parent_query = Group(Suppress('(P,') + Optional(attribute_name + Suppress(',')) + mcl_query + Suppress(')'))('parent_query')
        connected_query = Group(Suppress('(C,') + mcl_query + Suppress(')'))('connected_query')
        all_links_queries = Group(ZeroOrMore(connected_query | parent_query))('all_links_queries')
        
        # Add (A,key="value")
        addition_query = Group(Suppress('(A,') + Optional(attribute_filter_list) + Suppress(')'))('addition_query')
        
        ## All together... the MCL query!
        mcl_query << Group(Suppress('(') + Optional(type_query) + Optional(self_query) + Optional(addition_query) + all_links_queries + Suppress(')'))('mcl')
    
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
                attrname = prefix + att.attribute_name.replace('.', '__')
                attrvalue = att.attribute_value
                filters[attrname] = attrvalue
        
        return rs_l.filter(**filters)

    
    def __parseQuery(self, tree, prefix="", rs=None, allow_create=False, force_type=None):                 
        ## Use T and S      
        if len(tree.mcl.type_query) > 0:
            type_name = tree.mcl.type_query[0]
        else:
            type_name = None
        if force_type is not None:
            type_name = force_type
        if len(tree.mcl.self_query) > 0:
            self_query = tree.mcl.self_query[0]
        else:
            self_query = None 
        t_class = None
        if type_name:
            t_class = ContentType.objects.get(model=type_name.lower()).model_class()
        rs = self.__parseLevel0(type_name, self_query, prefix=prefix, rs=rs)
        
        ## Use P & C
        for pq in tree.mcl.all_links_queries:
            if pq.getName() == 'parent_query':
                pr = prefix
                relationship_type = None
                if pq.attribute_name:
                    if t_class and not t_class.parents.has_key(pq.attribute_name):
                        raise MageMclAttributeNameError('there is no relationship attribute named %s' % pq.attribute_name)
                    if t_class:
                        relationship_type = t_class.parents[pq.attribute_name]['model'].lower()
                        
                    filter_relationship_name = {pr + 'pedestals_ci2do__rel_name': pq.attribute_name}
                    rs = rs.filter(**filter_relationship_name)
                    
                pr = pr + "dependsOn__"
                rs = self.__parseQuery(tree=pq, prefix=pr, rs=rs, allow_create=allow_create, force_type=relationship_type)
                
            if pq.getName() == 'connected_query':
                pr = prefix
                pr = pr + "connectedTo__"
                rs = self.__parseQuery(tree=pq, prefix=pr, rs=rs, allow_create=allow_create)

        ## Creation? Only evaluate the RS if necessary.
        if tree.mcl.addition_query != "" and allow_create:
            if self.__parseQuery(tree, prefix="", rs=None, allow_create=False).count() == 0:
                if type_name is None:
                    raise MageMclSyntaxError('component instance should be created but type is not given')
                self.__createFromQuery(tree, type_name)
        
        ## Done                    
        return rs
    
    def __createFromQuery(self, tree, type_name):
        """ When this function is called, all relations are supposed to exist"""
        
        ## Create base element using T and S
        t = ContentType.objects.get(model=type_name.lower())
        t_class = t.model_class()
        
        all_fields = {}
        if len(tree.mcl.self_query) > 0:
            for att in tree.mcl.self_query[0]:
                attrname = att.attribute_name
                attrvalue = att.attribute_value
                all_fields[attrname] = attrvalue
        
        ## Add A fields - as long as this is not a link field...
        if tree.mcl.addition_query != "" and len(tree.mcl.addition_query) > 0:
            for att in tree.mcl.addition_query[0]:
                attrname = att.attribute_name
                attrvalue = att.attribute_value
                
                model_field = t_class._meta.get_field_by_name(attrname)[0]
                if isinstance(model_field , ManyToManyField) or isinstance(model_field , ForeignKey):
                    continue
                
                all_fields[attrname] = attrvalue
            
        ## Create the base element
        res = t_class(**all_fields)
        res.save() # To enable M2M
        
        ## Add the relations
        for pq in tree.mcl.all_links_queries:
            if pq.getName() == 'parent_query':
                if not pq.attribute_name:
                    raise MageMclSyntaxError('parent relationship name not given - cannot create a component instance without it.')
                relationship_type = t_class.parents[pq.attribute_name]['model'].lower()
                parent_s = self.__parseQuery(tree=pq, prefix="", rs=None, allow_create=False, force_type=relationship_type)
                
                for c in parent_s:
                    nc = CI2DO(pedestal=c, statue=res, rel_name=pq.attribute_name)
                    nc.save()
                
            if pq.getName() == 'connected_query':
                connected_s = self.__parseQuery(tree=pq, prefix="", rs=None, allow_create=False)
                for c in connected_s:
                    res.connectedTo.add(c)
        
        ## Check the relations - if incomplete, destroy and raise error: an incomplete instance is useless
        relation_errors = res.check_relation_complete()
        if len(relation_errors) > 0:
            res.delete()
            raise MageError('relationships are incomplete: %s' % relation_errors)
        
        ## Done. This function does not return anything - it has created a component that will be retrieved by a query in __parseQuery
    
    def get_components(self, mcl, allow_create=True):
        try:  
            results = self.mcl_query.parseString(mcl)  
            res = self.__parseQuery(results, allow_create=allow_create)
        except ParseException, e:
            raise MageMclSyntaxError(str(e))
        return res.distinct()
        

parser = MclEngine()        
