# import asyncio

import muffin
import pytest

from muffin_cache import CacheHandler, cache_view


@pytest.fixture(scope='session')
def app(loop):
    return muffin.Application(
        'cache', loop=loop,

        PLUGINS=(
            'muffin_redis',
            'muffin_cache',
        ),
        REDIS_FAKE=True,
    )


def test_plugin_register(app):
    assert 'cache' in app.ps
    assert 'lifetime' in app.ps.cache.cfg


def test_should_cache_response(app, client):

    hit_view_count = 0

    @app.register('/cache')
    class View(CacheHandler):

        def get(self, request):
            nonlocal hit_view_count
            hit_view_count += 1
            return 'result'

    for _ in range(2):
        response = client.get('/cache?q=1')
        assert response.text == 'result'
        assert hit_view_count == 1

    response = client.get('/cache')
    assert response.text == 'result'
    assert hit_view_count == 2


def test_should_cache_response_in_any_querystring_parameters_order(
    app, client
):

    hit_view_count = 0

    @app.register('/cache-sorted-qs')
    class View(CacheHandler):

        def get(self, request):
            nonlocal hit_view_count
            hit_view_count += 1
            return 'result'

    response = client.get('/cache-sorted-qs?foo=1&bar=2')
    assert response.text == 'result'
    assert hit_view_count == 1

    response = client.get('/cache-sorted-qs?bar=2&foo=1')
    assert response.text == 'result'
    assert hit_view_count == 1


def test_should_cache_response_by_http_method(app, client):

    hit_view_count = 0

    @app.register('/cache-http-method')
    class View(CacheHandler):

        def get(self, request):
            nonlocal hit_view_count
            hit_view_count += 1
            return 'result'

        def options(self, request):
            nonlocal hit_view_count
            hit_view_count += 1
            return 'result options'

    for _ in range(2):
        response = client.get('/cache-http-method')
        assert response.text == 'result'
        assert hit_view_count == 1

    for _ in range(2):
        response = client.options('/cache-http-method')
        assert response.text == 'result options'
        assert hit_view_count == 2


def test_should_cache_json_response(app, client):

    hit_view_count = 0

    @app.register('/cache_json')
    class View(CacheHandler):

        def get(self, request):
            nonlocal hit_view_count
            hit_view_count += 1
            return {'result': 'json'}

    for _ in range(2):
        response = client.get('/cache_json')
        assert response.json == {'result': 'json'}
        assert response.content_type == 'application/json'
        assert hit_view_count == 1


def test_should_cache_function_view(app, client):

    hit_view_count = 0

    @app.register('/cache_func')
    @cache_view
    def cached(request):
        nonlocal hit_view_count
        hit_view_count += 1
        return 'result'

    for _ in range(2):
        response = client.get('/cache_func')
        assert response.text == 'result'
        assert hit_view_count == 1


def test_should_not_cache_unsafe_http_method(app, client):

    hit_view_count = 0

    @app.register('/dont-cache')
    class View(CacheHandler):

        def post(self, request):
            nonlocal hit_view_count
            hit_view_count += 1
            return 'result'

    for i in range(1, 3):
        response = client.post('/dont-cache')
        assert response.text == 'result'
        assert hit_view_count == i


def test_should_dont_install_cache_plugin_without_redis(loop):
    app = muffin.Application(
        'cache', loop=loop,

        PLUGINS=('muffin_cache',)
    )
    assert 'cache' not in app.ps
