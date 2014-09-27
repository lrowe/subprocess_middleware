import os
import sys
from ..tween import SubprocessTween

subprocess_env = os.environ.copy()
subprocess_env['PYTHONPATH'] = os.pathsep.join(sys.path[1:])


def should_transform(request, response):
    return 'X-No-Transform' not in request.headers


def after_transform(request, response):
    response.headers['X-After-Transform'] = 'true'


testing_tween = SubprocessTween(
    should_transform=should_transform,
    after_transform=after_transform,
    args=[sys.executable, '-m', 'subprocess_middleware.tests.testing_transform'],
    env=subprocess_env,
)


startup_error_tween = SubprocessTween(
    should_transform=should_transform,
    after_transform=after_transform,
    args=[sys.executable, '-m', 'subprocess_middleware.tests.testing_transform', '--error'],
    env=subprocess_env,
)
