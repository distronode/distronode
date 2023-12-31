#!/bin/sh

set -ex

unset USR
# this should succeed and return 'nobody' as var is undefined
distronode -m debug -a msg="{{ lookup('env', 'USR', default='nobody')}}" localhost |grep nobody
# var is defined but empty, so should return empty
USR='' distronode -m debug -a msg="{{ lookup('env', 'USR', default='nobody')}}" localhost |grep -v nobody

# this should fail with undefined
distronode -m debug -a msg="{{ lookup('env', 'USR', default=Undefined)}}" localhost && exit 1 || exit 0
