Preparing MAGE for first use
###############################

.. py:module:: ref.models

MAGE is rather generic, allowing to specify a wide variety of environment types in various contexts.
Therefore, before starting to use MAGE, there are a few notions that must be defined in the tool in the order given here.

It is recommended to read the page fully before actually setting parameters. Afterwards, connect to the administration 
interface (default is site_root/admin, there is an 'A' link in the top right corner of the home page), login (with the 
super user created during install) and for each paragraph create the desired objects.

.. warning:: the idea is to follow the order given in the page 'new reference items', available from the home page.

Setting the technical context
*********************************

The first thing to do is to decide how to model the different environments.  The main ideas here are:

* every 'item' that can be packaged separately and has to be tracked (as in version tracking) must have its own component description.
* every data needed for administration (DNS, login, ports...) must be available in the model. Links between component descriptions must make this information
  available simply in the context of a modification of configuration of the tracked elements. (if a Java war package is installed, it must be easy to go
  from the package to the admin URL for example).
* the simpler, the better!

For each component that was identified, a **component description** must be created. It is simply a list of fields and relationships.

.. note:: the standard way of creating these is through the administration web UI (follow the links inside the 'new reference items' page). Scripting is also possible.

Basics attributes
=====================

* Name - this is a code that will be used when a short and stable in time name is preferable
* Description - the verbose 'public' name.
* Tag - a simple unbound classifier. Please use a tag, it makes many page more readable.
* Self description pattern: a *component expression* which resolution gives the 'name' of instances.

Simple fields. A simple field is just what its name entails - a key/value pair. Values are always stored as strings, even if a data type must be provided.
The data type is actually used for widget selection and controls.

* short name: a valid Python identifier. (no spaces, letters and digits and underscores, cannot begin with an underscore or with mage\_)
* label: verbose name used in forms
* compulsory: for validation
* sensitive: if True, the values will be hidden to anyone but admins and scripts (NOT published to everyone)
* widget row: if None, won't be published inside the environment description page. Otherwise, this gives the order of fields in that page.

Relationship fields
=====================

Computed fields
=====================

It is often interesting to make deductions instead of forcing administrators to input everything with many repetitions.
Computed fields exist for that. They allow to retrieve data from linked instances, to make basic mathematics operations, to compose strings, to fallback on another field if it is null, etc.
Please read the *component expression* reference and the samples for this.

Setting the applicative context
*********************************

Project
=====================

A project is nothing more than a classifier. It has no other interest than to regroup Environments (an Environment belongs to zero or one Project).

It's main use is in :doc:`conventions`, which can make use of its name and alternative names.


Application
=====================

This is a second level of classification: a project may have zero to many Applications. It can also be used in Conventions. The different 
Logical Components (see below) all belong to one (and only one) Application, so this is a very important classifier.


.. note:: 'Project' and 'Application' are just names. They can be considered as "Big project" and "Sub project", or "Program" and "Project", etc.


Logical Component (LC)
============================

It represents the "essence" of an item of the project. It can be an application, a configuration, a program... whatever. Choosing the right granularity for LC is crucial - they are the foundation of everything else. 
As a rule of thumb, a LC corresponds to an element you want to track in configuration/version on its own. The more there are, the more complicated it will get but the more precise the collected data will be.

Now, choosing the configuration tracking granularity is up to the user, as no tool will ever automate this - there are many trade-offs and therefore many different solutions.

.. py:class:: LogicalComponent

	.. py:attribute:: LogicalComponent.name

		The name of the logical component

	.. py:attribute:: LogicalComponent.application

		The application the component belongs to (compulsory)
		
	.. py:attribute:: LogicalComponent.description

		A (very) short text describing the use of the LC
		
	.. py:attribute:: LogicalComponent.scm_trackable

		Default is True. If False, this LC will never be used in any Configuration Management operation (backup, update, ...)
	
Implementation Offer (CIC)
============================

.. note:: internally, MAGE refers to this as a Component Implementation Class (CIC)

This is a technical way of actually implementing a logical component. 

For example, if the LC is "Application B data storage", there may be many CICs :

* an Oracle database schema
* a PostgreSQL database
* ... whatever RDBMS

In a single project, all these possibilities may be used. To build on the previous example, Oracle will be used in production 
but as Oracle is expensive, developers will use PostgreSQL. This is why the distinction (an abstraction level, 
actually) between the CIC and the LC is very important.

.. note:: obviously, in in simple project, nothing prevents you from having only one CIC for a LC.

.. py:class:: ComponentImplementationClass

	.. py:attribute:: ComponentImplementationClass.name
	
	.. py:attribute:: ComponentImplementationClass.description
	
	.. py:attribute:: ComponentImplementationClass.implements
	
		The :py:class:`LogicalComponent` implemented
		
	.. py:attribute:: ComponentImplementationClass.sla
	
		An optional :py:class:`SLA` object
		
	.. py:attribute:: ComponentImplementationClass.description
	
		The description object that will be used to actually instantiate the CIC. See above.

Environments
***********************
        
Environment Type
============================

Each environment has - optionally - one associated Type. It provides common values for :

* an optional SLA
* a typology (production, conformity, ...)
* backup related parameters
* types of component that are allowed for these environments.

At the beginning of the project, the first few types should be referenced. The list can be completed later - but never purged, as it would allow to re-write history.

Environment
============================

A potentially partial implementation of the functional and logical architecture of an IT perimeter, aiming at fulfilling the needs of a 
certain population at a given period of the life-cycle of a system.

Basically: a bunch of items that may belong to other environments too. 'Item' will be defined later.

Most of the time, they are built (in MAGE, but also in reality) by copying another one. Save, obviously, for the first one.

.. py:class:: Environment
	
	.. py:attribute:: Environment.name
	.. py:attribute:: Environment.buildDate
	
		Default is at the time the Python object is created.
		
	.. py:attribute:: Environment.destructionDate
	
		Planned destruction. Nullable.
	
	.. py:attribute:: Environment.description
	
		Not nullable. Displayed pretty much everywhere.
		
	.. py:attribute:: Environment.manager
	
		Name of the person in charge of using the environment. (often: team leader). Nullable.
		
	.. py:attribute:: Environment.project
	
		Nullable.
		
	.. py:attribute:: Environment.typology
	
		An environment type. Not nullable.
		
	.. py:attribute:: Environment.template_only
	
		Default False. All environments can be copied and serve as templates for creating others. If this is ticked, the environment will only be used for templating (there should be no actual implementation of the template)

		
At the beginning of a project, a first representative environment should be created though the admin (complete with component instance, described below) for every different environment "template" you'll have. This template will then be copied each time a new environment is created. During copy, the following elements are preserved or remapped:

* members of the environment are all copied (the list can be filtered as a parameter - so the source template can be "too complete")
* relationships between members of the source environment become relationships between the copied members
* relationships between members of the source environment and other items not member of the environment are preserved as-is in the copy, unless explicitly remapped (parameter). For example, an application server belonging to the source environment runs on a Windows server that does not belong to the environment. The copy of the environment will have a new application server running on the same server.
* some naming conventions will be applied to the copy (for example, to change the component instance names)
		
Environment content
**************************************

After the context is fully described, it is time to fill in the environments with data that will be useful for scripting, configuration tracking, ...  


Component Instance
============================

A component Instance is the representation of an actual "thing" managed on the project. Basically, it is an instance of CIC. To clarify things :

* Logical Component = "Application B data store"
* Component Implementation Class = "Oracle schema for B data store with High Availability"
* Component Instance = "schema my_schema_name (described by the items listed in Component Description "Oracle Schema")"

The component instance is described by the :py:attr:`ComponentImplementationClass.description` attribute of the CIC. However, all CI have a few common attributes.

.. py:class:: ComponentInstance

	.. py:attribute:: name
	
		The meaning of this attribute depends of the described CIC. However, it should always enable the user to identify an instance.
		
	.. py:attribute:: instantiates
	
		The :py:class:`ComponentImplementationClass` implemented.
		
	.. py:attribute:: deleted
	
		Instances are never deleted - they are hidden when they do not exist any more in the real world. This enables to having a consistent configuration tracking (for example, backups still exist when an environment is destroyed, and the user may want one day to restore it without loosing all the version data associated to it)
		
	.. py:attribute:: environments
	
		The different environments the instance belongs to. It may belong to multiple environment (may be the case for a shared middleware) or to none (it may make no sense to attribute a shared server to all the environments it supports)
	
.. warning:: often, only "component" is used instead of "Component Instance".

At the beginning of a project, the new environments (created at the beginning of this page) should be filled with component instances. Contrary to all other elements described on this page, there is no "Component Instance" page in the admin site. This page instead sits inside the main MAGE portal.

