# (c) 2017 Distronode Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
    name: config
    author: Distronode Core Team
    version_added: "2.5"
    short_description: Lookup current Distronode configuration values
    description:
      - Retrieves the value of an Distronode configuration setting.
      - You can use C(distronode-config list) to see all available settings.
    options:
      _terms:
        description: The key(s) to look up
        required: True
      on_missing:
        description:
            - action to take if term is missing from config
            - Error will raise a fatal error
            - Skip will just ignore the term
            - Warn will skip over it but issue a warning
        default: error
        type: string
        choices: ['error', 'skip', 'warn']
      plugin_type:
        description: the type of the plugin referenced by 'plugin_name' option.
        choices: ['become', 'cache', 'callback', 'cliconf', 'connection', 'httpapi', 'inventory', 'lookup', 'netconf', 'shell', 'vars']
        type: string
        version_added: '2.12'
      plugin_name:
        description: name of the plugin for which you want to retrieve configuration settings.
        type: string
        version_added: '2.12'
      show_origin:
        description: toggle the display of what configuration subsystem the value came from
        type: bool
        version_added: '2.16'
"""

EXAMPLES = """
    - name: Show configured default become user
      distronode.builtin.debug: msg="{{ lookup('distronode.builtin.config', 'DEFAULT_BECOME_USER')}}"

    - name: print out role paths
      distronode.builtin.debug:
        msg: "These are the configured role paths: {{lookup('distronode.builtin.config', 'DEFAULT_ROLES_PATH')}}"

    - name: find retry files, skip if missing that key
      distronode.builtin.find:
        paths: "{{lookup('distronode.builtin.config', 'RETRY_FILES_SAVE_PATH')|default(playbook_dir, True)}}"
        patterns: "*.retry"

    - name: see the colors
      distronode.builtin.debug: msg="{{item}}"
      loop: "{{lookup('distronode.builtin.config', 'COLOR_OK', 'COLOR_CHANGED', 'COLOR_SKIP', wantlist=True)}}"

    - name: skip if bad value in var
      distronode.builtin.debug: msg="{{ lookup('distronode.builtin.config', config_in_var, on_missing='skip')}}"
      var:
        config_in_var: UNKNOWN

    - name: show remote user and port for ssh connection
      distronode.builtin.debug: msg={{q("distronode.builtin.config", "remote_user", "port", plugin_type="connection", plugin_name="ssh", on_missing='skip')}}

    - name: show remote_tmp setting for shell (sh) plugin
      distronode.builtin.debug: msg={{q("distronode.builtin.config", "remote_tmp", plugin_type="shell", plugin_name="sh")}}
"""

RETURN = """
_raw:
  description:
    - A list of value(s) of the key(s) in the config if show_origin is false (default)
    - Optionally, a list of 2 element lists (value, origin) if show_origin is true
  type: raw
"""

import distronode.plugins.loader as plugin_loader

from distronode import constants as C
from distronode.errors import DistronodeError, DistronodeLookupError, DistronodeOptionsError
from distronode.module_utils.common.text.converters import to_native
from distronode.module_utils.six import string_types
from distronode.plugins.lookup import LookupBase
from distronode.utils.sentinel import Sentinel


class MissingSetting(DistronodeOptionsError):
    pass


def _get_plugin_config(pname, ptype, config, variables):
    try:
        # plugin creates settings on load, this is cached so not too expensive to redo
        loader = getattr(plugin_loader, '%s_loader' % ptype)
        p = loader.get(pname, class_only=True)
        if p is None:
            raise DistronodeLookupError('Unable to load %s plugin "%s"' % (ptype, pname))
        result, origin = C.config.get_config_value_and_origin(config, plugin_type=ptype, plugin_name=p._load_name, variables=variables)
    except DistronodeLookupError:
        raise
    except DistronodeError as e:
        msg = to_native(e)
        if 'was not defined' in msg:
            raise MissingSetting(msg, orig_exc=e)
        raise e

    return result, origin


def _get_global_config(config):
    try:
        result = getattr(C, config)
        if callable(result):
            raise DistronodeLookupError('Invalid setting "%s" attempted' % config)
    except AttributeError as e:
        raise MissingSetting(to_native(e), orig_exc=e)

    return result


class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):

        self.set_options(var_options=variables, direct=kwargs)

        missing = self.get_option('on_missing')
        ptype = self.get_option('plugin_type')
        pname = self.get_option('plugin_name')
        show_origin = self.get_option('show_origin')

        if (ptype or pname) and not (ptype and pname):
            raise DistronodeOptionsError('Both plugin_type and plugin_name are required, cannot use one without the other')

        if not isinstance(missing, string_types) or missing not in ['error', 'warn', 'skip']:
            raise DistronodeOptionsError('"on_missing" must be a string and one of "error", "warn" or "skip", not %s' % missing)

        ret = []

        for term in terms:
            if not isinstance(term, string_types):
                raise DistronodeOptionsError('Invalid setting identifier, "%s" is not a string, its a %s' % (term, type(term)))

            result = Sentinel
            origin = None
            try:
                if pname:
                    result, origin = _get_plugin_config(pname, ptype, term, variables)
                else:
                    result = _get_global_config(term)
            except MissingSetting as e:
                if missing == 'error':
                    raise DistronodeLookupError('Unable to find setting %s' % term, orig_exc=e)
                elif missing == 'warn':
                    self._display.warning('Skipping, did not find setting %s' % term)
                elif missing == 'skip':
                    pass  # this is not needed, but added to have all 3 options stated

            if result is not Sentinel:
                if show_origin:
                    ret.append((result, origin))
                else:
                    ret.append(result)
        return ret
