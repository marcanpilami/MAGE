Starting to use
######################

.. py:module:: ref.models

MAGE is rather generic, allowing to specify a wide variety of environment types in various contexts.

Before starting to use MAGE, there are a few notions that must be defined in the tool in the order given here.

It is recommended to read the page fully before actually setting parameters. Afterwards, connect to the administration interface (default is site_root/admin), login (with the super user created during install) and for each paragraph create the desired objects.

Setting the context
******************************

Classifiers
=====================

At the beginning of a project, the first thing is to describe the project itself. Two objects exist for this. This classification is supposed to be time-stable.

The second thing is to describe the environments that will be used. This can be a first-draft classification, as it can evolve easily.

Project
---------------------

A project is nothing more than a classifier. It has no other interest than to regroup Environments (an Environment belongs to zero or one Project).

It's main use is in Conventions, which can make use of its name and alternative names. It is also the bearer of the default Convention for all its Environments.


Application
---------------------

This is a second level of classification: a project may have zero to many Applications. It can also be used in Conventions. THe different Logical Components (see below) belong to one (and only one) Application.


.. note:: 'Project' and 'Application' are just names. They can be considered as "Big project" and "Sub project", or "Program" and "Project", etc.

Environment Type
---------------------

Each environment has - optionally - one associated Type. It provides common value :

* an optional SLA
* a typology (production, conformity, ...)
* a default Convention (that replaces the Convention given by the Project, if any) 

At the beginning of the project, the first few types should be referenced. The list can be completed later - but not purged.

Environment
---------------------

A potentialy partial implementation of the functional and logical architecture of an IT perimeter, aiming at fullfilling the needs of a certain population at a given period of the lifecycle of a system.

Basically: a bunch of items that may belong to other environments too. 'Item' will be defined later.

Most of the time, they are built (in MAGE, but also in reality) by copying another.

.. py:class:: Environment
	
	.. py:attribute:: Environment.name
	.. py:attribute:: Environment.buildDate
	
		Default is at the time the Python object is created.
		
	.. py:attribute:: Environment.destructionDate
	
		Planned destruction. Nullable.
	
	.. py:attribute:: Environment.description
	
		Not nullable.
		
	.. py:attribute:: Environment.manager
	
		Name of the person in charge of using the environment. (often: team leader). Nullable.
		
	.. py:attribute:: Environment.project
	
		Nullable.
		
	.. py:attribute:: Environment.typology
	
		An environment type. Not nullable.
		
	.. py:attribute:: Environment.template_only
	
		Default False. All environments can be copied and serve as templates for creating others. If this is ticked, the environment will only be used for templating (there should be no actual implementation of the template)

		
At the beginning of a project, a first representative environment should be created though the admin (complete with component instance, described below) for every different environment "template" you'll have. This template will then be copied each time a new environment is created. During copy, the following elements are preserved or remapped:

* members of the environment are all copied (the list can be filtered azs a parameter - so the template can be "too complete")
* relationships between members of the source environment become relationships between the copied members
* relationships between members of the source environment and other items not member of the environment are preserved as-is in the copy, unless explicitely remapped (parameter). For exemple, an application server belonging to the source environment runs on a Windows server that does not belong to the environment. The copy of the environment will have a new application server running on the same server.
* some naming conventions will be applied to the copy (for exemple, to change the component instance names)
		
Environment content
==========================================

After the context is fully described, it is time to fill in the environments with data that will be useful for scripting, configuration tracking, ... There are two categories here: 

* foundations. They describe how items should be managed. They will not change (or only a little) during the life of the project. 
* implementations. They will describe the often ephemeral managed technical items.

Foundations
----------------------------

Logical Component
^^^^^^^^^^^^^^^^^^^^^^^^^^^

It represents the "essence" of an item of the project. It can be an application, a configuration, a program... whatever. Choosing the right granularity for LC is crucial - they are the foundation of everything else. 
As a rule of thumb, a LC corresponds to an element you want to track in configuration/version on its own. The more there are, the more complicated it will get but the more precise the collected data will be.

Now, choosing the configuration tracking granularity is up to the user, as no tool will ever automate this - there are many trade offs and therefore many different solutions.

.. py:class:: LogicalComponent

	.. py:attribute:: LogicalComponent.name

		The name of the logical component

	.. py:attribute:: LogicalComponent.application

		The application the component belongs to (compulsory)
		
	.. py:attribute:: LogicalComponent.description

		A (very) short text describing the use of the LC
		
	.. py:attribute:: LogicalComponent.scm_trackable

		Default is True. If False, this LC will never be used in any Configuration Management operation (backup, update, ...)
	
Component Implementation Class
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This is a technical way of actualy implementing a logical component. 

For exemple, if the LC is "Application A data storage", there may be many CIC :

* an Oracle database schema
* a PostgreSQL database
* ... whatever RDBMS

In a single project, all these possibilities may be used. To build on the previous exemple, Oracle will be used in production but as Oracle is expensive, developpers will use PostegreSQL. This is why the distinction (an abstraction level, actually) between the CIC and the LC is very important.

.. note:: obviously, in in simple project, nothing prevents you from having only one CIC for a LC.

.. py:class:: ComponentImplementationClass

	.. py:attribute:: ComponentImplementationClass.name
	
	.. py:attribute:: ComponentImplementationClass.description
	
	.. py:attribute:: ComponentImplementationClass.implements
	
		The :py:class:`LogicalComponent` implemented
		
	.. py:attribute:: ComponentImplementationClass.sla
	
		An optional :py:class:`SLA` object
		
	.. py:attribute:: ComponentImplementationClass.python_model
	
		A ContentType object, i.e. a reference to a Python class that will be used to actually instanciate the CIC. This class will have to completely describe the technical implementation used on the project - most notably, what attrtibutes are necessary (a login? a password? a port? etc.). A few classes are provided with MAGE (for Websphere Servers, for Oracle Databases, etc), and you can extend with your own Python classes - see :ref:`extending`.

Conventions
^^^^^^^^^^^^^^^^^^^^^^^^^^^
		
A Convention is a way to specify rules to create Component Instances. Most notably, it specify naming conventions. For more information, see :doc:`conventions`
		

Implementation
-------------------------

Component Instance
^^^^^^^^^^^^^^^^^^^^^^^^^^^

A component Instance is the representation of an actual "thing" managed on the project. Basicaly, it is an instance of CIC. To clarify things :

* Logical Component = "Application A data store"
* Component Implementation Class = "Oracle schema for A data store"
* Component Instance = "schema my_schema_name"

The component instance is described by the :py:attr:`ComponentImplementationClass.python_model` attribute of the CIC. However, all CI have a few common attributes.

.. py:class:: ComponentInstance

	.. py:attribute:: name
	
		The meaning of this attribute depends of the described CIC. However, it should always enable the user to identify an instance.
		
	.. py:attribute:: instanciates
	
		The :py:class:`ComponentImplementationClass` implemented.
		
	.. py:attribute:: deleted
	
		Instances are never deleted - they are hidden when they do not exist anymore in the real world. This enables to having a consistent configuration tracking (for exemple, backups still exist when an environment is destroyed, and the user may want one day to restore it without loosing all the version data associated to it)
		
	.. py:attribute:: environments
	
		The different environments the instance belongs to. It may belong to multiple environment (may be the case for a shared middleware) or to none (it may make no sense to attribute a shared server to the environments it supports)
		
	.. py:attribute:: leaf
	
		This a read-only and code-only (nothing in the administration interface) property. Gives access to the subtype.
		
	The following are MAGE internals and should not be modified in code - and they will not appera in the administration interface.
	
	.. py:attribute:: connectedTo
	
	.. py:attribute:: dependsOn
	
	.. py:attribute:: model


.. warning:: often, only "component" is used instead of Component Instance.

At the beginning of a project, the new environments (ctraed at the beginning of this page) should be filled with component instances. Contrary to all other elements described on this page, there is no "Component Instance" page in the admin site. There is a page, however, for every different type of CI available: a page for Glassfish application servers, one for Oracle instance, another for servers...

Building environments in MAGE is actually building a tree: an application server is linked to a server, etc. These relationships are fundamental to MAGE: graphs, queries all rely on them.

.. _extending:

Extending MAGE with project-specific models
**************************************************

