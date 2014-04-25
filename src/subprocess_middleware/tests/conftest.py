import pytest


def pytest_configure(config):
    import logging
    logging.basicConfig()


def make_config():
    from pyramid.config import Configurator
    from pyramid.httpexceptions import HTTPBadRequest
    from pyramid.response import Response

    def hello_world(request):
        return Response('Hello world!')

    def transform_error(request):
        response = Response('Hello world!')
        response.headers['X-Transform-Error'] = 'true'
        return response

    def bad_request(request):
        raise HTTPBadRequest()

    config = Configurator()

    config.add_route('root', '/')
    config.add_view(hello_world, route_name='root')

    config.add_route('transform_error', '/transform_error')
    config.add_view(transform_error, route_name='transform_error')

    config.add_route('bad_request', '/bad_request')
    config.add_view(bad_request, route_name='bad_request')

    return config


@pytest.fixture(scope='session', params=['tween', 'wsgi'])
def app(request):
    config = make_config()

    if request.param == 'tween':
        config.add_tween('subprocess_middleware.tests.testing.testing_tween')
        return config.make_wsgi_app()

    elif request.param == 'wsgi':
        import sys
        from ..wsgi import SubprocessMiddleware
        app = config.make_wsgi_app()
        return SubprocessMiddleware(
            app, {},
            should_transform='subprocess_middleware.tests.testing:should_transform',
            args='"{}" -m subprocess_middleware.tests.testing_transform'.format(sys.executable),
            env='subprocess_middleware.tests.testing:subprocess_env',
        )


@pytest.fixture(scope='session')
def testapp(app):
    from webtest import TestApp
    return TestApp(app)
