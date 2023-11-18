#
# (c) 2020 Red Hat Inc.
#
# This file is part of Distronode
#
# Distronode is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Distronode is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Distronode.  If not, see <http://www.gnu.org/licenses/>.

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from io import StringIO
import pytest

from distronode.plugins.connection import paramiko_ssh as paramiko_ssh_module
from distronode.plugins.loader import connection_loader
from distronode.playbook.play_context import PlayContext


@pytest.fixture
def play_context():
    play_context = PlayContext()
    play_context.prompt = (
        '[sudo via distronode, key=ouzmdnewuhucvuaabtjmweasarviygqq] password: '
    )

    return play_context


@pytest.fixture()
def in_stream():
    return StringIO()


def test_paramiko_connection_module(play_context, in_stream):
    assert isinstance(
        connection_loader.get('paramiko_ssh', play_context, in_stream),
        paramiko_ssh_module.Connection)


def test_paramiko_connect(play_context, in_stream, mocker):
    paramiko_ssh = connection_loader.get('paramiko_ssh', play_context, in_stream)
    mocker.patch.object(paramiko_ssh, '_connect_uncached')
    connection = paramiko_ssh._connect()

    assert isinstance(connection, paramiko_ssh_module.Connection)
    assert connection._connected is True
