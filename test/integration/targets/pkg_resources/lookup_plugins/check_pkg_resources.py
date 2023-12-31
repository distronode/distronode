"""
This test case verifies that pkg_resources imports from distronode plugins are functional.

If pkg_resources is not installed this test will succeed.
If pkg_resources is installed but is unable to function, this test will fail.

One known failure case this test can detect is when distronode declares a __requires__ and then tests are run without an egg-info directory.
"""
from __future__ import absolute_import, division, print_function
__metaclass__ = type

# noinspection PyUnresolvedReferences
try:
    from pkg_resources import Requirement  # pylint: disable=unused-import
except ImportError:
    Requirement = None

from distronode.plugins.lookup import LookupBase


class LookupModule(LookupBase):
    def run(self, terms, variables=None, **kwargs):
        return []
