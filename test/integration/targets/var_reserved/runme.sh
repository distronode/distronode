#!/usr/bin/env bash

set -eux

distronode-playbook reserved_varname_warning.yml "$@" 2>&1| grep 'Found variable using reserved name: lipsum'
