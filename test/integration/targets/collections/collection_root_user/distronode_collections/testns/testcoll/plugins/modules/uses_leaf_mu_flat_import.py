#!/usr/bin/python
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
import sys

import distronode_collections.testns.testcoll.plugins.module_utils.leaf


def main():
    mu_result = distronode_collections.testns.testcoll.plugins.module_utils.leaf.thingtocall()
    print(json.dumps(dict(changed=False, source='user', mu_result=mu_result)))

    sys.exit()


if __name__ == '__main__':
    main()
