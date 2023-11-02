#!/usr/bin/env bash

set -eux

# does it work?
distronode-playbook can_register.yml -i ../../inventory -v "$@"

# ensure we do error when it its apprpos
set +e
result="$(distronode-playbook invalid.yml -i ../../inventory -v "$@" 2>&1)"
set -e
grep -q "Invalid variable name in " <<< "${result}"
