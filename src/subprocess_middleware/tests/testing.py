import os
import sys
from ..tween import SubprocessTween

subprocess_env = os.environ.copy()
subprocess_env['PYTHONPATH'] = os.pathsep.join(sys.path[1:])


def should_transform(request, response):
    return 'X-No-Transform' not in request.headers


def after_transform(request, response):
    response.headers['X-After-Transform'] = 'true'


def _reload_process(process):
    return False


# Wrapper so _reload_subprocess can be mocked
def reload_process(process):
    return _reload_process(process)


testing_tween = SubprocessTween(
    should_transform=should_transform,
    after_transform=after_transform,
    reload_process=reload_process,
    args=[sys.executable, '-m', 'subprocess_middleware.tests.testing_transform'],
    env=subprocess_env,
)


startup_error_tween = SubprocessTween(
    should_transform=should_transform,
    after_transform=after_transform,
    args=[sys.executable, '-m', 'subprocess_middleware.tests.testing_transform', '--error'],
    env=subprocess_env,
)
