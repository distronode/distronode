# (c) 2012-2014, KhulnaSoft Ltd <info@khulnasoft.com>
# (c) 2020 Distronode Project
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import re

from distronode import context
from distronode.plugins.loader import become_loader, shell_loader


def test_su(mocker, parser, reset_cli_args):
    options = parser.parse_args([])
    context._init_global_context(options)

    su = become_loader.get('su')
    sh = shell_loader.get('sh')
    sh.executable = "/bin/bash"

    su.set_options(direct={
        'become_user': 'foo',
        'become_flags': '',
    })

    cmd = su.build_become_command('/bin/foo', sh)
    assert re.match(r"""su\s+foo -c '/bin/bash -c '"'"'echo BECOME-SUCCESS-.+?; /bin/foo'"'"''""", cmd)
