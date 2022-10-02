from textwrap import wrap
from django.http.response import HttpResponse
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import resolve_url
from django.conf import settings

anonymous_mode = not 'MAGE.force_login_middleware.ForceLoginMiddleware' in settings.MIDDLEWARE


def permission_required_project_aware(perm, login_url=None, raise_exception=False, no_check_in_anonymous_mode=False):
    """A decorator that has the same signature as permission_required and which uses the project context inside the query to use instance-level permissions instead of model-level."""
    def wrap_view(view_function):
        def wrapped_view(request, *args, **kwargs):
            if not hasattr(request, "project") or not request.project:
                # cannot have a view protected on project level without a project in the query.
                raise PermissionDenied

            if isinstance(perm, str):
                perms = (perm,)
            else:
                perms = perm

            newperms = []
            for permission in perms:
                newperms.append(f'{permission}_{request.project.id}')

            # Actually check permissions
            if (no_check_in_anonymous_mode and anonymous_mode) or request.user.has_perms(newperms):
                return view_function(request, *args, **kwargs)
            elif raise_exception:
                raise PermissionDenied
            else:
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(request.build_absolute_uri(), login_url=resolve_url(login_url or settings.LOGIN_URL))

        return wrapped_view

    return wrap_view


def login_required_unless_anonymous_mode(function=None, login_url=None):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    def wrapped_view(request, *args, **kwargs):
        if (anonymous_mode or request.user.is_authenticated):
            return function(request, *args, **kwargs)

        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(request.build_absolute_uri(), login_url=resolve_url(login_url or settings.LOGIN_URL))
    return wrapped_view
