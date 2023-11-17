#!/usr/bin/python
# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: collection_module
short_description: A module to test a task's resolved action name.
description: A module to test a task's resolved action name.
options: {}
author: Distronode Core Team
notes:
  - Supports C(check_mode).
'''

from distronode.module_utils.basic import DistronodeModule


def main():
    module = DistronodeModule(supports_check_mode=True, argument_spec={})
    module.exit_json(changed=False)


if __name__ == '__main__':
    main()
