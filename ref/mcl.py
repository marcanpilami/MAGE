# coding: utf-8
'''
    @license: Apache License, Version 2.0
    @copyright: 2007-2013 Marc-Antoine Gouillart
    @author: Marc-Antoine Gouillart
'''

## PyParsing imports
from pyparsing import Suppress, Optional, Token, Word, Or , alphanums , QuotedString , oneOf, OneOrMore, ZeroOrMore, delimitedList, Group, Forward, ParseException

## Django imports
from django.contrib.contenttypes.models import ContentType
from django.db.models.fields.related import ManyToManyField, ForeignKey  

## MAGE imports
from MAGE.exceptions import MageError
from ref.exceptions import MageMclAttributeNameError, MageMclSyntaxError
from ref.models import ComponentInstance, ComponentImplementationClass, \
    Environment, ImplementationDescription, ImplementationRelationDescription


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
        
        # Self Type - (T,"modelname"[,"cic"])
        model_type = Word(alphanums + '_')
        cic_name = Word(alphanums + '_')
        type_query = Group(Suppress('(T,') + model_type + Optional(Suppress(',') + cic_name) + Suppress(')'))("type_query")
        
        # Related components connections
        rel_query = Group(Suppress('(R,') + attribute_name + Suppress(',') + mcl_query + Suppress(')'))('rel_query')
        all_links_queries = Group(ZeroOrMore(rel_query))('all_rel_queries')
        
        # Add (A,key="value")
        addition_query = Group(Suppress('(A,') + Optional(attribute_filter_list) + Suppress(')'))('addition_query')
        
        # Environment (E,envtname1,...)
        envt_name = Word(alphanums + '_')
        envt_list = delimitedList(envt_name)
        envt_query = Group(Suppress('(E,') + envt_list + Suppress(')'))('envt_query')
        
        ## All together... the MCL query!
        mcl_query << Group(Suppress('(') + Optional(type_query) + Optional(self_query) + Optional(envt_query) + Optional(addition_query) + all_links_queries + Suppress(')'))('mcl')
    
        
        ## A query can be followed by an update statement (can NOT be in sub queries)
        update_query = Group(Suppress('(U,') + attribute_filter_list + Suppress(')'))('update_query')
    
        self.mcl_query = mcl_query + Optional(update_query)
        
    
    def __parseQuery(self, tree, prefix="", rs=None, allow_create=False, force_type=None):                 
        ## Starting recursion all all instances
        if not rs:
            rs = ComponentInstance.objects
            
        print 'before filtering: %s' % rs.count()
        
        ## Use T 
        if len(tree.mcl.type_query) > 0:
            type_name = tree.mcl.type_query[0]
        else:
            type_name = None
        if force_type is not None:
            type_name = force_type
           
        filters = {} 
        if type_name:           
            filters[prefix + 'implementation__name'] = type_name
        
        if len(tree.mcl.type_query) == 2:
            cic = tree.mcl.type_query[1]
            filters[prefix + 'instanciates__name'] = cic
            
        rs = rs.filter(**filters)
        print 'after T: %s (type was %s)' % (rs.count(), type_name)
        filters.clear()
        
        ## Use S
        if len(tree.mcl.self_query) > 0:
            for att in tree.mcl.self_query[0]:
                attrname = att.attribute_name
                attrvalue = att.attribute_value
                
                operator = '__exact'
                if '*' in attrvalue:
                    operator = "__contains"
                    attrvalue = attrvalue.replace('*', '')
                filters[prefix + 'field_set__field__name'] = attrname
                filters[prefix + 'field_set__value' + operator] = attrvalue
                print filters
                rs = rs.filter(**filters)
                filters.clear()
                
        print 'after S: %s' % rs.count()
            
        ## Use E
        for envt_name in tree.mcl.envt_query:
            rs = rs.filter(environments__name=envt_name)        
        print 'after E: %s' % rs.count()
        
        ## Use R
        for pq in tree.mcl.all_rel_queries:        
            pr = prefix
            target_type = None
            
            if type_name:
                target_type = ImplementationRelationDescription.objects.get(name=pq.attribute_name, source__name=type_name).target.name
            
            #rs = rs.filter(** {pr + "relationships__field__name" : pq.attribute_name})    
            pr = pr + "relationships__"
            rs = self.__parseQuery(tree=pq, prefix=pr, rs=rs, allow_create=allow_create, force_type=target_type)

        ## Creation? Only evaluate the RS if necessary.
        if tree.mcl.addition_query != "" and allow_create:
            if self.__parseQuery(tree, prefix="", rs=None, allow_create=False).count() == 0:
                if type_name is None:
                    raise MageMclSyntaxError('component instance should be created but type is not given')
                self.__createFromQuery(tree, type_name, cic=cic)
        
        ## Update
        if tree.update_query != "":
            for cp in rs:
                cp = cp.leaf
                for att in tree.update_query.attribute_filter_list:
                    setattr(cp, att.attribute_name, att.attribute_value)
                cp.save()
        
        ## Done                    
        return rs
    
    def __createFromQuery(self, tree, type_name, cic=None):
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
                
        ## CIC
        if cic:
            cic = ComponentImplementationClass.objects.get(name=cic)
            all_fields['instanciates'] = cic
        
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
        res.save()  # To enable M2M
        
        ## Use E
        for envt_name in tree.mcl.envt_query:
            res.environments.add(Environment.objects.get(name=envt_name))
        
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
    
    def get_components(self, mcl, allow_create=True, force_type=None):
        try:  
            results = self.mcl_query.parseString(mcl)  
            res = self.__parseQuery(results, allow_create=allow_create, force_type=force_type)
        except ParseException, e:
            raise MageMclSyntaxError(str(e))
        return res.distinct()
        

parser = MclEngine()        
