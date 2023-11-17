#!/usr/bin/python
from __future__ import absolute_import, division, print_function
__metaclass__ = type

from distronode.module_utils.basic import DistronodeModule
# overridden
from distronode.module_utils.distronode_release import data

results = {"data": data}

DistronodeModule(argument_spec=dict()).exit_json(**results)
