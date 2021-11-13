from ref.models import Project

"""A very simple middleware which adds a 'project' argument to the view call if the argument 'project_id' was given. Factorizes stupid code, including global cache."""
class ProjectFromProjectIdMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not 'project' in view_kwargs and 'project_id' in view_kwargs and view_kwargs['project_id']:
            view_kwargs['project'] = Project.objects.get(pk = view_kwargs['project_id'])
        
        if 'project_id' in view_kwargs: del view_kwargs['project_id']
