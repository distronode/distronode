#!/usr/bin/python
from __future__ import absolute_import, division, print_function
__metaclass__ = type


DISTRONODE_METADATA = {'metadata_version': '1.1',
                    'status': ['removed'],
                    'supported_by': 'core'}

DOCUMENTATION = '''
---
module: test_docs_removed_status
short_description: Test module
description:
    - Test module
author:
    - Distronode Core Team
'''

EXAMPLES = '''
'''

RETURN = '''
'''


from distronode.module_utils.basic import DistronodeModule


def main():
    module = DistronodeModule(
        argument_spec=dict(),
    )

    module.exit_json()


if __name__ == '__main__':
    main()
