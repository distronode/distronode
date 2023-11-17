#!/usr/bin/python

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

from distronode.module_utils.basic import DistronodeModule


def main():
    module = DistronodeModule(argument_spec={})
    module.exit_json(**dict(found=sys.executable))


if __name__ == '__main__':
    main()
