# THIS FILE SHOULD NEVER BE EDITED.
# Parameters should go inside a file named local_settings.py in the same directory.
# A sample file named local_settings.sample.py is provided in this directory.

import os

# Fixes our usage of os.getenv() method with docker
# Empty variable should use default value
def getenv(environment_variable, default=''):
    get_env = os.getenv(environment_variable, default)
    return get_env if get_env != '' else default

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DEBUG = getenv('DJANGO_DEBUG', False)
TEMPLATE_DEBUG = DEBUG

ADMINS = ()
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': getenv('DATABASE_ENGINE', 'django.db.backends.sqlite3'),  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': getenv('DATABASE_NAME', os.path.join(BASE_DIR, 'tmp/db.sqlite')),  # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': getenv('DATABASE_USER', ''),
        'PASSWORD': getenv('DATABASE_PASSWORD', ''),
        'HOST': getenv('DATABASE_HOST', ''),  # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': getenv('DATABASE_PORT', ''),  # Set to empty string for default.
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = getenv('DJANGO_ALLOWED_HOSTS', '*').split(',')

INTERNAL_IPS = [ getenv('DJANGO_INTERNAL_IPS', '127.0.0.1'), ]

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, 'tmp/media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/magefiles/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'tmp/static')

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Make this unique, and don't share it with anybody. (overloaded in local settings)
SECRET_KEY = getenv('DJANGO_SECRET_KEY', 'your_own_here')

LOCAL_MIDDLEWARE = []
MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'ref.middleware.DisableCSRF',
    'MAGE.project_middleware.ProjectFromProjectIdMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'mozilla_django_oidc.middleware.SessionRefresh',
]

ROOT_URLCONF = 'MAGE.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'MAGE.wsgi.application'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'MAGE/templates'),
        ],
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
                'MAGE.project_middleware.add_project_to_template_context'
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ]
        },
    },
]


# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

LOGIN_URL = 'login'  # named URL
LOGIN_REDIRECT_URL = 'welcome'
# Only used when force logging middleware is enabled (off by default):
FORCE_LOGIN_EXCEPTIONS = ('login', 'logout', 'script_logout', 'script_login', 'script_login_post', 'force_login', 'openid', )

CRISPY_TEMPLATE_PACK = 'bootstrap3'
DEFAULT_FILE_STORAGE = getenv('DEFAULT_FILE_STORAGE', 'django.core.files.storage.FileSystemStorage')
AZURE_ACCOUNT_NAME = getenv('AZURE_ACCOUNT_NAME')
AZURE_ACCOUNT_KEY = getenv('AZURE_ACCOUNT_KEY')
AZURE_CONTAINER = getenv('AZURE_CONTAINER', 'mage-media')

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'houba-hop'
    }
}

DEFAULT_PROJECT_ID = None
LOCAL_APPS = []
try:
    from MAGE.local_settings import *
except ImportError as e:
    pass

INSTALLED_APPS = [
    'django.contrib.auth',
    'mozilla_django_oidc', # Load after auth
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.staticfiles',

    'crispy_forms',

    'ref',  ## Keep REF first after django internals
    'scm',  ## Keep SCM second
]

INSTALLED_APPS += LOCAL_APPS
MIDDLEWARE += LOCAL_MIDDLEWARE

AUTHENTICATION_BACKENDS = [
    'mozilla_django_oidc.auth.OIDCAuthenticationBackend',
]

OIDC_RP_SIGN_ALGO = 'RS256'
OIDC_OP_JWKS_ENDPOINT = "https://login.microsoftonline.com/f229acc0-5400-42d3-9d32-ae7c2c2c43ce/discovery/v2.0/keys"

# From Open id provider (Azure Ad)
OIDC_RP_CLIENT_ID = '71c4b90c-ebff-4b05-a4a9-700ba0315e86'
OIDC_RP_CLIENT_SECRET = '2vF8Q~7NJMfTS59UdToIXMz6ACtOSRLnU3uSIc94'

# Specific to your OpenID Connect provider
OIDC_OP_AUTHORIZATION_ENDPOINT = "https://login.microsoftonline.com/f229acc0-5400-42d3-9d32-ae7c2c2c43ce/oauth2/v2.0/authorize"
OIDC_OP_TOKEN_ENDPOINT = "https://login.microsoftonline.com/f229acc0-5400-42d3-9d32-ae7c2c2c43ce/oauth2/v2.0/token"
OIDC_OP_USER_ENDPOINT = "https://graph.microsoft.com/oidc/userinfo"
