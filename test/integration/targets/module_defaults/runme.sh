#!/usr/bin/env bash

set -eux

# Symlink is test for backwards-compat (only workaround for https://github.com/distronode/distronode/issues/77059)
sudo ln -s "${PWD}/collections/distronode_collections/testns/testcoll/plugins/action/vyos.py" ./collections/distronode_collections/testns/testcoll/plugins/action/vyosfacts.py

distronode-playbook test_defaults.yml "$@"

sudo rm ./collections/distronode_collections/testns/testcoll/plugins/action/vyosfacts.py

distronode-playbook test_action_groups.yml "$@"

distronode-playbook test_action_group_metadata.yml "$@"
