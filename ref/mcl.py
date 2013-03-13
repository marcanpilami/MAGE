'''
Created on 11 mars 2013

@author: Marc-Antoine
'''
from pyparsing import Optional, Word, Or , alphas, QuotedString , oneOf, OneOrMore, ZeroOrMore, delimitedList, Group
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
    
    filters={}
    if self_query:
        for att in [ i for i in self_query.attribute_def_list ]:
            attrname = att.attribute_name
            attrvalue = att.attribute_value
            filters[attrname] = attrvalue

    return cl.objects.filter(**filters)

def __parseRelationChain(sub_query_chain, compo_list):
    for compo  in compo_list:
        pass
    
def __parseRelationChainCompo(sub_query_chain, compo):
    for sub_query in sub_query_chain:
        pass

def get_components(mcl):
    res = []
    
    ## 1 - grammar
    
    # Key="value"
    attribute_name = Word(alphas + '_').setResultsName("attribute_name")   
    attribute_value = QuotedString('"', escQuote='""').setResultsName("attribute_value")
    attribute_def = Group(attribute_name + '=' + attribute_value)('attribute_def')
    attribute_def_list = Group(delimitedList(attribute_def))("attribute_def_list")
    
    # Self filters - (S,name="toto")
    self_query = Group('(S,' + attribute_def_list + ')')('self_query')
    
    # self Type - (T,"modelname")
    type_query = Group('(T,' + attribute_value + ')')("type_query")
    
    # Related components connexions - (P,name="marsu",description="houba"
    subparent_query = Group('P,' + attribute_def_list + Optional(','))("subparent_query")
    subconnected_query = Group('C,' + attribute_def_list + Optional(','))("subconnected_query")
    sub_query = (subparent_query | subconnected_query)
    links_query = Group('(' + delimitedList(sub_query, '|') + ')')("sub_queries")
    related_queries = Group(ZeroOrMore(links_query))('related_queries')
    
    mcl_query = Group(Optional(type_query) + Optional(self_query) + related_queries)('mcl')

    
    results = mcl_query.parseString(mcl)
    print mcl
    print results.dump()
    print
    print
    
    if results.mcl.self_query:
        for attr in results.mcl.self_query.attribute_def_list:
            print attr.dump()
   # print results.type_query.attribute_value
    #print results.self_query.attribute_def_list
    
    ## 1 : all components of given type (if type is given)
    
    #print results.mcl.self_query.attribute_def_list[0].attribute_name
    #print results.mcl.type_query.attribute_value
    res = __parseLevel0(results.mcl.type_query, results.mcl.self_query)
    
    for related_query in results.mcl.related_queries:
        __parseRelationChain(results.msc., compo_list)
    print res
    
    
## Tests simples sans relations
#get_components('(S,name="waPRDINT2")')
#get_components('(T,"wascluster")')
#get_components('(T,"wascluster")(S,name="wcluPRDUSR")')
#get_components('')
get_components('(P,name="wcluPRDUSR")')
#get_components('(P,model="wascluster",name="wcluPRDUSR")')


#get_components('(S,name_toto="as (name\',))""")')
#get_components('(S,name="as name1",descr="toto toto")')

#get_components('(P,model="pmodel1",name="p1")(P,model="pmodel2",name="p2"|C,model="meuh")')

#get_components('(T,"supermodel")(S,name="as name1",descr="toto toto")(P,model="pmodel1",name="p1")(P,model="pmodel2",name="p2")')
