# coding: utf-8
'''
Created on 30 août 2014

@author: Marc-Antoine
'''
from pyparsing import Forward, Group, Suppress, Optional, ZeroOrMore, Combine, \
    Word, alphas, nums, QuotedString, OneOrMore, Keyword, CaselessKeyword, \
    CaselessLiteral
from ref.models.models import ComponentInstance

def __build_grammar():
    expr = Forward()
    
    verb = CaselessLiteral("SELECT")('verb')
    noun = CaselessLiteral("COMPONENTS")('noun')
    
    identifier = Combine(Word(alphas + "_", exact=1) + Optional(Word(nums + alphas + "_")))("identifier")
    navigation = Group(identifier + ZeroOrMore(Suppress(".") + identifier))("navigation")
    
    filter_predicate = Group(navigation + Suppress("=") + (QuotedString("'", escQuote="''") | (Suppress('(') + expr + Suppress(')')))('value'))('predicate')
    where_clause = Group(Suppress(CaselessLiteral("WHERE")) + filter_predicate + ZeroOrMore(Suppress(CaselessLiteral("AND")) + filter_predicate))('where') 

    expr << Group(verb + noun + Optional(where_clause))('query')
    return expr

__grammar = __build_grammar()


def run(query):
    expr = __grammar.parseString(query)
    print expr.dump()   
    return __run(expr) 
    #return  __grammar.parseString(query)

def __run(q):
    q = q.query
    if q.verb == 'SELECT' and q.noun == 'COMPONENTS':
        return __select_compo(q)
    
def __select_compo(q):
    
    rs = ComponentInstance.objects
    
    if q.where:
        for predicate in q.where:
            print predicate
            
            ## Special keys begin with '_', normal keys without '_' are CI attributes
            if len(predicate.navigation) == 1 and predicate.navigation[0].startswith('_'):
                key = predicate.navigation[0]
                if key == "_type":
                    rs = rs.filter(implementation__name=predicate.value)
                if key == "_id":
                    rs = rs.filter(id=predicate.value)
                if key == "_envt":
                    rs = rs.filter(environments__name=predicate.value)
                    
                continue
            
            ## Key analysis: last part is always a simple field, others are relationship fields
            r = {}
            prefix = ""
            for part in predicate.navigation[0:-1]:
                r[ prefix + 'rel_target_set__field__name'] = part
                prefix = prefix + 'relationships__'
            
            ## Add last item - the attribute name itself
            if predicate.navigation[-1] == '_id':
                r[ prefix + 'id'] = predicate.value
            else:
                r[ prefix + 'field_set__field__name'] = predicate.navigation[-1]
                r[ prefix + 'field_set__value'] = predicate.value
            rs = rs.filter(**r)
            print r
            print len(rs)
            
    return rs
            
