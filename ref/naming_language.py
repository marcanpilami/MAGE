# coding: utf-8

import traceback

from pyparsing import alphas, Group, OneOrMore, nums, ZeroOrMore, Forward, QuotedString, \
    Word, Suppress, Literal, Optional, Combine

# %client_url?("http://"|%group.dns_to_use?%group.domain.name|":"|"123"

def build_grammar():
    expr = Forward()
    # Our identifier definition is Python's one with the added constraint of not allowing underscores as first character. 
    identifier = Combine(Word(alphas, exact=1) + Optional(Word(nums + alphas + "_")))("identifier")    
    navigation = Group(Suppress("%") + identifier + ZeroOrMore(Suppress(".") + identifier))("navigation")
    text = QuotedString('"', escQuote='""')("text")
    numeric = Word(nums)('num')
    
    datatoken = (navigation | text | numeric)('datatoken')
    
    expr << Group(((datatoken | Suppress("(") + expr + Suppress(")"))('left') + ZeroOrMore(Group(Word("?|+-*/", exact=1)('op') + (datatoken | Suppress("(") + expr + Suppress(")")))('ppp'))('additional')))("expr")    
    return expr

__grammar = build_grammar()  #.setDebug()

def resolve(pattern):
    print '**********************************************************'
    print pattern
    res = __grammar.parseString(pattern)
    print res.dump()
    print res
    expr(res)
    
def expr(e):
    ## String or numeric: return it (end of recursion 1)
    if type(e) == 'str':
        return e
    
    
    
    i = 0    
    tokens = e.expr.asList()
    while i < len(tokens):
        operand1
        
