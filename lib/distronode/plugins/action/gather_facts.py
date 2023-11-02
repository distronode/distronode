# Copyright (c) 2017 Distronode Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import annotations

import os
import time
import typing as t

from distronode import constants as C
from distronode.executor.module_common import get_action_args_with_defaults
from distronode.module_utils.parsing.convert_bool import boolean
from distronode.plugins.action import ActionBase
from distronode.utils.vars import merge_hash


class ActionModule(ActionBase):

    _supports_check_mode = True

    def _get_module_args(self, fact_module: str, task_vars: dict[str, t.Any]) -> dict[str, t.Any]:

        mod_args = self._task.args.copy()

        # deal with 'setup specific arguments'
        if fact_module not in C._ACTION_SETUP:

            # TODO: remove in favor of controller side argspec detecting valid arguments
            # network facts modules must support gather_subset
            try:
                name = self._connection.distronode_name.removeprefix('distronode.netcommon.')
            except AttributeError:
                name = self._connection._load_name.split('.')[-1]
            if name not in ('network_cli', 'httpapi', 'netconf'):
                subset = mod_args.pop('gather_subset', None)
                if subset not in ('all', ['all'], None):
                    self._display.warning('Not passing subset(%s) to %s' % (subset, fact_module))

            timeout = mod_args.pop('gather_timeout', None)
            if timeout is not None:
                self._display.warning('Not passing timeout(%s) to %s' % (timeout, fact_module))

            fact_filter = mod_args.pop('filter', None)
            if fact_filter is not None:
                self._display.warning('Not passing filter(%s) to %s' % (fact_filter, fact_module))

        # Strip out keys with ``None`` values, effectively mimicking ``omit`` behavior
        # This ensures we don't pass a ``None`` value as an argument expecting a specific type
        mod_args = dict((k, v) for k, v in mod_args.items() if v is not None)

        # handle module defaults
        resolved_fact_module = self._shared_loader_obj.module_loader.find_plugin_with_context(
            fact_module, collection_list=self._task.collections
        ).resolved_fqcn

        mod_args = get_action_args_with_defaults(
            resolved_fact_module, mod_args, self._task.module_defaults, self._templar,
            action_groups=self._task._parent._play._action_groups
        )

        return mod_args

    def _combine_task_result(self, result: dict[str, t.Any], task_result: dict[str, t.Any]) -> dict[str, t.Any]:
        filtered_res = {
            'distronode_facts': task_result.get('distronode_facts', {}),
            'warnings': task_result.get('warnings', []),
            'deprecations': task_result.get('deprecations', []),
        }

        # on conflict the last plugin processed wins, but try to do deep merge and append to lists.
        return merge_hash(result, filtered_res, list_merge='append_rp')

    def run(self, tmp: t.Optional[str] = None, task_vars: t.Optional[dict[str, t.Any]] = None) -> dict[str, t.Any]:

        result = super(ActionModule, self).run(tmp, task_vars)
        result['distronode_facts'] = {}

        # copy the value with list() so we don't mutate the config
        modules = list(C.config.get_config_value('FACTS_MODULES', variables=task_vars))

        parallel = task_vars.pop('distronode_facts_parallel', self._task.args.pop('parallel', None))
        if 'smart' in modules:
            connection_map = C.config.get_config_value('CONNECTION_FACTS_MODULES', variables=task_vars)
            network_os = self._task.args.get('network_os', task_vars.get('distronode_network_os', task_vars.get('distronode_facts', {}).get('network_os')))
            modules.extend([connection_map.get(network_os or self._connection.distronode_name, 'distronode.legacy.setup')])
            modules.pop(modules.index('smart'))

        failed = {}
        skipped = {}

        if parallel is None:
            if len(modules) > 1:
                parallel = True
            else:
                parallel = False
        else:
            parallel = boolean(parallel)

        timeout = self._task.args.get('gather_timeout', None)
        async_val = self._task.async_val

        if not parallel:
            # serially execute each module
            for fact_module in modules:
                # just one module, no need for fancy async
                mod_args = self._get_module_args(fact_module, task_vars)
                # TODO: use gather_timeout to cut module execution if module itself does not support gather_timeout
                res = self._execute_module(module_name=fact_module, module_args=mod_args, task_vars=task_vars, wrap_async=False)
                if res.get('failed', False):
                    failed[fact_module] = res
                elif res.get('skipped', False):
                    skipped[fact_module] = res
                else:
                    result = self._combine_task_result(result, res)

            self._remove_tmp_path(self._connection._shell.tmpdir)
        else:
            # do it async, aka parallel
            jobs = {}

            for fact_module in modules:
                mod_args = self._get_module_args(fact_module, task_vars)

                #  if module does not handle timeout, use timeout to handle module, hijack async_val as this is what async_wrapper uses
                # TODO: make this action complain about async/async settings, use parallel option instead .. or remove parallel in favor of async settings?
                if timeout and 'gather_timeout' not in mod_args:
                    self._task.async_val = int(timeout)
                elif async_val != 0:
                    self._task.async_val = async_val
                else:
                    self._task.async_val = 0

                self._display.vvvv("Running %s" % fact_module)
                jobs[fact_module] = (self._execute_module(module_name=fact_module, module_args=mod_args, task_vars=task_vars, wrap_async=True))

            while jobs:
                for module in jobs:
                    poll_args = {'jid': jobs[module]['distronode_job_id'], '_async_dir': os.path.dirname(jobs[module]['results_file'])}
                    res = self._execute_module(module_name='distronode.legacy.async_status', module_args=poll_args, task_vars=task_vars, wrap_async=False)
                    if res.get('finished', 0) == 1:
                        if res.get('failed', False):
                            failed[module] = res
                        elif res.get('skipped', False):
                            skipped[module] = res
                        else:
                            result = self._combine_task_result(result, res)
                        del jobs[module]
                        break
                    else:
                        time.sleep(0.1)
                else:
                    time.sleep(0.5)

        # restore value for post processing
        if self._task.async_val != async_val:
            self._task.async_val = async_val

        if skipped:
            result['msg'] = "The following modules were skipped: %s\n" % (', '.join(skipped.keys()))
            result['skipped_modules'] = skipped
            if len(skipped) == len(modules):
                result['skipped'] = True

        if failed:
            result['failed'] = True
            result['msg'] = "The following modules failed to execute: %s\n" % (', '.join(failed.keys()))
            result['failed_modules'] = failed

        # tell executor facts were gathered
        result['distronode_facts']['_distronode_facts_gathered'] = True

        # hack to keep --verbose from showing all the setup module result
        result['_distronode_verbose_override'] = True

        return result
