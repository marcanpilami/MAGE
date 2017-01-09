# THIS FILE SHOULD NEVER BE EDITED.
# Parameters should go inside a file named local_settings.py in the same directory.
# A sample file named local_settings.sample.py is provided in this directory.

import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DEBUG = (os.getenv("DEBUG") == "True")
TEMPLATE_DEBUG = DEBUG

ADMINS = ()
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': os.getenv("DB_ENGINE"),
        'NAME': os.getenv("DB_NAME"),
        'USER': os.getenv("DB_USER"),
        'PASSWORD': os.getenv("DB_PASSWORD"),
        'HOST': os.getenv("DB_HOST"),
        'PORT': '',  # Set to empty string for default.
    }
}

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = [os.getenv('WEBSITE_HOSTNAME'), ]

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
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/magefiles/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

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
SECRET_KEY = 'your_own_here'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

LOCAL_MIDDLEWARE_CLASSES = ()
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'ref.middleware.DisableCSRF',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'MAGE.force_login_middleware.ForceLoginMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'MAGE.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'MAGE.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(BASE_DIR, 'MAGE/templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.template.context_processors.debug',
    'django.template.context_processors.i18n',
    'django.template.context_processors.media',
    'django.template.context_processors.static',
    'django.template.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    "django.core.context_processors.request",
)


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

LOGIN_URL = 'openid'  # named URL
LOGIN_REDIRECT_URL = 'welcome'
# Only used when force logging middleware is enabled (off by default):
FORCE_LOGIN_EXCEPTIONS = ('login', 'logout', 'script_logout', 'script_login', 'script_login_post', 'force_login',
                          'openid', 'openid_with_op_name', 'openid_login_cb', 'openid_logout_cb' )

CRISPY_TEMPLATE_PACK = 'bootstrap3'
DEFAULT_FILE_STORAGE = os.getenv('DEFAULT_FILE_STORAGE', 'django.core.files.storage.FileSystemStorage')
AZURE_ACCOUNT_NAME = os.getenv('AZURE_ACCOUNT_NAME')
AZURE_ACCOUNT_KEY = os.getenv('AZURE_ACCOUNT_KEY')
AZURE_CONTAINER = os.getenv('AZURE_CONTAINER', 'mage-media')

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'houba-hop'
    }
}

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'djangooidc.backends.OpenIdConnectBackend',
)

##################################
# OIDC

OIDC_LOGIN_TEMPLATE = "fed_login.html"

OIDC_ALLOW_DYNAMIC_OP = False

OIDC_CALLBACK_URL_START = "%s://%s" %(os.getenv('WEBSITE_PROTOCOL', 'https'), os.getenv('WEBSITE_HOSTNAME', 'localhost'))

OIDC_DYNAMIC_CLIENT_REGISTRATION_DATA = {
    "application_type": "web",
    "contacts": [a[1] for a in ADMINS],
    "redirect_uris": ["%s/openid/callback/login/" %OIDC_CALLBACK_URL_START, ],
    "post_logout_redirect_uris": ["%s/openid/callback/logout/" %OIDC_CALLBACK_URL_START, ]
}

OIDC_DEFAULT_BEHAVIOUR = {
    "response_type": "code",
    "scope": ["openid", "profile", "email", "address", "phone"],
}

OIDC_PROVIDERS = {
    "Azure Active Directory": {
        "srv_discovery_url": "https://sts.windows.net/%s/" % os.getenv('AZURE_AD_DIRECTORY_GUID'),
        "behaviour": OIDC_DEFAULT_BEHAVIOUR,
        "client_registration": {
            "client_id": os.getenv('AZURE_AD_CLIENT_ID'),
            "client_secret": os.getenv('AZURE_AD_CLIENT_SECRET'),
            "redirect_uris": ["%s/openid/callback/login/" %OIDC_CALLBACK_URL_START, ],
            "post_logout_redirect_uris": ["%s/openid/callback/logout/" %OIDC_CALLBACK_URL_START, ],
            "token_endpoint_auth_method": "client_secret_post",
        }
    },
}

#
##################################

LOCAL_APPS = ()
try:
    from MAGE.local_settings import *
except ImportError, e:
    pass

INSTALLED_APPS = (
    'django.contrib.auth',
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
)

INSTALLED_APPS += LOCAL_APPS
MIDDLEWARE_CLASSES += LOCAL_MIDDLEWARE_CLASSES
