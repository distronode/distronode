#!/usr/bin/env bash

set -eux

group=local

cd ../connection

INVENTORY="../connection_${group}/test_connection.inventory" ./test.sh \
    -e target_hosts="${group}" \
    -e action_prefix= \
    -e local_tmp=/tmp/distronode-local \
    -e remote_tmp=/tmp/distronode-remote \
    "$@"
