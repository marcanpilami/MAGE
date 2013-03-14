'''
Created on 11 mars 2013

@author: Marc-Antoine
'''
from pyparsing import Suppress, Optional, Token, Word, Or ,  alphanums , QuotedString , oneOf, OneOrMore, ZeroOrMore, delimitedList, Group
from django.contrib.contenttypes.models import ContentType
from ref.models import ComponentInstance

def __parseAttr(compo_list, attribute_def):
    attrname = attribute_def.attribute_name
    attrvalue = attribute_def.attribute_value
    
    res = []
    for compo in compo_list:
        v = compo.__getattr__(attrname)
        if  v == attrvalue:
            res.append(compo) 
    
    return res
    
def __parseLevel0(type_query, self_query):
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

def __parseRelationChain(links_query, compo_list):
    for sub_query in links_query:  
        for attr in sub_query.attribute_def_list:
            print attr.attribute_name
            print attr.attribute_value
            print sub_query.type
            
            for compo in compo_list:
                l_field = 'dependsOn'
                if sub_query.type == 'C':
                    l_field = 'connectedTo'

def __tmp(compo_list, links_query_list):
    for compo in compo_list:
        pass


def __checkCompoInstance(compo, attribute_def_list): 
    for attr in attribute_def_list:
        try:
            if not getattr(compo, attr.attribute_name) == attr.attribute_value:
                return False
        except:
            return False
    return True
    
def __parseRelationChainCompo(sub_query_chain, compo):
    for sub_query in sub_query_chain:
        pass

def get_components(mcl):
    res = []
    
    ## 1 - grammar
    
    # Key="value"
    attribute_name = Word( alphanums  + '_').setResultsName("attribute_name")   
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
    all_links_queries=Group(ZeroOrMore(links_query))('all_links_queries')
    
    mcl_query = Group(Optional(type_query) + Optional(self_query) + all_links_queries)('mcl')

    
    results = mcl_query.parseString(mcl)
    print mcl
    print results.dump()
    print
    print
        
   # print results.type_query.attribute_value
    #print results.self_query.attribute_def_list
    
    ## 1 : all components of given type (if type is given)
    
    #print results.mcl.self_query.attribute_def_list[0].attribute_name
    #print results.mcl.type_query.attribute_value
    res = __parseLevel0(results.mcl.type_query, results.mcl.self_query)
    
    for links_query in results.mcl['all_links_queries']:
        __parseRelationChain(links_query, res)
    print res
    
    
## Tests simples sans relations
#get_components('(S,name="waPRDINT2")')
#get_components('(T,"wascluster")')
#get_components('(T,"wascluster")(S,name="wcluPRDUSR")')
#get_components('')
#get_components('(P,name="wcluPRDUSR")')
get_components('(P,name1="wcluPRDUSR"|C,name2="meuh")')
#get_components('(P,model="wascluster",name="wcluPRDUSR")')


#get_components('(S,name_toto="as (name\',))""")')
#get_components('(S,name="as name1",descr="toto toto")')

#get_components('(P,model="pmodel1",name="p1")(P,model="pmodel2",name="p2"|C,model="meuh")')

#get_components('(T,"supermodel")(S,name="as name1",descr="toto toto")(P,model="pmodel1",name="p1")(P,model="pmodel2",name="p2")')
