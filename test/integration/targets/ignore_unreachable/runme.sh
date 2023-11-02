#!/usr/bin/env bash
set -eux

export DISTRONODE_CONNECTION_PLUGINS=./fake_connectors
# use fake connectors that raise srrors at different stages
distronode-playbook test_with_bad_plugins.yml -i inventory -v "$@"
unset DISTRONODE_CONNECTION_PLUGINS

distronode-playbook test_cannot_connect.yml -i inventory -v "$@"

if distronode-playbook test_base_cannot_connect.yml -i inventory -v "$@"; then
    echo "Playbook intended to fail succeeded. Connection succeeded to nonexistent host"
    exit 99
else
    echo "Connection to nonexistent hosts failed without using ignore_unreachable. Success!"
fi
