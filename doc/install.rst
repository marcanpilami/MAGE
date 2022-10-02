Installation with Git
######################

Prerequisites
*************

* OS: every OS with a supported Python 3.10 distribution. (Windows, most Linux distributions, Solaris, ...)
* The latest Python 3.10.x (not Python 2.x)
* A git client (on Windows, the recommended distribution is GitHub's http://msysgit.github.io/)
* Optionally, a database (Oracle >= 10g, PostgresQL, mysql). Default is sqlite 3 - it is bundled with Python, so nothing special is required. In other databases, you will
  need an account with the permission to create tables, sequences and indexes (or their equivalent in your database).


MAGE itself
***********

Checkout
========

Choose a directory in which to install MAGE. This directory will not be accessible to users. It will be referred to as ${MAGE_INSTALL_ROOT} in this document.::

	git clone https://github.com/marcanpilami/MAGE.git
    
Libraries
=========

These are installed with PIP::

    ## Linux (sh, bash & similar) or Windows (pwsh)
    cd $MAGE_INSTALL_ROOT
    pip install -r requirements.txt --upgrade
    
Settings
========

Copy the file ${MAGE_INSTALL_ROOT}/MAGE/local_settings.sample.py to ${MAGE_INSTALL_ROOT}/MAGE/local_settings.py

Edit the file. Every setting is explained in the file. Of particular importance are:

* Database configuration.
* Allowed hosts (unless running in debug mode)
* Static root - this directory will be directly accessible to users

Sync
====

In the ${MAGE_INSTALL_ROOT} directory, create the database objects by running::

    python manage.py migrate
    python manage.py collectstatic
    python manage.py createsuperuser
    python manage.py synccheckers
	
You will be asked to create a root account. Accept and do not forget the password you specify.

Test
====

Run::

	python manage.py runserver 0.0.0.0:8000

This will launch a small web server listening on an address printed on the standard output. With a browser, try this address. You should then access MAGE's homepage.

Initial data
============

If you just want to play with demo data, run the following commands::

    python manage.py shell
    from scm.demo_items import create_test_is
    create_test_is()
    exit
    
Otherwise, the database is yours to populate through the GUI and scripts. For writing bootstrap script, inspiration should be taken from the one used above.


WSGI/OSGI/FastCGI/SCGI/AJP integration
======================================

For deploying MAGE inside a full-fledged web server, please follow the instructions at https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/.

Please note that all new deployments should use WSGI and NOT FastCGI which is deprecated in the Apache world.
