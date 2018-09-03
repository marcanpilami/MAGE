# coding: utf-8

from pyparsing import alphas, Group, nums, ZeroOrMore, Forward, QuotedString, \
    Word, Suppress, Optional, Combine

from django.core.cache import cache

def build_grammar():
    expr = Forward()
    # Our identifier definition is Python's one with the added constraint of not allowing underscores as first character.
    identifier = Combine(Word(alphas, exact=1) + Optional(Word(nums + alphas + "_")))("identifier")
    navigation = Group(identifier + ZeroOrMore(Suppress(".") + identifier))("navigation")
    text = QuotedString('"', escQuote='""')("text")
    numeric = Word(nums)('num')
    operator = Word("?|+-/*", exact=1)("operator")

    datatoken = Group(navigation | text | numeric)('datatoken')

    # expr << Group(((datatoken | Suppress("(") + expr + Suppress(")")) + ZeroOrMore(Group(operator + (datatoken | Suppress("(") + expr + Suppress(")")))('operand'))('right_group')))("expr")
    expr << Group(((datatoken | Suppress("(") + expr + Suppress(")")) + ZeroOrMore(Group(operator + (datatoken | Suppress("(") + expr + Suppress(")")))('operand'))('right_group')))("expr")

    return expr

__grammar = build_grammar()  #.setDebug()

def resolve(pattern, instance, field_id=None):
    # Always use the true Django object
    try:
        instance = instance._instance  
    except:
        pass

    # Cache?
    if field_id:
        key = 'computed_%s_%s' % (field_id, instance.pk)
        cached = cache.get(key)
        if cached:
            if cached == 'NonePpokiGFVGH':
                return None
            else:
                return cached

    expression = parse(pattern)
    res = __resolve_expr(expression.expr, instance)
    if field_id:
        if res is None:
            cache.set(key, 'NonePpokiGFVGH')
        else:
            cache.set(key, res)
    return res

def parse(pattern):
    """Parses the given pattern and throws an exception if it is wrong. Used to check patterns."""
    return __grammar.parseString(pattern)

def __resolve_datatoken(datatoken, instance):
    res = ""

    if datatoken.num:
        res = int(datatoken.num)
    elif datatoken.text:
        res = datatoken.text
    elif datatoken.navigation:
        res = __resolve_navigation(datatoken.navigation, instance)

    return res

def __resolve_expr(e, instance):
    if e.expr:
        left = __resolve_expr(e.expr)
    else:
        left = __resolve_datatoken(e.datatoken, instance)

    if not e.right_group:
        return left

    for group in e.right_group:
        operator = group.operator
        if group.expr:
            right = __resolve_expr(group.expr, instance)
        else:
            right = __resolve_datatoken(group.datatoken, instance)

        if operator == "|":
            left = "%s%s" % (left, right)
        elif operator == "?":
            if left :
                return left
            if right:
                return right
        elif operator == '+':
            left = int(left) + int(right)
        elif operator == '-':
            left = int(left) - int(right)
        elif operator == '*':
            left = int(left) * int(right)
        elif operator == '/':
            left = int(left) / int(right)

    return left


def __resolve_navigation(path, instance):
    ''' Will instanciate a pattern according to the value inside the given component instance'''

    # Import here to avoid circular imports
    from ref.models.instances import ComponentInstanceField, ComponentInstance

    if path[-1] == 'mage_id':
        req = {}
        m = ""
        for segment in path[-2::-1]:
            req[m + 'rel_targeted_by_set__field__name'] = segment
            m = m + 'reverse_relationships__'
        req[m + 'id'] = instance.id
        res = ComponentInstance.objects.filter(**req).all()

        return res[0].id if len(res) == 1 else None
    else:
        req = {'field__name': path[-1]}
        m = "instance__"
        for segment in path[-2::-1]:
            req[m + 'rel_targeted_by_set__field__name'] = segment
            m = m + 'reverse_relationships__'
        req[m + 'id'] = instance.id
        res = ComponentInstanceField.objects.filter(**req).all()

        return res[0].value if len(res) == 1 else None
