from __future__ import absolute_import, division, print_function
__metaclass__ = type

import tempfile

try:
    import urllib2  # intentionally trigger pylint distronode-bad-import error  # pylint: disable=unused-import
except ImportError:
    urllib2 = None

try:
    from urllib2 import Request  # intentionally trigger pylint distronode-bad-import-from error  # pylint: disable=unused-import
except ImportError:
    Request = None

tempfile.mktemp()  # intentionally trigger pylint distronode-bad-function error
