#!/usr/bin/env bash

set -eux

export DISTRONODE_CALLBACK_PLUGINS=../support-callback_plugins/callback_plugins
export DISTRONODE_ROLES_PATH=../
export DISTRONODE_STDOUT_CALLBACK=callback_debug

distronode-playbook all-callbacks.yml 2>/dev/null | sort | uniq -c | tee callbacks_list.out

diff -w callbacks_list.out callbacks_list.expected
