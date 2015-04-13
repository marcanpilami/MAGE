'''
    Azure storage backend. This is based on the backend provided in django-storages
    See https://django-storages.readthedocs.org/en/latest/
'''

import os.path

from django.core.files.storage import Storage
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from django.utils.deconstruct import deconstructible
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile

try:
    from azure import WindowsAzureMissingResourceError
    from azure.storage import AccessPolicy
    from azure.storage.blobservice import BlobService
    from azure.storage.sharedaccesssignature import SharedAccessPolicy, SharedAccessSignature
except ImportError:
    raise ImproperlyConfigured("Could not load Azure bindings. See https://github.com/WindowsAzure/azure-sdk-for-python")

def clean_name(name):
    return os.path.normpath(name).replace("\\", "/")

@deconstructible
class AzureStorage(Storage):
    account_name = settings.AZURE_ACCOUNT_NAME
    account_key = settings.AZURE_ACCOUNT_KEY
    azure_container = settings.AZURE_CONTAINER

    def __init__(self, *args, **kwargs):
        super(AzureStorage, self).__init__(*args, **kwargs)
        self._connection = None

    @property
    def connection(self):
        if self._connection is None:
            # Create connection
            self._connection = BlobService(self.account_name, self.account_key)
            
            # Create container if needed
            containers = [c for c in self._connection.list_containers(prefix=self.azure_container) if c.name == self.azure_container ]
            if len(containers) == 0:
                self._connection.create_container(self.azure_container, {'origin': 'created by Django web app'}, fail_on_exist=True)

        return self._connection

    def _open(self, name, mode="rb"):
        stream = SimpleUploadedFile(name, None)
        self.connection.get_blob_to_file(self.azure_container, name, stream)
        stream.seek(0)
        return stream

    def exists(self, name):
        try:
            self.connection.get_blob_properties(self.azure_container, name)
        except WindowsAzureMissingResourceError:
            return False
        else:
            return True

    def delete(self, name):
        self.connection.delete_blob(self.azure_container, name)

    def size(self, name):
        properties = self.connection.get_blob_properties(self.azure_container, name)
        return properties["content-length"]

    def _save(self, name, content):
        self.connection.put_block_blob_from_file(self.azure_container, name, content)
        return name

    def url(self, name):
        ap = AccessPolicy(expiry=(timezone.datetime.utcnow() + timezone.timedelta(seconds=600)).strftime('%Y-%m-%dT%H:%M:%SZ'), \
                          start=(timezone.datetime.utcnow() + timezone.timedelta(seconds=-600)).strftime('%Y-%m-%dT%H:%M:%SZ'), \
                          permission='r')
        sap = SharedAccessPolicy(ap)
        sas = SharedAccessSignature(self.account_name, self.account_key)
        url = sas.generate_signed_query_string(path=self.azure_container + '/' + name, resource_type='b', shared_access_policy=sap)
        
        return self.connection.make_blob_url(self.azure_container, name) + "?" + sas._convert_query_string(url)
