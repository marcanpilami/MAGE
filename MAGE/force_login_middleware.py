from django.conf import settings
from django.contrib.auth.decorators import login_required

""" Adapted from http://stackoverflow.com/questions/2164069/best-way-to-make-djangos-login-required-the-default """

class ForceLoginMiddleware(object):
    """
    Middleware component that forces authentication on all views.
    It actually wraps the login_required decorator around the views.
    To use, add the class to MIDDLEWARE_CLASSES and optionally define
    FORCE_LOGIN_EXCEPTIONS containing the named URLs that are to be
    exempted from forces authentication in your settings.py.
    For example:
    ------
    FORCE_LOGIN_EXCEPTIONS = ('login', 'script_login')
    ------
    """
    def __init__(self):
        self.exceptions = ('login',)
        if hasattr(settings, 'FORCE_LOGIN_EXCEPTIONS'):
            self.exceptions = settings.FORCE_LOGIN_EXCEPTIONS

    def process_view(self, request, view_func, view_args, view_kwargs):
        # No need to process URLs if user already logged in
        if request.user.is_authenticated:
            return None

        # An exception match should immediately return None
        if request.resolver_match.url_name in self.exceptions:
            return None

        # Otherwise return the view wrapped inside the standard decorator
        return login_required(view_func)(request, *view_args, **view_kwargs)
