'''
Created on 11 mars 2013

@author: Marc-Antoine
'''
from pyparsing import Suppress, Optional, Token, Word, Or , alphanums , QuotedString , oneOf, OneOrMore, ZeroOrMore, delimitedList, Group
from django.contrib.contenttypes.models import ContentType
from ref.models import ComponentInstance

#def create_component_instance(instance_type, instance_name, **):

class MclEngine:
    def __init__(self):
        """ Defines the MCL grammar"""
        
        # Key="value"
        attribute_name = Word(alphanums + '_').setResultsName("attribute_name")   
        attribute_value = QuotedString('"', escQuote='""').setResultsName("attribute_value")
        attribute_def = Group(attribute_name + '=' + attribute_value)('attribute_def')
        attribute_def_list = Group(delimitedList(attribute_def))("attribute_def_list")
        
        # Self filters - (S,name="toto")
        self_query = Group('(S,' + attribute_def_list + ')')('self_query')
        
        # self Type - (T,"modelname")
        type_query = Group('(T,' + attribute_value + ')')("type_query")
        
        # Related components connexions - (P,name="marsu",description="houba"
        rel_query_type = oneOf(['P', 'C'])('type')
        sub_query = Group(rel_query_type + Suppress(',') + attribute_def_list)("sub_query")      
        links_query = Group(Suppress('(') + delimitedList(sub_query, '|') + Suppress(')'))('links_query')
        all_links_queries = Group(ZeroOrMore(links_query))('all_links_queries')
        
        self.mcl_query = Group(Optional(type_query) + Optional(self_query) + all_links_queries)('mcl')
    
        
    def __parseAttr(self, compo_list, attribute_def):
        attrname = attribute_def.attribute_name
        attrvalue = attribute_def.attribute_value
        
        res = []
        for compo in compo_list:
            v = compo.__getattr__(attrname)
            if  v == attrvalue:
                res.append(compo) 
        
        return res
        
    def __parseLevel0(self, type_query, self_query):
        cl = ComponentInstance
        if type_query:
            t = ContentType.objects.get(model=type_query.attribute_value)
            cl = t.model_class()
        
        filters = {}
        if self_query:
            for att in [ i for i in self_query.attribute_def_list ]:
                attrname = att.attribute_name
                attrvalue = att.attribute_value
                filters[attrname] = attrvalue
    
        return cl.objects.filter(**filters)
    
    def __parseRelationChain(self, links_query, compo_list):
        sub_query_aslist = links_query.asList()              
        for compo in compo_list[:]:
            if not self.__checkCompoInstance(compo, sub_query_aslist):
                compo_list.remove(compo)
        
        return compo_list
    
    def __checkCompoInstance(self, compo, sub_query_aslist):
        first_query = sub_query_aslist[0]
        toCheck = []
        if first_query[0] == 'C':
            toCheck = compo.connectedTo.all()
        elif first_query[0] == 'P':     
            toCheck = compo.dependsOn.all()
        for n in toCheck:
            if self.__checkCompoInstanceNeigbors(n, sub_query_aslist):
                return True
        return False
    
    def __checkCompoInstanceNeigbors(self, compo, sub_query_aslist, already_checked=[]): 
        current_query = sub_query_aslist[0]
        
        ## Check component itself
        for attr in current_query[1]:
            attrname = attr[0]
            attrvalue = attr[2]
            
            if attrname == 'model':
                if not compo.model.model == attrvalue:
                    return False
            else:    
                try:
                    if not getattr(compo, attrname) == attrvalue:
                        return False
                except:
                    return False
            
        ## If we are at the end of the query, done.
        if len(sub_query_aslist) == 1:
            return True    
        
        ## If we are here, the component itself is OK? we have to check its connected partners.
        already_checked.append(compo)
        
        ## Check its partners
        cdr = sub_query_aslist[1:]
        next_level = cdr[0]
        
        toCheck = []
        if next_level[0] == 'C':
            toCheck.extend(compo.connectedTo.all())
        elif next_level[0] == 'P':     
            toCheck.extend(compo.dependsOn.all())
            
        # remove neighbors that were already used (avoids cycles) 
        toCheck = [ i for i in toCheck if i not in already_checked]
        
        for neighbor in toCheck:
            if self.__checkCompoInstanceNeigbors(neighbor, cdr, already_checked):
                return True
        
        return False
        
    
    def get_components(self, mcl):
        ## Parse query
        results = self.mcl_query.parseString(mcl)        
        
        ## Results from a database query - without relationships
        res = list(self.__parseLevel0(results.mcl.type_query, results.mcl.self_query))
        
        ## Filter these results with relationships constraints
        for links_query in results.mcl['all_links_queries']:
            res = self.__parseRelationChain(links_query, res)
            if len(res) == 0:
                break
        
        ## Done
        return res


parser = MclEngine()        

