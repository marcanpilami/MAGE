# coding: utf-8

'''
    Python MAGE client lib tests
    @license: Apache License, Version 2.0
    @copyright: 2015 Sebastien Renard
    @author: Sebastien Renard
'''

from django.test import LiveServerTestCase
from django.contrib.auth.models import User

import requests

from ref.demo_items import utility_create_logical, utility_create_meta, utility_create_test_instances
from ref.models.description import clear_classes_cache

from .libmage6 import MageClient, LibMageException

USERNAME = "root"
PASSWORD = "secret"


def create_admin_login(url):
    """Create superuser in test database with default credentials"""
    m = MageClient(url, USERNAME, PASSWORD)
    root = User.objects.create_user(username = m.username, email = None, password = m.password)
    root.is_superuser = True
    root.save()


class TestLoginLogout(LiveServerTestCase):
    def setUp(self):
        create_admin_login(self.live_server_url)


    def test_invalid_mage_client(self):
        params = (("http://localhost", None, "secret"),
                  ("http://localhost", "", "secret"),
                  ("", "", ""),
                  (None, None, None),)
        for param in params:
            self.assertRaises(LibMageException, MageClient, *param)



    def test_login(self):
        m = MageClient(self.live_server_url, USERNAME, PASSWORD)
        m.login()
        self.assertIsInstance(m._session, requests.Session)
        m.logout()


    def test_bad_login(self):
        m = MageClient(self.live_server_url, USERNAME, PASSWORD)
        url = m.base_url

        m.base_url = "localhost:8080"  # missing sheme
        self.assertRaises(LibMageException, m.login)

        m.base_url = "http://unknown-host"  # cannot resolve
        self.assertRaises(LibMageException, m.login)

        m.base_url = url  # Restore good url
        m.password = "badpassword"
        self.assertRaises(LibMageException, m.login)  # bad password

        m.username = "clown"
        self.assertRaises(LibMageException, m.login)  # bad username


    def test_login_twice(self):
        m = MageClient(self.live_server_url, USERNAME, PASSWORD)
        m.login()
        m.login()
        self.assertIsInstance(m._session, requests.Session)
        m.logout()


    def test_logout(self):
        # test logout with login first
        # test that after logout _session is None
        # test that after logout we cannot query anymore
        pass


    def test_prefix(self):
        # Add tests with mage running with prefix
        # we should ensure that base_url ends with / for proper urljoin
        pass


class TestQuerying(LiveServerTestCase):
    def setUp(self):
        utility_create_meta()
        utility_create_logical()
        utility_create_test_instances()
        clear_classes_cache()
        create_admin_login(self.live_server_url)


    def test_multiple_result_query(self):
        m = MageClient(self.live_server_url, USERNAME, PASSWORD)
        m.login()
        query = "SELECT ENVIRONMENT 'DEV1' 'oracleschema' INSTANCES"# WITH COMPUTATIONS"
        r = m.run_mql_query(query)
        self.assertEqual(len(r), 3)


    def test_single_result_query(self):
        m = MageClient(self.live_server_url, USERNAME, PASSWORD)
        m.login()
        m_query = "SELECT ENVIRONMENT 'DEV1' 'oracleschema' INSTANCES"
        s_query = "SELECT ENVIRONMENT 'DEV1' 'oracleschema' INSTANCES where name='schema1'"
        self.assertRaises(LibMageException, m.run_mql_query, m_query, unique=True)
        r = m.run_mql_query(s_query, unique=True)
        self.assertDictContainsSubset( {u'name': u'schema1'}, r)
        #BUG: fail with django live test server, but works when runs as the only test or against previously launched mage. Bug in MAGE server or django ?


    def test_query_without_login(self):
        m = MageClient(self.live_server_url, USERNAME, PASSWORD)
        self.assertRaises(LibMageException, m.run_mql_query, "query")