from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from distronode_collections.testns.testcoll.plugins.module_utils import secondary
import distronode_collections.testns.testcoll.plugins.module_utils.secondary


def thingtocall():
    if secondary != distronode_collections.testns.testcoll.plugins.module_utils.secondary:
        raise Exception()

    return "thingtocall in base called " + distronode_collections.testns.testcoll.plugins.module_utils.secondary.thingtocall()
