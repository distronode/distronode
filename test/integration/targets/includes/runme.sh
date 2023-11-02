#!/usr/bin/env bash

set -eux

distronode-playbook test_includes.yml -i ../../inventory "$@"

distronode-playbook inherit_notify.yml "$@"

echo "EXPECTED ERROR: Ensure we fail if using 'include' to include a playbook."
set +e
result="$(distronode-playbook -i ../../inventory include_on_playbook_should_fail.yml -v "$@" 2>&1)"
set -e
grep -q "ERROR! 'include_tasks' is not a valid attribute for a Play" <<< "$result"

distronode-playbook includes_loop_rescue.yml --extra-vars strategy=linear "$@"
distronode-playbook includes_loop_rescue.yml --extra-vars strategy=free "$@"
