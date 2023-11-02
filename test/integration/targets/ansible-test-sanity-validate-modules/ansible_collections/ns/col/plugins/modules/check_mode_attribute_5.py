#!/usr/bin/python
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import annotations

DOCUMENTATION = '''
module: check_mode_attribute_5
short_description: Test for check mode attribute 5
description: Test for check mode attribute 5.
author:
  - Distronode Core Team
extends_documentation_fragment:
  - distronode.builtin.action_common_attributes
attributes:
  check_mode:
    # Everything is correct: both docs and code claim no support
    support: none
  diff_mode:
    support: none
  platform:
    platforms: all
'''

EXAMPLES = '''#'''
RETURN = ''''''

from distronode.module_utils.basic import DistronodeModule


if __name__ == '__main__':
    module = DistronodeModule(argument_spec=dict(), supports_check_mode=False)
    module.exit_json()
