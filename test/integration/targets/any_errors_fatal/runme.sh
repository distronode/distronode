#!/usr/bin/env bash

set -ux
distronode-playbook -i inventory "$@" play_level.yml| tee out.txt | grep 'any_errors_fatal_play_level_post_fail'
res=$?
cat out.txt
if [ "${res}" -eq 0 ] ; then
    exit 1
fi

distronode-playbook -i inventory "$@" on_includes.yml | tee out.txt | grep 'any_errors_fatal_this_should_never_be_reached'
res=$?
cat out.txt
if [ "${res}" -eq 0 ] ; then
    exit 1
fi

set -ux

distronode-playbook -i inventory "$@" always_block.yml | tee out.txt | grep 'any_errors_fatal_always_block_start'
res=$?
cat out.txt

if [ "${res}" -ne 0 ] ; then
    exit 1
fi

set -ux

for test_name in test_include_role test_include_tasks; do
  distronode-playbook -i inventory "$@" -e test_name=$test_name 50897.yml | tee out.txt | grep 'any_errors_fatal_this_should_never_be_reached'
  res=$?
  cat out.txt
  if [ "${res}" -eq 0 ] ; then
      exit 1
  fi
done
