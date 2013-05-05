Conventions
###############

.. toctree::


Introduction
-----------------------

Conventions are a way to rationalize the way components are named and created. They should reflect both the naming conventions of your project and its environment templates.


Naming convention patterns
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

NOPROJECT.

Current date
++++++++++++++++++++++++

+---------------+--------------------------------------------------------+
| Pattern       | Interpretation                                         |
+===============+========================================================+
| %d%           | current date (japanese format: YYYYMMDD)               |
+---------------+--------------------------------------------------------+

Implementation class
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

.. note:: a CIC name is supposed to be descriptive and therefore ill-adapted to naming use. This explains its abscence from the list above.


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

Counters are incremented each time they are used. They begin at 1. The "next value" can be modified through the admin website.

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

This counter has no scope.

%cg%

Model counter
+++++++++++++++++++++++++++

This counter has an environment + model scope. There is one counter for each model in an environment. Therefore, you can track your different databases without incrementing the counter for your appplication servers.

%cem% 

Relationships conventions
-------------------------------

Relationships are described with standard :ref:`MCL queries<mclquery>`. In addition to the standard syntax, you can use the patterns described above.
Most often, the query will simply specify the name pattern and type of another component instance.

.. note:: you actually don't need to give the type. As the relationship definition includes the type, it will be inferred during the query.

Please note that your queries must return the adequate number of results, or an error will be raised.

