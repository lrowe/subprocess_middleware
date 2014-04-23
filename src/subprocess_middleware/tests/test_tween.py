import pytest


@pytest.fixture
def app():
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

    config.add_tween('subprocess_middleware.tests.testing_tween.testing_tween')
    return config.make_wsgi_app()


@pytest.fixture
def testapp(app):
    from webtest import TestApp
    return TestApp(app)


def test_tween(testapp):
    res = testapp.get('/')
    assert 'X-Transformed' in res.headers
    res = testapp.get('/')
    assert 'X-Transformed' in res.headers


def test_tween_should_transform(testapp):
    res = testapp.get('/', headers={'X-No-Transform': 'true'})
    assert 'X-Transformed' not in res.headers


def test_tween_transform_error(testapp):
    res = testapp.get('/transform_error', status=500)
    assert 'X-Transformed' not in res.headers


def test_tween_bad_request(testapp):
    res = testapp.get('/bad_request', status=400)
    assert 'X-Transformed' in res.headers
