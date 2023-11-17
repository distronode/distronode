# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
name: deprecated
short_description: lookup
description: Lookup.
author:
  - Distronode Core Team
'''

EXAMPLES = '''#'''
RETURN = '''#'''

from distronode.plugins.lookup import LookupBase


class LookupModule(LookupBase):
    def run(self, **kwargs):
        return []
