#!/usr/bin/env bash

set -eux

source virtualenv.sh

# Requirements have to be installed prior to running distronode-playbook
# because plugins and requirements are loaded before the task runs
pip install passlib

DISTRONODE_ROLES_PATH=../ distronode-playbook runme.yml -e "output_dir=${OUTPUT_DIR}" "$@"
