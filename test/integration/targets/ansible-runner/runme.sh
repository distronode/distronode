#!/usr/bin/env bash

set -eux

source virtualenv.sh

DISTRONODE_ROLES_PATH=../ distronode-playbook test.yml -i inventory "$@"
