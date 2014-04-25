from .worker import (
    TransformError,
    TransformWorker,
)
from webob import (
    Request,
    Response,
)
from webob.compat import string_types
import pkg_resources
import shlex


truthy = frozenset(('t', 'true', 'y', 'yes', 'on', '1'))


def asbool(s):
    """ Return the boolean value ``True`` if the case-lowered value of string
    input ``s`` is any of ``t``, ``true``, ``y``, ``on``, or ``1``, otherwise
    return the boolean value ``False``.  If ``s`` is the value ``None``,
    return ``False``.  If ``s`` is already one of the boolean values ``True``
    or ``False``, return it."""
    if s is None:
        return False
    if isinstance(s, bool):
        return s
    s = str(s).strip()
    return s.lower() in truthy


def maybe_dotted(value):
    if not isinstance(value, string_types):
        return value
    return pkg_resources.EntryPoint.parse('x=%s' % value).load(False)


def transform_error(detail, comment):
    body = 'Transform failed.\n\n{detail}\n\n{comment}'.format(detail=detail, comment=comment)
    return Response(status="500 Internal Server Error", body=body)


class SubprocessMiddleware(object):
    should_transform = None

    def __init__(self, app, global_conf, should_transform=None, transform_error=transform_error, **settings):
        self.app = app
        self.global_conf = global_conf
        self.should_transform = maybe_dotted(should_transform)
        self.transform_error = maybe_dotted(transform_error)

        kw = settings.copy()
        for name in ['bufsize']:
            if name in settings and isinstance(settings[name], string_types):
                kw[name] = int(settings[name])
        for name in ['env', 'preexec_fn', 'startupinfo', 'creationflags']:
            if name in settings:
                kw[name] = maybe_dotted(settings[name])
        for name in ['reload_process', 'shell', 'universal_newlines', 'restore_signals', 'start_new_session']:
            if name in settings:
                kw[name] = asbool(settings[name])
        if 'args' in settings and not kw.get('shell'):
            if isinstance(settings['args'], string_types,):
                kw['args'] = shlex.split(settings['args'])

        self.transform = TransformWorker(**kw)

    def __call__(self, environ, start_response):
        request = Request(environ)
        response = request.get_response(self.app)

        if self.should_transform is None or self.should_transform(request, response):
            try:
                response = self.transform(response)
            except TransformError as e:
                response = self.transform_error(detail=e.detail, comment=e.comment)

        return response(environ, start_response)
