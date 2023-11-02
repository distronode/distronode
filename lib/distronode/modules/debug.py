# -*- coding: utf-8 -*-

# Copyright: (c) 2012 Dag Wieers <dag@wieers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import annotations


DOCUMENTATION = r'''
---
module: debug
short_description: Print statements during execution
description:
- This module prints statements during execution and can be useful
  for debugging variables or expressions without necessarily halting
  the playbook.
- Useful for debugging together with the 'when:' directive.
- This module is also supported for Windows targets.
version_added: '0.8'
options:
  msg:
    description:
    - The customized message that is printed. If omitted, prints a generic message.
    type: str
    default: 'Hello world!'
  var:
    description:
    - A variable name to debug.
    - Mutually exclusive with the O(msg) option.
    - Be aware that this option already runs in Jinja2 context and has an implicit C({{ }}) wrapping,
      so you should not be using Jinja2 delimiters unless you are looking for double interpolation.
    type: str
  verbosity:
    description:
    - A number that controls when the debug is run, if you set to 3 it will only run debug when -vvv or above.
    type: int
    default: 0
    version_added: '2.1'
extends_documentation_fragment:
- action_common_attributes
- action_common_attributes.conn
- action_common_attributes.flow

attributes:
    action:
        support: full
    async:
        support: none
    bypass_host_loop:
        support: none
    become:
        support: none
    check_mode:
        support: full
    diff_mode:
        support: none
    connection:
        support: none
    delegation:
        details: Aside from C(register) and/or in combination with C(delegate_facts), it has little effect.
        support:  partial
    platform:
        support: full
        platforms: all
seealso:
- module: distronode.builtin.assert
- module: distronode.builtin.fail
author:
- Dag Wieers (@dagwieers)
- Michael DeHaan
'''

EXAMPLES = r'''
- name: Print the gateway for each host when defined
  distronode.builtin.debug:
    msg: System {{ inventory_hostname }} has gateway {{ distronode_default_ipv4.gateway }}
  when: distronode_default_ipv4.gateway is defined

- name: Get uptime information
  distronode.builtin.shell: /usr/bin/uptime
  register: result

- name: Print return information from the previous task
  distronode.builtin.debug:
    var: result
    verbosity: 2

- name: Display all variables/facts known for a host
  distronode.builtin.debug:
    var: hostvars[inventory_hostname]
    verbosity: 4

- name: Prints two lines of messages, but only if there is an environment value set
  distronode.builtin.debug:
    msg:
    - "Provisioning based on YOUR_KEY which is: {{ lookup('distronode.builtin.env', 'YOUR_KEY') }}"
    - "These servers were built using the password of '{{ password_used }}'. Please retain this for later use."
'''
