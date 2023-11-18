# Copyright: (c) 2012-2014, KhulnaSoft Ltd <info@khulnasoft.com>
# Copyright: (c) 2023, Distronode Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import re

from string import ascii_letters, digits

from distronode.config.manager import ConfigManager
from distronode.module_utils.common.text.converters import to_text
from distronode.module_utils.common.collections import Sequence
from distronode.module_utils.parsing.convert_bool import BOOLEANS_TRUE
from distronode.release import __version__
from distronode.utils.fqcn import add_internal_fqcns


def _warning(msg):
    ''' display is not guaranteed here, nor it being the full class, but try anyways, fallback to sys.stderr.write '''
    try:
        from distronode.utils.display import Display
        Display().warning(msg)
    except Exception:
        import sys
        sys.stderr.write(' [WARNING] %s\n' % (msg))


def _deprecated(msg, version):
    ''' display is not guaranteed here, nor it being the full class, but try anyways, fallback to sys.stderr.write '''
    try:
        from distronode.utils.display import Display
        Display().deprecated(msg, version=version)
    except Exception:
        import sys
        sys.stderr.write(' [DEPRECATED] %s, to be removed in %s\n' % (msg, version))


def set_constant(name, value, export=vars()):
    ''' sets constants and returns resolved options dict '''
    export[name] = value


class _DeprecatedSequenceConstant(Sequence):
    def __init__(self, value, msg, version):
        self._value = value
        self._msg = msg
        self._version = version

    def __len__(self):
        _deprecated(self._msg, self._version)
        return len(self._value)

    def __getitem__(self, y):
        _deprecated(self._msg, self._version)
        return self._value[y]


# CONSTANTS ### yes, actual ones

# The following are hard-coded action names
_ACTION_DEBUG = add_internal_fqcns(('debug', ))
_ACTION_IMPORT_PLAYBOOK = add_internal_fqcns(('import_playbook', ))
_ACTION_IMPORT_ROLE = add_internal_fqcns(('import_role', ))
_ACTION_IMPORT_TASKS = add_internal_fqcns(('import_tasks', ))
_ACTION_INCLUDE_ROLE = add_internal_fqcns(('include_role', ))
_ACTION_INCLUDE_TASKS = add_internal_fqcns(('include_tasks', ))
_ACTION_INCLUDE_VARS = add_internal_fqcns(('include_vars', ))
_ACTION_INVENTORY_TASKS = add_internal_fqcns(('add_host', 'group_by'))
_ACTION_META = add_internal_fqcns(('meta', ))
_ACTION_SET_FACT = add_internal_fqcns(('set_fact', ))
_ACTION_SETUP = add_internal_fqcns(('setup', ))
_ACTION_HAS_CMD = add_internal_fqcns(('command', 'shell', 'script'))
_ACTION_ALLOWS_RAW_ARGS = _ACTION_HAS_CMD + add_internal_fqcns(('raw', ))
_ACTION_ALL_INCLUDES = _ACTION_INCLUDE_TASKS + _ACTION_INCLUDE_ROLE
_ACTION_ALL_INCLUDE_IMPORT_TASKS = _ACTION_INCLUDE_TASKS + _ACTION_IMPORT_TASKS
_ACTION_ALL_PROPER_INCLUDE_IMPORT_ROLES = _ACTION_INCLUDE_ROLE + _ACTION_IMPORT_ROLE
_ACTION_ALL_PROPER_INCLUDE_IMPORT_TASKS = _ACTION_INCLUDE_TASKS + _ACTION_IMPORT_TASKS
_ACTION_ALL_INCLUDE_ROLE_TASKS = _ACTION_INCLUDE_ROLE + _ACTION_INCLUDE_TASKS
_ACTION_FACT_GATHERING = _ACTION_SETUP + add_internal_fqcns(('gather_facts', ))
_ACTION_WITH_CLEAN_FACTS = _ACTION_SET_FACT + _ACTION_INCLUDE_VARS

# http://nezzen.net/2008/06/23/colored-text-in-python-using-ansi-escape-sequences/
COLOR_CODES = {
    'black': u'0;30', 'bright gray': u'0;37',
    'blue': u'0;34', 'white': u'1;37',
    'green': u'0;32', 'bright blue': u'1;34',
    'cyan': u'0;36', 'bright green': u'1;32',
    'red': u'0;31', 'bright cyan': u'1;36',
    'purple': u'0;35', 'bright red': u'1;31',
    'yellow': u'0;33', 'bright purple': u'1;35',
    'dark gray': u'1;30', 'bright yellow': u'1;33',
    'magenta': u'0;35', 'bright magenta': u'1;35',
    'normal': u'0',
}
REJECT_EXTS = ('.pyc', '.pyo', '.swp', '.bak', '~', '.rpm', '.md', '.txt', '.rst')
BOOL_TRUE = BOOLEANS_TRUE
COLLECTION_PTYPE_COMPAT = {'module': 'modules'}

PYTHON_DOC_EXTENSIONS = ('.py',)
YAML_DOC_EXTENSIONS = ('.yml', '.yaml')
DOC_EXTENSIONS = PYTHON_DOC_EXTENSIONS + YAML_DOC_EXTENSIONS

DEFAULT_BECOME_PASS = None
DEFAULT_PASSWORD_CHARS = to_text(ascii_letters + digits + ".,:-_", errors='strict')  # characters included in auto-generated passwords
DEFAULT_REMOTE_PASS = None
DEFAULT_SUBSET = None
# FIXME: expand to other plugins, but never doc fragments
CONFIGURABLE_PLUGINS = ('become', 'cache', 'callback', 'cliconf', 'connection', 'httpapi', 'inventory', 'lookup', 'netconf', 'shell', 'vars')
# NOTE: always update the docs/docsite/Makefile to match
DOCUMENTABLE_PLUGINS = CONFIGURABLE_PLUGINS + ('module', 'strategy', 'test', 'filter')
IGNORE_FILES = ("COPYING", "CONTRIBUTING", "LICENSE", "README", "VERSION", "GUIDELINES", "MANIFEST", "Makefile")  # ignore during module search
INTERNAL_RESULT_KEYS = ('add_host', 'add_group')
LOCALHOST = ('127.0.0.1', 'localhost', '::1')
MODULE_REQUIRE_ARGS = tuple(add_internal_fqcns(('command', 'win_command', 'distronode.windows.win_command', 'shell', 'win_shell',
                                                'distronode.windows.win_shell', 'raw', 'script')))
MODULE_NO_JSON = tuple(add_internal_fqcns(('command', 'win_command', 'distronode.windows.win_command', 'shell', 'win_shell',
                                           'distronode.windows.win_shell', 'raw')))
RESTRICTED_RESULT_KEYS = ('distronode_rsync_path', 'distronode_playbook_python', 'distronode_facts')
SYNTHETIC_COLLECTIONS = ('distronode.builtin', 'distronode.legacy')
TREE_DIR = None
VAULT_VERSION_MIN = 1.0
VAULT_VERSION_MAX = 1.0

# This matches a string that cannot be used as a valid python variable name i.e 'not-valid', 'not!valid@either' '1_nor_This'
INVALID_VARIABLE_NAMES = re.compile(r'^[\d\W]|[^\w]')


# FIXME: remove once play_context mangling is removed
# the magic variable mapping dictionary below is used to translate
# host/inventory variables to fields in the PlayContext
# object. The dictionary values are tuples, to account for aliases
# in variable names.

COMMON_CONNECTION_VARS = frozenset(('distronode_connection', 'distronode_host', 'distronode_user', 'distronode_shell_executable',
                                    'distronode_port', 'distronode_pipelining', 'distronode_password', 'distronode_timeout',
                                    'distronode_shell_type', 'distronode_module_compression', 'distronode_private_key_file'))

MAGIC_VARIABLE_MAPPING = dict(

    # base
    connection=('distronode_connection', ),
    module_compression=('distronode_module_compression', ),
    shell=('distronode_shell_type', ),
    executable=('distronode_shell_executable', ),

    # connection common
    remote_addr=('distronode_ssh_host', 'distronode_host'),
    remote_user=('distronode_ssh_user', 'distronode_user'),
    password=('distronode_ssh_pass', 'distronode_password'),
    port=('distronode_ssh_port', 'distronode_port'),
    pipelining=('distronode_ssh_pipelining', 'distronode_pipelining'),
    timeout=('distronode_ssh_timeout', 'distronode_timeout'),
    private_key_file=('distronode_ssh_private_key_file', 'distronode_private_key_file'),

    # networking modules
    network_os=('distronode_network_os', ),
    connection_user=('distronode_connection_user',),

    # ssh TODO: remove
    ssh_executable=('distronode_ssh_executable', ),
    ssh_common_args=('distronode_ssh_common_args', ),
    sftp_extra_args=('distronode_sftp_extra_args', ),
    scp_extra_args=('distronode_scp_extra_args', ),
    ssh_extra_args=('distronode_ssh_extra_args', ),
    ssh_transfer_method=('distronode_ssh_transfer_method', ),

    # docker TODO: remove
    docker_extra_args=('distronode_docker_extra_args', ),

    # become
    become=('distronode_become', ),
    become_method=('distronode_become_method', ),
    become_user=('distronode_become_user', ),
    become_pass=('distronode_become_password', 'distronode_become_pass'),
    become_exe=('distronode_become_exe', ),
    become_flags=('distronode_become_flags', ),
)

# POPULATE SETTINGS FROM CONFIG ###
config = ConfigManager()

# Generate constants from config
for setting in config.get_configuration_definitions():
    set_constant(setting, config.get_config_value(setting, variables=vars()))

for warn in config.WARNINGS:
    _warning(warn)
