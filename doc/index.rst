############
MAGE
############

*****************
Introduction
*****************

MAGE is an assistant for managing the different environments all big IT projects will eventually end up with (development, acceptance, integration, preproduction, etc). It will never *do* any action on the environments by itself, such as installing a patch, but will provide many tools to help script these actions (the list of which is specific to each project) and to keep tabs on the environments (this was installed at that time, etc).

Basically, it's a scripting toolbox with some kind of CMDB and DSL designed for out-of-production environments, as well as a publishing portal for all these data.

A partial list of functions:

* A referential for the environments. What is their content (databases, programs, configurations, ... basically anything is possible), the description of these contents (login/password, directory paths, ...). A simple query API, accessible through a simple HTTP GET, is provided.
	* **Scripting API**: this enables a huge deal of automation in scripts. For exemple, a shell script suposed to backup all environments will only have to query MAGE for the elements to backup and will retrieve all necessary data - such as connection information. All it has to know for this is a MAGE account, and submit a query.
	* **Ease of use**: the referential was built with ease of use in mind. For exemple, every environment can easily be cloned instead of having to define every component. It is even possible to define templates.
	* **Naming conventions**: MAGE can also help enforce naming conventions (which will be automatically applied on an environment duplication for exemple).
	* **Easy admin**: a fully-featured web site to easily manage your environments, change names, descriptions, every last piece of data stored in the referential. It is based on the Django admin site, for those who know this marvelous little web framework.
	* **Publication**: Web pages with clear graphs and tables are automatically created to provide all the data the environments users will need.
* A  full SCM system
	* **SCM referential**: stores references to every patchset/installset/binaries/..., the associated versions.
	* **Configuration ordering**: whatever the version naming convention is (A, B, C or 321.1.2, 2.2.3, or really whatever), MAGE will be able to determine a version order thanks to a nifty dependency system (a delivery is either FULL without depdendencies on other components versions OR requires other components to be at a certain version level (exact, or superior to, or inferior to)).
	* **Backup tracking**: backups are just another kind of FULL patchset - and so are treated as such. A special API is provided to enable scripts to easily store backup data with simple HTTP GETs.
	* **Configuration tracking**: the heart of the SCM module. Each time a configuration is modified through the installation of a patchset (or assimilated), it should be registered (through a simple GET). MAGE will then provide many web pages detailing the history of environments, the current versions of elements, a time machine, etc.: basicaly, all the SCM views that are usually needed on big IT projects, and then some.
	* **Publication**: all the data is made freely accessible to everyone on web pages, limiting the volume of basic and unproductive questions the IT team may receive.


**********
Contents
**********

.. toctree::
	:maxdepth: 2
	
	install
	starting
	mql
	conventions

	