from .worker import (
    TransformError,
    TransformWorker,
)
from pyramid.httpexceptions import HTTPInternalServerError
from pyramid.response import Response


class TransformErrorResponse(HTTPInternalServerError):
    explanation = 'Transform failed.'


class SubprocessTween(object):
    def __init__(self, should_transform=None, after_transform=None,
                 transform_error=TransformErrorResponse, Response=Response, **kw):
        self.should_transform = should_transform
        self.after_transform = after_transform
        self.transform = TransformWorker(Response=Response, **kw)
        self.transform_error = transform_error

    def __call__(self, handler, registry):
        transform = self.transform
        should_transform = self.should_transform
        after_transform = self.after_transform
        transform_error = self.transform_error
        transform.reload_process = registry.settings['pyramid.reload_templates']

        def subprocess_tween(request):
            response = handler(request)
            if should_transform and not should_transform(request, response):
                return response
            try:
                response = transform(response)
            except TransformError as e:
                response = transform_error(detail=e.detail, comment=e.comment)
            else:
                after_transform and after_transform(request, response)
            return response

        return subprocess_tween
