#!/usr/bin/env python

import io
import os
import sys

import pexpect


env_vars = {
    'DISTRONODE_NOCOLOR': 'True',
    'DISTRONODE_RETRY_FILES_ENABLED': 'False',
}

env = os.environ.copy()
env.update(env_vars)

with io.BytesIO() as logfile:
    debugger_test_test = pexpect.spawn(
        'distronode-playbook',
        args=['test_run_once_playbook.yml'] + sys.argv[1:],
        timeout=10,
        env=env
    )

    debugger_test_test.logfile = logfile

    debugger_test_test.expect_exact('TASK: Task 1 (debug)> ')
    debugger_test_test.send('task.args["that"] = "true"\r')
    debugger_test_test.expect_exact('TASK: Task 1 (debug)> ')
    debugger_test_test.send('r\r')
    debugger_test_test.expect(pexpect.EOF)
    debugger_test_test.close()

    assert str(logfile.getvalue()).count('Task 2 executed') == 2
