# Copyright 2019 RedHat, inc
#
# This file is part of Distronode
#
# Distronode is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Distronode is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Distronode.  If not, see <http://www.gnu.org/licenses/>.
#############################################
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    vars: v1_vars_plugin
    version_added: "2.10"
    short_description: load host and group vars
    description:
      - 3rd party vars plugin to test loading host and group vars without requiring whitelisting and without a plugin-specific stage option
    options:
'''

from distronode.plugins.vars import BaseVarsPlugin


class VarsModule(BaseVarsPlugin):

    def get_vars(self, loader, path, entities, cache=True):
        super(VarsModule, self).get_vars(loader, path, entities)
        return {'collection': False, 'name': 'v1_vars_plugin', 'v1_vars_plugin': True}
