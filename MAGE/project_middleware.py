from ref.models import Project


class ProjectFromProjectIdMiddleware:
    """A very simple middleware which adds a 'project' argument to the view call and template context if the argument 'project_id' was given. Factorizes stupid code, including global cache."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not 'project' in view_kwargs and 'project_id' in view_kwargs and view_kwargs['project_id']:
            request.project = Project.objects.get(pk = view_kwargs['project_id'])

        if 'project_id' in view_kwargs:
            del view_kwargs['project_id']


def add_project_to_template_context(request):
    """ Template context processor. Uses the project set by the middleware to inject it in into the template context. """
    if hasattr(request, 'project'):
        return {"project": request.project}
    else:
        return {}
