#!/usr/bin/env bash

set -eux

DISTRONODE_GATHER_SUBSET='min' distronode-playbook base.yml "$@"
