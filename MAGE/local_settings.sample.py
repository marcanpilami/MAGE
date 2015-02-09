# coding: utf-8

DEBUG = False

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

SECRET_KEY='a_random_string'

# Set your database connection data. Default is a local sqlite3 file in ./tmp/db.sqlite
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

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Paris'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'fr-fr'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
# STATIC_ROOT = './tmp/static'

# URL prefix for static files. Typically, you should only need to change this if you host static files
# in another site than the Django application.
# Example: "http://example.com/static/", "http://static.example.com/"
# STATIC_URL = '/static/'

# Absolute filesystem path to the directory that will hold the uploaded delivery files.
# Only use if file upload is enabled in your environment.
# Example: "/var/www/example.com/media/"
# MEDIA_ROOT = './tmp/files'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash. Remarks for STATIC_URL apply.
# Only use if file upload is enabled in your environment.
# Examples: "http://example.com/media/", "http://media.example.com/"
# MEDIA_URL = '/magefiles/'

# Add your applications here (comma separated list)
# Example: LOCAL_APPS = ('debug_toolbar.apps.DebugToolbarConfig', 'django.contrib.staticfiles')
LOCAL_APPS=()

# Cache setings. Default is an in process memory cache.
#CACHES = {
#    'default': {
#        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
#        'LOCATION': 'houba-hop'
#    }
#}
