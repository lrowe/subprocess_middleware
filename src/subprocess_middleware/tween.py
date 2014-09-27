from .worker import TransformWorker
from pyramid.httpexceptions import HTTPServerError
from pyramid.response import Response


class TransformErrorResponse(HTTPServerError):
    explanation = 'Transform failed.'


class SubprocessTween(object):
    def __init__(self, should_transform=None, after_transform=None,
                 transform_error=TransformErrorResponse, reload_process=False,
                 Response=Response, **kw):
        self.should_transform = should_transform
        self.after_transform = after_transform
        self.transform_error = transform_error
        self.reload_process = reload_process
        self.Response = Response
        self.kw = kw

    def __call__(self, handler, registry):
        if registry.settings['pyramid.reload_templates']:
            self.reload_process = True
        transform = TransformWorker(
            Response=Response, reload_process=self.reload_process, **self.kw)
        should_transform = self.should_transform
        after_transform = self.after_transform
        transform_error = self.transform_error

        def subprocess_tween(request):
            response = handler(request)
            if should_transform and not should_transform(request, response):
                return response
            try:
                response = transform(response)
            except ValueError as e:
                response = transform_error(e.args[0])
            else:
                after_transform and after_transform(request, response)
            return response

        return subprocess_tween
