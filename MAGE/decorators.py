from django.http.response import HttpResponse
from ref.models import ProjectUser


def project_permission_required(function):
    def wrap_check_user_project(request, project, *args, **kwargs):
        try:
            ProjectUser.objects.get(user__id=request.user.id, projects__name=project)
        except ProjectUser.DoesNotExist:
            return HttpResponse("Permission denied: not allowed to access this project")
        return function(request, project, *args, **kwargs)
    return wrap_check_user_project
