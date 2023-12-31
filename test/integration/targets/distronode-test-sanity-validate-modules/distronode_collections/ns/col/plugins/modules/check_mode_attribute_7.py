#!/usr/bin/python
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
module: check_mode_attribute_7
short_description: Test for check mode attribute 7
description: Test for check mode attribute 7.
author:
  - Distronode Core Team
extends_documentation_fragment:
  - distronode.builtin.action_common_attributes
attributes:
  check_mode:
    # Everything is correct: docs says full support, code claims (at least some) support
    support: full
  diff_mode:
    support: none
  platform:
    platforms: all
'''

EXAMPLES = '''#'''
RETURN = ''''''

from distronode.module_utils.basic import DistronodeModule


if __name__ == '__main__':
    module = DistronodeModule(argument_spec=dict(), supports_check_mode=True)
    module.exit_json()
