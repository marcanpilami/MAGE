# coding: utf-8

# This is the main configuration file. Please copy it as 'MAGE/local_settings.py' and set
# the desired values.
# Please note that MAGE will run with default values if this file does not exist (everything
# here is optional)
#
# A typical installation will override:
#      DATABASES
#      SECRET_KEY
#      ALLOWED_HOSTS
#      MEDIA_ROOT
#      MEDIA_URL
#      STATIC_ROOT
#      STATIC_URL


###############################################################################
## Database
###############################################################################

## Default database is a sqlite file inside ./tmp/db.sqlite

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',  # You may replace 'sqlite3' with 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
#         'NAME': '/var/tmp/db.sqlite',  # Or database name if not using sqlite3 (absolute path if sqlite3)
#         # The following settings are not used with sqlite3:
#         'USER': '',
#         'PASSWORD': '',
#         'HOST': '',  # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
#         'PORT': '',  # Set to empty string for default.
#     }
# }


###############################################################################
## URLs and network settings
###############################################################################

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.8/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['*',]

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
# STATIC_ROOT = './tmp/static'

# URL prefix for static files. Typically, you should only need to change this if you host static files
# in another site than the Django application.
# Example: "http://example.com/static/", "http://static.example.com/"
# STATIC_URL = '/static/'

# Used for CSRF protection. Please set your own.
SECRET_KEY='a_random_string'


###############################################################################
## Delivery file handling
###############################################################################

# Set here the storage provider used to store delivery file. MAGE is provided with an Azure
# blob storage provider.
# Default is on the local file system inside directory MEDIA_ROOT
# DEFAULT_FILE_STORAGE = 'MAGE.storage.AzureStorage'

# Absolute filesystem path to the directory that will hold the uploaded delivery files.
# Only use if file upload is enabled in your environment. Ignored if you've set DEFAULT_FILE_STORAGE.
# Example: "/var/www/example.com/media/"
# MEDIA_ROOT = './tmp/files'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash. Remarks for STATIC_URL apply.
# Only use if file upload is enabled in your environment.
# Examples: "http://example.com/media/", "http://media.example.com/"
# MEDIA_URL = '/magefiles/'

# If using Azure blob storage, this must be the 'accountname' as in accountname.blob.core.windows.net
# AZURE_ACCOUNT_NAME = 'accountname'

# If using Azure blob storage, this must be one of the access keys
# AZURE_ACCOUNT_KEY = 'Ldkjf886+skdchnv=='

# If using Azure blob storage, this is the container name. Default is 'mage-media'
# AZURE_CONTAINER = 'containername'


###############################################################################
## Default language
###############################################################################

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Paris'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'fr-fr'


###############################################################################
## Additional modules
###############################################################################

# Add your applications here (comma separated list)
# Example: LOCAL_APPS = ['debug_toolbar.apps.DebugToolbarConfig', ]
LOCAL_APPS=[]

# Add your own middleware here.
    # Example: LOCAL_MIDDLEWARE = ['MAGE.profiler.ProfileMiddleware', 'debug_toolbar.middleware.DebugToolbarMiddleware',]
LOCAL_MIDDLEWARE = []


###############################################################################
## Misc.
###############################################################################

# Cache settings. Default is an in process memory cache.
#CACHES = {
#    'default': {
#        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
#        'LOCATION': 'houba-hop'
#    }
#}

# Uncomment to force authentication on all pages (default is public read access)
# LOCAL_MIDDLEWARE_CLASSES = ['MAGE.force_login_middleware.ForceLoginMiddleware',]

# If True, detailed exception will be displayed on errors. Performance and security impact.
DEBUG = False

# The list of clients considered as local. Only these can see the debug toolbar if enabled.
#INTERNAL_IPS = [ '127.0.0.1', ]

# The list of admins that receive a mail when a server error occurs
ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

