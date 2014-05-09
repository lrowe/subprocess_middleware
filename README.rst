=====================
Subprocess Middleware
=====================

.. image:: https://travis-ci.org/lrowe/subprocess_middleware.svg?branch=master   :target: https://travis-ci.org/lrowe/subprocess_middleware

This package was built to support rendering Python generated JSON into HTML using a nodejs.
Transform subprocesses are reused, avoiding process startup overhead and allowing the JIT to kick in.
For our code this gives a 10x speedup for subsequent responses.

The protocol is simple and generic, HTTP formatted responses (headers and body) are piped into and out of the transform subprocess.
Transforms may modify both the response headers and body.

Transforms modifying the response body must ensure the Content-Length header is updated to match.


Python 2 and subprocess32
-------------------------

The subprocess module in Python 2.7 can leak file descriptors.
Backported fixes from Python 3.x are available in subprocess32_, and will be used if installed.

.. _subprocess32: https://pypi.python.org/pypi/subprocess32


Pipe buffering
--------------

For small responses, the unix command ``cat`` works as an identity transform.
Once a response exceeds the pipe buffer limit (typically 16K or 64K), a deadlock occurs with both processes waiting for the other to read.
To avoid this, subprocesses should read in the entirity of each response before writing to stdout and flush stdout at the response end.

Working around this limitation would require writing and reading from different threads.


Alternatives
============

Apache mod_ext_filter
---------------------

With mod_ext_filter_, the response body is simply piped through an external program.
A new process is started for each response, so it suffers from the same limitations as CGI where application setup costs are paid for each request.

.. _mod_ext_filter: http://httpd.apache.org/docs/2.4/en/mod/mod_ext_filter.html


FastCGI filter
--------------

FastCGI_ defines a filter role for transforming responses using long-lived processes.
Unfortunately the filter role is not supported by Apache mod_fcgid_ and the FastCGI protocol itself is unnecessarily complicated to implement.

.. _FastCGI: http://www.fastcgi.com/devkit/doc/fastcgi-prog-guide/ch1intro.htm
.. _mod_fcgid: http://httpd.apache.org/mod_fcgid/mod/mod_fcgid.html


Transforming HTTP reverse proxy
-------------------------------

Another alternative would be to implement the transform as part of an HTTP proxy.
This adds significant deployment complexity with multiple hops required to support SSL.


PyV8
----

PyV8_ allows running JavaScript in process.
It can be tricky to build whereas nodejs packages are easily available.

.. _PyV8: https://pypi.python.org/pypi/PyV8

uWSGI Transformations
---------------------

uWSGI_ are working on an rpc plugin for their transformation system.
The rpc protocol itself has a 64k request size limit.

.. _uWSGI: http://uwsgi-docs.readthedocs.org/
