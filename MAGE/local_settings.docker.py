# coding: utf-8
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MEDIA_ROOT = os.path.join(BASE_DIR, 'deployment/media')
STATIC_ROOT = os.path.join(BASE_DIR, 'deployment/static')

USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'ref.middleware.DisableCSRF',
    'MAGE.project_middleware.ProjectFromProjectIdMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'MAGE.force_login_middleware.ForceLoginMiddleware',
]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

TIME_ZONE = 'Europe/Paris'
LANGUAGE_CODE = 'fr-fr'

DEFAULT_PROJECT_ID=os.getenv('MAGE_DEFAULT_PROJECT', None)
