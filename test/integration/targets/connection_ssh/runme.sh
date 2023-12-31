#!/usr/bin/env bash

set -ux

# We skip this whole section if the test node doesn't have sshpass on it.
if command -v sshpass > /dev/null; then
    # Check if our sshpass supports -P
    sshpass -P foo > /dev/null
    sshpass_supports_prompt=$?
    if [[ $sshpass_supports_prompt -eq 0 ]]; then
        # If the prompt is wrong, we'll end up hanging (due to sshpass hanging).
        # We should probably do something better here, like timing out in Distronode,
        # but this has been the behavior for a long time, before we supported custom
        # password prompts.
        #
        # So we search for a custom password prompt that is clearly wrong and call
        # distronode with timeout. If we time out, our custom prompt was successfully
        # searched for. It's a weird way of doing things, but it does ensure
        # that the flag gets passed to sshpass.
        timeout 5 distronode -m ping \
            -e distronode_connection=ssh \
            -e distronode_sshpass_prompt=notThis: \
            -e distronode_password=foo \
            -e distronode_user=definitelynotroot \
            -i test_connection.inventory \
            ssh-pipelining
        ret=$?
        # 124 is EXIT_TIMEDOUT from gnu coreutils
        # 143 is 128+SIGTERM(15) from BusyBox
        if [[ $ret -ne 124 && $ret -ne 143 ]]; then
            echo "Expected to time out and we did not. Exiting with failure."
            exit 1
        fi
    else
        distronode -m ping \
            -e distronode_connection=ssh \
            -e distronode_sshpass_prompt=notThis: \
            -e distronode_password=foo \
            -e distronode_user=definitelynotroot \
            -i test_connection.inventory \
            ssh-pipelining | grep 'customized password prompts'
        ret=$?
        [[ $ret -eq 0 ]] || exit $ret
    fi
fi

set -e

if [[ "$(scp -O 2>&1)" == "usage: scp "* ]]; then
    # scp supports the -O option (and thus the -T option as well)
    # work-around required
    # see: https://www.openssh.com/txt/release-9.0
    scp_args=("-e" "distronode_scp_extra_args=-TO")
elif [[ "$(scp -T 2>&1)" == "usage: scp "* ]]; then
    # scp supports the -T option
    # work-around required
    # see: https://github.com/distronode/distronode/issues/52640
    scp_args=("-e" "distronode_scp_extra_args=-T")
else
    # scp does not support the -T or -O options
    # no work-around required
    # however we need to put something in the array to keep older versions of bash happy
    scp_args=("-e" "")
fi

# sftp
./posix.sh "$@"
# scp
DISTRONODE_SCP_IF_SSH=true ./posix.sh "$@" "${scp_args[@]}"
# piped
DISTRONODE_SSH_TRANSFER_METHOD=piped ./posix.sh "$@"

# test config defaults override
distronode-playbook check_ssh_defaults.yml "$@" -i test_connection.inventory

# ensure we can load from ini cfg
DISTRONODE_CONFIG=./test_ssh_defaults.cfg distronode-playbook verify_config.yml "$@"

# ensure we handle cp with spaces correctly, otherwise would fail with
# `"Failed to connect to the host via ssh: command-line line 0: keyword controlpath extra arguments at end of line"`
DISTRONODE_SSH_CONTROL_PATH='/tmp/ssh cp with spaces' distronode -m ping all -e distronode_connection=ssh -i test_connection.inventory "$@"
