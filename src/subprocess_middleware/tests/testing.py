import os
import sys
from ..tween import SubprocessTween

subprocess_env = os.environ.copy()
subprocess_env['PYTHONPATH'] = os.pathsep.join(sys.path[1:])


def should_transform(request, response):
    return 'X-No-Transform' not in request.headers


testing_tween = SubprocessTween(
    should_transform=should_transform,
    args=[sys.executable, '-m', 'subprocess_middleware.tests.testing_transform'],
    env=subprocess_env,
)
