Changelog
=========

0.3 (2014-09-26)
----------------

* Make subprocess reloading hookable, e.g. check subprocess memory with psutil.

* Ensure subprocess startup errors are logged.

0.2 (2014-09-24)
----------------

* Tweak error handling to just use ValueError.
  The ``transform_error`` handler now receives just the single ValueError message.

* Avoid instantiating huge strings by reading blocks.

* Support chunked transfer encoding.

0.1 (2014-05-12)
----------------

* Initial release.
