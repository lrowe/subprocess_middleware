from webob import Response
from webob.compat import bytes_
import sys


def main():
    while 1:
        try:
            response = Response.from_file(sys.stdin)
        except ValueError:
            break  # assume EOF

        if 'X-Transform-Error' in response.headers:
            sys.stderr.write('Error output')
            break

        response.headers['X-Transformed'] = 'true'

        body = response.body  # Ensure content length header
        headers = bytes_(response.__str__(skip_body=True))
        sys.stdout.write(headers)
        sys.stdout.write(b'\r\n\r\n')
        sys.stdout.write(body)
        sys.stdout.flush()


if __name__ == '__main__':
    main()
