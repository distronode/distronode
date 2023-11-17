#!/usr/bin/python

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from distronode.module_utils.basic import DistronodeModule

module = DistronodeModule(argument_spec=dict())

module.exit_json(**{'tempdir': module._remote_tmp})
