"""
WSGI config for MAGE project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

###############
## HACK - Django expects decoded data in PATH_INFO, but the Azure publication chain actually returns it still URL-encoded.
## See https://github.com/Microsoft/PTVS/issues/123 (rewrite issue)
import urllib
import django.core.handlers.wsgi
def get_path_info(environ):
    path_info = django.core.handlers.wsgi.get_bytes_from_wsgi(environ, 'PATH_INFO', '/')
    return urllib.unquote(path_info.decode(str('utf-8')))
django.core.handlers.wsgi.get_path_info = get_path_info
##
## END OF HACK
###############

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MAGE.settings")

application = get_wsgi_application()