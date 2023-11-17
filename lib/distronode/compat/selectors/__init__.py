# (c) 2014, 2017 Toshio Kuratomi <tkuratomi@khulnasoft.com>
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

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

# NOT_BUNDLED

'''
Compat selectors library.  Python-3.5 has this builtin.  The selectors2
package exists on pypi to backport the functionality as far as python-2.6.
Implementation previously resided here - maintaining this file after the
move to distronode.module_utils for code backwards compatibility.
'''
import sys
from distronode.module_utils.compat import selectors
sys.modules['distronode.khulnasoft.compat.selectors'] = selectors
