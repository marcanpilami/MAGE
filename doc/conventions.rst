Conventions patterns
##########################

.. toctree::


Introduction
-----------------------

Conventions are a way to rationalize the way components are named and created and speed up their creation.
They should reflect both the naming conventions of your project and its environment templates.

A convention can be defined for each standard field inside the component description (it is the 'default' field). They are used:

* when a new component instance is created. All fields that have a default/convention value are set with it.
* when an environment is duplicated, all fields with a default/convention are reset with it.

Please note it is not compulsory to use conventions patterns as a default - a simple value - or nothing - is enough. But
it is **strongly recommended** to use them as they allow one click component instance creation, minimizing the risk of error.

Simple naming patterns
-------------------------------

Environment
+++++++++++++++++

+---------------+-------------------------------------------+
| Pattern       | Interpretation                            |
+===============+===========================================+
| %e%           | environment name (lower case)             |
+---------------+-------------------------------------------+
| %E%           | environment name (upper case)             |
+---------------+-------------------------------------------+

If the component does not belong to an environment, NOENVIRONMENT will be used.

Application
++++++++++++++++

+---------------+--------------------------------------------------------+
| Pattern       | Interpretation                                         |
+===============+========================================================+
| %a%           | application name (lower case)                          |
+---------------+--------------------------------------------------------+
| %A%           | application name (upper case)                          |
+---------------+--------------------------------------------------------+
| %a1%          | application alternate name 1 (lower case)              |
+---------------+--------------------------------------------------------+
| %A1%          | application alternate name 1 (upper case)              |
+---------------+--------------------------------------------------------+
| %a2%          | application alternate name 2 (lower case)              |
+---------------+--------------------------------------------------------+
| %A2%          | application alternate name 2 (upper case)              |
+---------------+--------------------------------------------------------+
| %a3%          | application alternate name 3 (lower case)              |
+---------------+--------------------------------------------------------+
| %A3%          | application alternate name 3 (upper case)              |
+---------------+--------------------------------------------------------+

If no application, NOAPPLICATION will be used.

Project
++++++++++++++

+---------------+--------------------------------------------------------+
| Pattern       | Interpretation                                         |
+===============+========================================================+
| %p%           | project name (lower case)                              |
+---------------+--------------------------------------------------------+
| %P%           | project name (upper case)                              |
+---------------+--------------------------------------------------------+
| %p1%          | project alternate name 1 (lower case)                  |
+---------------+--------------------------------------------------------+
| %P1%          | project alternate name 1 (upper case)                  |
+---------------+--------------------------------------------------------+
| %p2%          | project alternate name 2 (lower case)                  |
+---------------+--------------------------------------------------------+
| %P2%          | project alternate name 2 (upper case)                  |
+---------------+--------------------------------------------------------+
| %p3%          | project alternate name 3 (lower case)                  |
+---------------+--------------------------------------------------------+
| %P3%          | project alternate name 3 (upper case)                  |
+---------------+--------------------------------------------------------+

NOPROJECT if no project.

Current date
++++++++++++++++++++++++

+---------------+--------------------------------------------------------+
| Pattern       | Interpretation                                         |
+===============+========================================================+
| %d%           | current date (japanese format: YYYYMMDD)               |
+---------------+--------------------------------------------------------+

Offer
+++++++++++++++++++++++++

+---------------+--------------------------------------------------------+
| Pattern       | Interpretation                                         |
+===============+========================================================+
| %ic1%         | CIC field ref1                                         |
+---------------+--------------------------------------------------------+
| %ic2%         | CIC field ref2                                         |
+---------------+--------------------------------------------------------+
| %ic3%         | CIC field ref3                                         |
+---------------+--------------------------------------------------------+

.. note:: a CIC name is supposed to be descriptive and therefore ill-adapted to naming use. This explains its absence from the list above.


Logical component
+++++++++++++++++++++++++

+---------------+--------------------------------------------------------+
| Pattern       | Interpretation                                         |
+===============+========================================================+
| %lc1%         | LC field ref1                                          |
+---------------+--------------------------------------------------------+
| %lc2%         | LC field ref2                                          |
+---------------+--------------------------------------------------------+
| %lc3%         | LC field ref3                                          |
+---------------+--------------------------------------------------------+

Naming convention counters
-------------------------------------

Counters are incremented each time they are used. This is why creating a component instance always begins with a specific form, and not inside
the admin application - this allow MAGE to always use the counters.
However, should a counter become desynchronized, it is possible to set its value through the admin.

They all begin at 1, and have different scopes. The scope is what defines the counter to increment in each case. 
For example, an environment scope means there is one counter per environment. Two different items inside the same environment using an environment scope will actually
use the same counter.

Counters can be formatted by giving a number of figures after the classifier of the counter.

Environment counter
++++++++++++++++++++++++

This counter has an environment scope.

%ce%

Project counter
++++++++++++++++++++++++++

This counter has a project scope (therefore multiple applications)

%cp%

Global counter
++++++++++++++++++++++++++

This counter has no scope. There is only one such counter.

%cg%

Model + environment counter
+++++++++++++++++++++++++++++

This counter has an environment + component description scope. There is one counter for each description in an environment. Therefore, you can track your different databases without incrementing the counter for your application servers.

%cem% 

Model counter
+++++++++++++++++++++++++++++

This counter has a component description scope. There is one counter for each description.

%cm%

Instance counter
+++++++++++++++++++++++++++++

This counter is scoped by another component instance designated by a dotted-path expression ending on an instance ID.

%cidotted.expression.to.id%

Example for the 'port' field of an application server, sitting on a Unix server designated by the 'server' field'::

    1788+%ci2server.mage_id% 
    
This will give a port, starting at 1789, which is unique for the Unix server (that means if there are many servers each hosting multiple AS,
each server will have ASs running on ports 1789, 1790, ... without duplicates or holes in the sequence.)

.. note::
    MAGE always adds a field named mage_id to every component instance to help using this feature.
 

Relation counter
+++++++++++++++++++++++++++++

This counter has a component description scope. There is one counter for each description.

%n%

Expression patterns
----------------------------

This is a special pattern that can only be applied after all fields and relationships have been set on an instance. 
It consists in a *navigation expression*, as detailed elsewhere.

For example, if your convention is that the JMX monitoring port is HTTP port + 1000, it can be specified as::

    %nport%+1000
    
%n means expression pattern (n means navigation).

As this is applied in a second place, it is still possible to have a counter giving the value of port. This will work perfectly::

    port => 1788+%ci2server.mage_id%
    jmx_port => %nport%+1000
    
 
.. note:: every result of the application of any type of pattern is eventually valued as an integer - it it doesn't work nothing is done, if
   it works the result of the valuation becomes the new value for the field. 