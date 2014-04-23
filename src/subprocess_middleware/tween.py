from .worker import (
    TransformError,
    TransformWorker,
)
from pyramid.httpexceptions import HTTPInternalServerError
from pyramid.response import Response


class TransformErrorResponse(HTTPInternalServerError):
    explanation = 'Transform failed.'


class SubprocessTween(object):
    def __init__(self, should_transform=None, transform_error=TransformErrorResponse, Response=Response, **kw):
        self.should_transform = should_transform
        self.transform = TransformWorker(Response=Response, **kw)
        self.transform_error = transform_error

    def __call__(self, handler, registry):
        transform = self.transform
        should_transform = self.should_transform
        transform_error = self.transform_error

        def subprocess_tween(request):
            response = handler(request)
            if not (should_transform is None or should_transform(request, response)):
                return response
            try:
                return transform(response)
            except TransformError as e:
                # This tween 
                return transform_error(detail=e.detail, comment=e.comment)

        return subprocess_tween
