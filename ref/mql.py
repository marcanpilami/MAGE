# coding: utf-8

'''
MAGE Query Language
'''

from pyparsing import Forward, Group, Suppress, Optional, ZeroOrMore, Combine, \
    Word, alphas, nums, QuotedString, CaselessLiteral, FollowedBy
from ref.models.models import ComponentInstance, ComponentInstanceField, ComponentInstanceRelation
from django.db.models.query import Prefetch

def __build_grammar():
    expr = Forward()

    k_select = CaselessLiteral("SELECT")
    k_from = CaselessLiteral("FROM")
    k_where = CaselessLiteral("WHERE")
    k_and = CaselessLiteral("AND")
    k_instances = CaselessLiteral("INSTANCES")
    qs = QuotedString("'", escQuote="''")

    identifier = Combine(Word(alphas + "_", exact=1) + Optional(Word(nums + alphas + "_")))("identifier")
    navigation = Group(identifier + ZeroOrMore(Suppress(".") + identifier))("navigation")

    filter_predicate = Group(navigation + Suppress("=") + (qs('value') | (Suppress('(') + expr('subquery') + Suppress(')'))))('predicate')
    where_clause = Group(Suppress(k_where) + filter_predicate + ZeroOrMore(Suppress(k_and) + filter_predicate))('where')

    # Pre filters
    impl = Optional(Suppress("implementation")) + qs('impl')
    cic = Suppress("offer") + qs('cic')
    lc = Suppress("lc") + qs('lc')
    envt = Suppress("environment") + qs('envt')
    pre_filter = Optional(envt) + Optional(lc) + Optional(cic) + Optional(impl) + FollowedBy(k_instances)

    # Dict query (only select some elements and navigate)
    nl_expr = Group(navigation + ZeroOrMore(Suppress(',') + navigation) + FollowedBy(k_from))('selector')

    # The sum of all fears
    select = Group(Suppress(k_select) + Optional(nl_expr + Suppress(k_from)) + pre_filter + Suppress(k_instances) + Optional(where_clause) + Optional(CaselessLiteral('WITH COMPUTATIONS')('compute')))('select')

    expr << select
    return expr

__grammar = __build_grammar()


def run(query):
    expr = __grammar.parseString(query)
    print expr.dump()
    return __run(expr)
    #return  __grammar.parseString(query)

def __run(q):
    if q.select != None:
        return __select_compo(q.select)

def __select_compo(q):

    rs = ComponentInstance.objects.all()

    if q.lc:
        rs = rs.filter(instanciates__implements__name=q.lc)
    if q.cic:
        rs = rs.filter(instanciates__name=q.cic)
    if q.impl:
        rs = rs.filter(implementation__name=q.impl)
    if q.envt:
        rs = rs.filter(environments__name=q.envt)

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

            ## Add last item - the attribute name itself, constraint by the value
            val = None
            if predicate.value:
                val = predicate.value
            elif predicate.subquery:
                tmp = __select_compo(predicate.subquery)
                if not type(tmp) == list:
                    raise Exception('subqueries must always return a single field')
                if len(tmp) != 1:
                    raise Exception('subqueries must return a single value')
                val = tmp[0].values()[0]

            if predicate.navigation[-1] == '_id':
                r[ prefix + 'id'] = val
            else:
                r[ prefix + 'field_set__field__name'] = predicate.navigation[-1]
                r[ prefix + 'field_set__value'] = val
            rs = rs.filter(**r)

    if not q.selector:
        return __to_dict(rs, use_computed_fields=q.compute)
    else:
        return __to_dict(rs, q.selector)

def __to_dict(rs, selector=None, optim=True, use_computed_fields=False):
    '''Navigations are done entirely in memory to avoid hitting too much the database'''
    res = []

    ## All data
    if not selector:
        rs = rs.prefetch_related(Prefetch('field_set', queryset=ComponentInstanceField.objects.select_related('field')))
        rs = rs.prefetch_related(Prefetch('rel_target_set', queryset=ComponentInstanceRelation.objects.select_related('field')))
        rs = rs.select_related('implementation')
        rs = rs.prefetch_related('environments')

        for ci in rs.all():
            compo = {}
            res.append(compo)

            compo['mage_id'] = ci.id
            compo['mage_cic_id'] = ci.instanciates_id
            compo['mage_deleted'] = ci.deleted
            compo['mage_implementation_id'] = ci.implementation_id
            compo['mage_implementation_name'] = ci.implementation.name
            compo['mage_environments'] = ','.join([e.name for e in ci.environments.all()])

            for fi in ci.field_set.all():
                compo[fi.field.name] = fi.value

            for fi in ci.rel_target_set.all():
                compo[fi.field.name + '_id'] = fi.target_id

            if use_computed_fields:
                for cf in ci.implementation.computed_field_set.all():
                    compo[cf.name] = cf.resolve(ci)

        return res

    ## Preload data
    if optim:
        for navigation in selector:
            for idn in navigation:
                pass

        #rs = rs.prefetch_related(Prefetch('field_set', queryset=ComponentInstanceField.objects.select_related('field')))
        #rs.prefetch_related('rel_target_set')
        #return {}

        rs = rs.prefetch_related(Prefetch('rel_target_set', queryset=ComponentInstanceRelation.objects.select_related('field', 'target')))
        rs = rs.prefetch_related(Prefetch('rel_target_set__target__field_set', queryset=ComponentInstanceField.objects.select_related('field')))
    #    rs = rs.prefetch_related('rel_target_set__target__field_set__field')

    ## Fetch!
    for ci in rs.all():
        compo = {}
        res.append(compo)

        for navigation in selector:
            tmp = ci
            for idn in navigation:
                if navigation.asList().index(idn) == len(navigation) - 1:
                    # the end of the line is always a value field
                    found = False
                    for fi in tmp.field_set.all():
                        if fi.field.name == idn:
                            found = True
                            compo['_'.join(navigation.asList())] = fi.value
                    if not found:
                        raise Exception("'%s' is not a valid value attribute" % idn)
                else:
                    # navigation
                    found = False
                    for rel in tmp.rel_target_set.all():
                        if rel.field.name == idn:
                            tmp = rel.target
                            found = True
                            break
                    if not found:
                        raise Exception("'%s' is not a valid relationship attribute" % idn)


    print res
    return res
