from webob import Response
from webob.compat import bytes_
import sys


def main():
    try:
        stdin = sys.stdin.buffer
        stdout = sys.stdout.buffer
    except AttributeError:  # Python 2
        stdin = sys.stdin
        stdout = sys.stdout

    while 1:
        try:
            response = Response.from_file(stdin)
        except ValueError:
            break  # assume EOF

        if 'X-Transform-Error' in response.headers:
            sys.stderr.write('Error output')
            break

        response.headers['X-Transformed'] = 'true'

        body = response.body  # Ensure content length header
        headers = bytes_(response.__str__(skip_body=True))
        stdout.write(headers)
        stdout.write(b'\r\n\r\n')
        stdout.write(body)
        stdout.flush()


if __name__ == '__main__':
    main()
