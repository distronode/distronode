# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
    name: lookup2
    author: Distronode Core Team
    short_description: hello test lookup
    description:
        - Hello test lookup.
    options: {}
"""

EXAMPLES = """
- minimal:
"""

RETURN = """
"""

from distronode.plugins.lookup import LookupBase


class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):
        return []
