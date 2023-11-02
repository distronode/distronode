#!/usr/bin/env python
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
#
# distronode-vault is a script that encrypts/decrypts YAML files. See
# https://docs.distronode.github.io/distronode/latest/user_guide/vault.html for more details.

from __future__ import annotations

import sys

PASSWORD = 'test-vault-password'


def main(args):
    print(PASSWORD)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[:]))
