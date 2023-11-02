#
# (c) 2016 Red Hat Inc.
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
#
from __future__ import annotations


import sys
import copy

from distronode_collections.distronode.netcommon.plugins.action.network import (
    ActionModule as ActionNetworkModule,
)
from distronode_collections.distronode.netcommon.plugins.module_utils.network.common.utils import (
    load_provider,
)
from distronode_collections.vyos.vyos.plugins.module_utils.network.vyos.vyos import (
    vyos_provider_spec,
)
from distronode.utils.display import Display

display = Display()


class ActionModule(ActionNetworkModule):
    def run(self, tmp=None, task_vars=None):
        del tmp  # tmp no longer has any effect

        module_name = self._task.action.split(".")[-1]
        self._config_module = True if module_name == "vyos_config" else False
        persistent_connection = self._play_context.connection.split(".")[-1]
        warnings = []

        if persistent_connection == "network_cli":
            provider = self._task.args.get("provider", {})
            if any(provider.values()):
                display.warning(
                    "provider is unnecessary when using network_cli and will be ignored"
                )
                del self._task.args["provider"]
        elif self._play_context.connection == "local":
            provider = load_provider(vyos_provider_spec, self._task.args)
            pc = copy.deepcopy(self._play_context)
            pc.connection = "distronode.netcommon.network_cli"
            pc.network_os = "vyos.vyos.vyos"
            pc.remote_addr = provider["host"] or self._play_context.remote_addr
            pc.port = int(provider["port"] or self._play_context.port or 22)
            pc.remote_user = (
                provider["username"] or self._play_context.connection_user
            )
            pc.password = provider["password"] or self._play_context.password
            pc.private_key_file = (
                provider["ssh_keyfile"] or self._play_context.private_key_file
            )

            connection = self._shared_loader_obj.connection_loader.get(
                "distronode.netcommon.persistent",
                pc,
                sys.stdin,
                task_uuid=self._task._uuid,
            )

            # TODO: Remove below code after distronode minimal is cut out
            if connection is None:
                pc.connection = "network_cli"
                pc.network_os = "vyos"
                connection = self._shared_loader_obj.connection_loader.get(
                    "persistent", pc, sys.stdin, task_uuid=self._task._uuid
                )

            display.vvv(
                "using connection plugin %s (was local)" % pc.connection,
                pc.remote_addr,
            )

            command_timeout = (
                int(provider["timeout"])
                if provider["timeout"]
                else connection.get_option("persistent_command_timeout")
            )
            connection.set_options(
                direct={"persistent_command_timeout": command_timeout}
            )

            socket_path = connection.run()
            display.vvvv("socket_path: %s" % socket_path, pc.remote_addr)
            if not socket_path:
                return {
                    "failed": True,
                    "msg": "unable to open shell. Please see: "
                    + "https://docs.distronode.com/distronode/latest/network/user_guide/network_debug_troubleshooting.html#category-unable-to-open-shell",
                }

            task_vars["distronode_socket"] = socket_path
            warnings.append(
                [
                    "connection local support for this module is deprecated and will be removed in version 2.14, use connection %s"
                    % pc.connection
                ]
            )
        else:
            return {
                "failed": True,
                "msg": "Connection type %s is not valid for this module"
                % self._play_context.connection,
            }

        result = super(ActionModule, self).run(task_vars=task_vars)
        if warnings:
            if "warnings" in result:
                result["warnings"].extend(warnings)
            else:
                result["warnings"] = warnings
        return result