# coding: utf-8

'''
    Python MAGE client lib for python scripts
    @license: Apache License, Version 2.0
    @copyright: 2015 Sebastien Renard
    @author: Sebastien Renard
'''


from urlparse import urljoin
import logging
from logging.handlers import RotatingFileHandler

import requests


class MageClient(object):
    """Mage client that connect to Mage server though HTTP(S) REST web services"""

    def __init__(self, base_url="http://127.0.0.1:8081", username= "root", password = "secret", setup_log=True):
        self.base_url = base_url
        self.username = username
        self.password = password
        self._session = None

        self.logger = logging.getLogger("libmage")
        if setup_log and len(self.logger.handlers) == 0:
            self.logger.setLevel(logging.DEBUG)
            formatter = logging.Formatter("%(asctime)s :: %(levelname)s :: %(message)s")
            file_handler = RotatingFileHandler("libmage.log", "a", maxBytes=10*1024*1024, backupCount=10)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            self.logger.info("lib mage own logger has been initialised")



    def login(self):
        """Log to mage and return an http session with proper credential"""
        login = urljoin(self.base_url, "/accounts/scriptlogin")

        # Sanity checks
        if not login.startswith("http"):
            msg = "Bad MAGE_BASE_URL. It should starts with http://... or (bette) https://..."
            self.logger.fatal(msg)
            raise LibMageException(msg)
        if not login.startswith("https://"):
            self.logger.warn("Using clear http to login. You should use ssl (https) to protect your passsword")

        if self._session is not None:
            self.logger.warn("A session was already defined for this client. You should logout before login again or not login twice")

        self._session = requests.Session()
        self.logger.info("Loggin to MAGE with url %s " % login)

        try:
            request = self._session.post(login, data = { "username": self.username, "password": self.password })
        except requests.ConnectionError, e:
            self._session = None
            msg = "Failed to connect to MAGE: %s" % e
            self.logger.fatal(msg)
            self.logger.exception(e)
            raise LibMageException(msg)

        if request.status_code != 200:
            self._session = None
            msg = "Cannot log in Mage. Response was %s: %s" % (request.status_code, request.reason)
            self.logger.fatal(msg)
            raise LibMageException(msg)


    def logout(self):
        """Be a good citizen, close session"""
        #TODO: call mage logout URL
        pass


    def run_query(self, query, uniq=False):
        """Execute a query on mage. Return results as json like dict
        @:param uniq: if True, assume that query return only one. It raises if stricly less or more that 1 response it returned. Default is False
        @:return list of responses. If uniq=True, returns only one response object instead of a list of response.. """
        base_query = "/ref/mql/json/"
        url = urljoin(self.base_url, base_query)
        url = urljoin(url, query)
        if self._session is None:
            msg = "You must login before trying to run a query"
            self.logger.fatal(msg)
            raise LibMageException(msg)
        self.logger.debug("Running mage query: %s" % url)
        request = self._session.get(url)
        if request.status_code != 200:
            msg = "Cannot query Mage. Response was %s: %s" % (request.status_code, request.reason)
            self.logger.critical(msg)
            raise LibMageException(msg)
        self.logger.debug("Query answer: %s" % request.json())
        return request.json()


    def mage_get_delivery_id(self):
        raise NotImplementedError()


    def mage_get_delivery_content(self):
        raise NotImplementedError()


    def mage_get_installable_item_detail(self):
        raise NotImplementedError()


    def mage_get_install_methods(self):
        raise NotImplementedError()


    def mage_get_compatible_installable_items(self):
        raise NotImplementedError()


    def mage_test_ii_dependencies(self):
        raise NotImplementedError()


    def mage_register_install(self):
        raise NotImplementedError()


    def mage_register_backup_ci(self):
        raise NotImplementedError()


    def mage_archive_set(self):
        raise NotImplementedError()


    def mage_latest_backup_age(self):
        raise NotImplementedError()


class LibMageException(Exception):
    """lib mage client exception root class"""
    pass
