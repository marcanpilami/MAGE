Installation
###################

Prerequisites
********************


* OS: every OS with a supported Python 2.7 distribution. (Windows, most Linux distributions, Solaris, ...)
* Python 2.7.x (not Python 3.x)
* Python easy install (may be included in your Python distribution, otherwise download http://peak.telecommunity.com/dist/ez_setup.py and run python ez_setup.py)
* Graphviz (latest available version on your platform,. The 'dot' executable must be in the PATH)
* A git client (on Windows, the recommended distribution is github's http://msysgit.github.io/)
* Optionaly, a database (Oracle >= 10g, PostgresQL, mysql). Default is sqlite 3 - it is bundled with Python, so nothing special is required. In other databases, you will need an account with the permission to create tables, sequences and indexes (or their equivalent in your database).

Django: install these through easy_install :

* django==1.5.1
* pyparsing==1.5.7
* pydot
* ipython
* Sphinx


MAGE itself
*******************

Checkout
=============

Choose a directory in which to install MAGE. This directory will not be accessible to users. It will be refered to as ${MAGE_INSTALL_ROOT} in this document. ::

	git clone git://github.com/marcanpilami/MAGE.git

Settings
==============

Copy the file ${MAGE_INSTALL_ROOT}/MAGE/local_settings.sample.py to ${MAGE_INSTALL_ROOT}/MAGE/local_settings.py

Edit the file. Every setting is explained in the file. Of particular importance are:

* Database configuration. 
* Allowed hosts (unless running in debug mode)
* Static root - this directory will be directly accessible to users
* Template dir, in which the already specified path must be completed with ${MAGE_INSTALL_ROOT}

Sync
=============

In the ${MAGE_INSTALL_ROOT} directory, create the database objects by running::

	python manage.py syncdb
	
You will be asked to create a root account. Accept, and do not forget the password you specify. Then run::

	python manage.py collectstatic

Test
===============

Run::

	python manage.py runserver

This will launch a small web server listening on an address printed on the standard output. With a browser, try this address. You should access MAGE's homepage.

Initial data
=======================

MAGE module authors may provide intiial data with a hook. So just call in your internet browser the page ${ROOT_MAGE_URL}/scm/demo (this will redirect to the home page).

This will delete every last bit of data from the database, and fill it with the data provided by the modules. In case there is no such data, you can still get some demo data with ${ROOT_MAGE_URL}/scm/demointernal


OSGI/FastCGI/SCGI/AJP integration
=====================================

It is now possible - as an option - to have a fully-featured web server serve our web pages. For this, follow the instructions at https://docs.djangoproject.com/en/1.5/howto/deployment/
