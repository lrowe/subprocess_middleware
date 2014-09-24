from subprocess_middleware.response import (
    response_from_file,
    response_to_file,
)
from webob import Response
from webob.compat import (
    PY3,
)
import sys

HTTP_VERSION = 'HTTP/1.1 '


def main():
    if PY3:
        stdin = sys.stdin.buffer
        stdout = sys.stdout.buffer
    else:
        stdin = sys.stdin
        stdout = sys.stdout

    while 1:
        response = response_from_file(Response, stdin)
        if response is None:
            break  # EOF

        if 'X-Transform-Error' in response.headers:
            sys.stderr.write('Error output')
            break

        response.headers['X-Transformed'] = 'true'
        response_to_file(response, stdout)
        stdout.flush()

        if response.headers.get('Connection') == 'close':
            break


if __name__ == '__main__':
    main()
