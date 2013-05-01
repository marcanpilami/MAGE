MCL
############

.. toctree::

Introduction
-----------------------

MCL is a query and component creation language.

Grammar (EBNF)
-----------------------

::

	mcl_query ::= '(' ('(T,' component_type ')' )? ('(S,' attribute_filter (',' attribute_filter)* ')')? ('(P,' (parent_field_name ',')+ mcl_query ')')* ('(C,' mcl_query ')')* ')'

	attribute_filter ::= attribute_name ('.' attribute_name)* '=' (('"' .+ '"') | '@' attribute_name | mcl_query )

	attribute_name ::= [a-zA-Z0-9_]+

	parent_field_name ::= attribute_name 

*mcl_query*: 

.. image:: media/mcl_query.png


*attribute_filter*:

.. image:: media/attribute_filter.png	

*attribute_name*:

.. image:: media/attribute_name.png	

*parent_field_name*:

.. image:: media/parent_field_name.png	

*Diagrams generated with http://railroad.my28msec.com/rr/ui*

How to query
-----------------------

MCL is a **filter** language. That means that it works in a negative fashion: you begin with every existing omponent instances, and the more filters you add, the less instances survive. It also means that everything is optional in MCL, but the outer parenthesis - in this case, every single last instance is returned.

This section introduces all the different filters, from the simplest to the more complicated.

Query on attributes (simple)
++++++++++++++++++++++++++++++++++++++++++++

In this case, the user knows a few attributes (usually the name) of the required component instance.::

	(S,attribute="value",otherattribute="othervalue",...)
	
S means Self. Double inverted commas are compulsory. In case there are some in the value, double them to escape them.

.. warning:: if no type is given (see next paragraph), only base instance attributes can be queried (name, description)

.. note:: Queriable attributes are documented

Exemples:::

	((S,name="waPRDINT2"))
	((S,environments="PRD1"))
	((S,description="it's ""beautiful""",name="marsupilami"))

Query on type
++++++++++++++++++++++++++++++++++++++++++++

There are many component instance types: Oracle instances, web servers, batch programs, etc. To filter on this:::

	(T,componenttype)
	
T means Type.

Example::

	((T,wascluster))

Query on attributes (reference)
++++++++++++++++++++++++++++++++++++++++++++

In this case, the user doesn't know the value of an attribute but knows it is equal to another attribute.::

	(S,attribute=@otherattribute)
	
Note the absence of inverted commas.

Exemple::

	((S,login=@password))
	
Query on attributes (relations)
++++++++++++++++++++++++++++++++++++++++++++

In this case, the query is on the attributes of a related instance.::

	(S,linkattribute.attribute="value")
	
Beware in this case if you use the @ notation - it refers to the base instance, not the related one. There could be more than two levels.

Exemple::

	((S,instance.name="MYORACLEINSTANCE"))
	
looks for every component instance which has an instance named MYORACLEINSTANCE.

Query on parents
++++++++++++++++++++++++++++++++++++++++++++

Instances have a special set of relationships called Parents. To query on this relationships, just create a sub query inside a (P,)::

	((P,((S,name="MYORACLEINSTANCE"))))

Same thing with connected instance with (C,)

Mixing it all
++++++++++++++++++++++++++++++++++++++++++++

Just collate the different filters in this order: T, S, P, C. For exemple::

	((T,wasapplication)(S,name="module1")(P,((T,wascluster)(P,((T,osserver)(S,name="server1"))))))
	
will look for applications named module1 that run on a cluster running on server1.