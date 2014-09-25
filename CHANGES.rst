Changelog
=========

0.2 (2014-09-24)
----------------

* Tweak error handling to just use ValueError.
  The ``transform_error`` handler now receives just the single ValueError message.

* Avoid instantiating huge strings by reading blocks.

* Support chunked transfer encoding.

0.1 (2014-05-12)
----------------

* Initial release.
