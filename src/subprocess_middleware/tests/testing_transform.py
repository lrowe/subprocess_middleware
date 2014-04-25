from webob import Response
from webob.compat import (
    PY3,
    bytes_,
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
        http_version = stdin.read(len(HTTP_VERSION))
        if not http_version:
            break  # EOF

        response = Response.from_file(stdin)

        if 'X-Transform-Error' in response.headers:
            sys.stderr.write('Error output')
            break

        response.headers['X-Transformed'] = 'true'

        body = response.body  # Ensure content length header
        headers = bytes_(response.__str__(skip_body=True))
        stdout.write(b'HTTP/1.1 ')
        stdout.write(headers)
        stdout.write(b'\r\n\r\n')
        stdout.write(body)
        stdout.flush()


if __name__ == '__main__':
    main()
