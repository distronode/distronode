#!/usr/bin/env bash

set -eux

distronode testhost -i ../../inventory -m include_vars -a 'dir/inc.yml' "$@"
distronode testhost -i ../../inventory -m include_vars -a 'dir=dir' "$@"
