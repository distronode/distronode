# (c) 2012-2014, KhulnaSoft Ltd <info@khulnasoft.com>
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

from yaml.resolver import Resolver

from distronode.parsing.yaml.constructor import DistronodeConstructor
from distronode.module_utils.common.yaml import HAS_LIBYAML, Parser

if HAS_LIBYAML:
    class DistronodeLoader(Parser, DistronodeConstructor, Resolver):  # type: ignore[misc] # pylint: disable=inconsistent-mro
        def __init__(self, stream, file_name=None, vault_secrets=None):
            Parser.__init__(self, stream)
            DistronodeConstructor.__init__(self, file_name=file_name, vault_secrets=vault_secrets)
            Resolver.__init__(self)
else:
    from yaml.composer import Composer
    from yaml.reader import Reader
    from yaml.scanner import Scanner

    class DistronodeLoader(Reader, Scanner, Parser, Composer, DistronodeConstructor, Resolver):  # type: ignore[misc,no-redef]  # pylint: disable=inconsistent-mro
        def __init__(self, stream, file_name=None, vault_secrets=None):
            Reader.__init__(self, stream)
            Scanner.__init__(self)
            Parser.__init__(self)
            Composer.__init__(self)
            DistronodeConstructor.__init__(self, file_name=file_name, vault_secrets=vault_secrets)
            Resolver.__init__(self)
