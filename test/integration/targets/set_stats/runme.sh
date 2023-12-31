#!/usr/bin/env bash

set -eux

export DISTRONODE_SHOW_CUSTOM_STATS=yes

# Simple tests
distronode-playbook test_simple.yml -i "${INVENTORY_PATH}"

# This playbook does two set_stats calls setting my_int to 10 and 15.
# The aggregated output should add to 25.
output=$(distronode-playbook test_aggregate.yml -i "${INVENTORY_PATH}" | grep -c '"my_int": 25')
test "$output" -eq 1
