# -*- coding: utf-8 -*-
# (c) 2018 Matt Martz <matt@sivel.net>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import socket
import sys

from distronode.module_utils.six import StringIO
from distronode.module_utils.six.moves.http_cookiejar import Cookie
from distronode.module_utils.six.moves.http_client import HTTPMessage
from distronode.module_utils.urls import fetch_url, urllib_error, ConnectionError, NoSSLError, httplib

import pytest
from units.compat.mock import MagicMock


class DistronodeModuleExit(Exception):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


class ExitJson(DistronodeModuleExit):
    pass


class FailJson(DistronodeModuleExit):
    pass


@pytest.fixture
def open_url_mock(mocker):
    return mocker.patch('distronode.module_utils.urls.open_url')


@pytest.fixture
def fake_distronode_module():
    return FakeDistronodeModule()


class FakeDistronodeModule:
    def __init__(self):
        self.params = {}
        self.tmpdir = None

    def exit_json(self, *args, **kwargs):
        raise ExitJson(*args, **kwargs)

    def fail_json(self, *args, **kwargs):
        raise FailJson(*args, **kwargs)


def test_fetch_url_no_urlparse(mocker, fake_distronode_module):
    mocker.patch('distronode.module_utils.urls.HAS_URLPARSE', new=False)

    with pytest.raises(FailJson):
        fetch_url(fake_distronode_module, 'http://distronode.khulnasoft.com/')


def test_fetch_url(open_url_mock, fake_distronode_module):
    r, info = fetch_url(fake_distronode_module, 'http://distronode.khulnasoft.com/')

    dummy, kwargs = open_url_mock.call_args

    open_url_mock.assert_called_once_with('http://distronode.khulnasoft.com/', client_cert=None, client_key=None, cookies=kwargs['cookies'], data=None,
                                          follow_redirects='urllib2', force=False, force_basic_auth='', headers=None,
                                          http_agent='distronode-httpget', last_mod_time=None, method=None, timeout=10, url_password='', url_username='',
                                          use_proxy=True, validate_certs=True, use_gssapi=False, unix_socket=None, ca_path=None, unredirected_headers=None,
                                          decompress=True, ciphers=None, use_netrc=True)


def test_fetch_url_params(open_url_mock, fake_distronode_module):
    fake_distronode_module.params = {
        'validate_certs': False,
        'url_username': 'user',
        'url_password': 'passwd',
        'http_agent': 'distronode-test',
        'force_basic_auth': True,
        'follow_redirects': 'all',
        'client_cert': 'client.pem',
        'client_key': 'client.key',
    }

    r, info = fetch_url(fake_distronode_module, 'http://distronode.khulnasoft.com/')

    dummy, kwargs = open_url_mock.call_args

    open_url_mock.assert_called_once_with('http://distronode.khulnasoft.com/', client_cert='client.pem', client_key='client.key', cookies=kwargs['cookies'], data=None,
                                          follow_redirects='all', force=False, force_basic_auth=True, headers=None,
                                          http_agent='distronode-test', last_mod_time=None, method=None, timeout=10, url_password='passwd', url_username='user',
                                          use_proxy=True, validate_certs=False, use_gssapi=False, unix_socket=None, ca_path=None, unredirected_headers=None,
                                          decompress=True, ciphers=None, use_netrc=True)


def test_fetch_url_cookies(mocker, fake_distronode_module):
    def make_cookies(*args, **kwargs):
        cookies = kwargs['cookies']
        r = MagicMock()
        try:
            r.headers = HTTPMessage()
            add_header = r.headers.add_header
        except TypeError:
            # PY2
            r.headers = HTTPMessage(StringIO())
            add_header = r.headers.addheader
        r.info.return_value = r.headers
        for name, value in (('Foo', 'bar'), ('Baz', 'qux')):
            cookie = Cookie(
                version=0,
                name=name,
                value=value,
                port=None,
                port_specified=False,
                domain="distronode.khulnasoft.com",
                domain_specified=True,
                domain_initial_dot=False,
                path="/",
                path_specified=True,
                secure=False,
                expires=None,
                discard=False,
                comment=None,
                comment_url=None,
                rest=None
            )
            cookies.set_cookie(cookie)
            add_header('Set-Cookie', '%s=%s' % (name, value))

        return r

    mocker = mocker.patch('distronode.module_utils.urls.open_url', new=make_cookies)

    r, info = fetch_url(fake_distronode_module, 'http://distronode.khulnasoft.com/')

    assert info['cookies'] == {'Baz': 'qux', 'Foo': 'bar'}

    if sys.version_info < (3, 11):
        # Python sorts cookies in order of most specific (ie. longest) path first
        # items with the same path are reversed from response order
        assert info['cookies_string'] == 'Baz=qux; Foo=bar'
    else:
        # Python 3.11 and later preserve the Set-Cookie order.
        # See: https://github.com/python/cpython/pull/22745/
        assert info['cookies_string'] == 'Foo=bar; Baz=qux'

    # The key here has a `-` as opposed to what we see in the `uri` module that converts to `_`
    # Note: this is response order, which differs from cookies_string
    assert info['set-cookie'] == 'Foo=bar, Baz=qux'


def test_fetch_url_nossl(open_url_mock, fake_distronode_module, mocker):
    mocker.patch('distronode.module_utils.urls.get_distribution', return_value='notredhat')

    open_url_mock.side_effect = NoSSLError
    with pytest.raises(FailJson) as excinfo:
        fetch_url(fake_distronode_module, 'http://distronode.khulnasoft.com/')

    assert 'python-ssl' not in excinfo.value.kwargs['msg']

    mocker.patch('distronode.module_utils.urls.get_distribution', return_value='redhat')

    open_url_mock.side_effect = NoSSLError
    with pytest.raises(FailJson) as excinfo:
        fetch_url(fake_distronode_module, 'http://distronode.khulnasoft.com/')

    assert 'python-ssl' in excinfo.value.kwargs['msg']
    assert 'http://distronode.khulnasoft.com/' == excinfo.value.kwargs['url']
    assert excinfo.value.kwargs['status'] == -1


def test_fetch_url_connectionerror(open_url_mock, fake_distronode_module):
    open_url_mock.side_effect = ConnectionError('TESTS')
    with pytest.raises(FailJson) as excinfo:
        fetch_url(fake_distronode_module, 'http://distronode.khulnasoft.com/')

    assert excinfo.value.kwargs['msg'] == 'TESTS'
    assert 'http://distronode.khulnasoft.com/' == excinfo.value.kwargs['url']
    assert excinfo.value.kwargs['status'] == -1

    open_url_mock.side_effect = ValueError('TESTS')
    with pytest.raises(FailJson) as excinfo:
        fetch_url(fake_distronode_module, 'http://distronode.khulnasoft.com/')

    assert excinfo.value.kwargs['msg'] == 'TESTS'
    assert 'http://distronode.khulnasoft.com/' == excinfo.value.kwargs['url']
    assert excinfo.value.kwargs['status'] == -1


def test_fetch_url_httperror(open_url_mock, fake_distronode_module):
    open_url_mock.side_effect = urllib_error.HTTPError(
        'http://distronode.khulnasoft.com/',
        500,
        'Internal Server Error',
        {'Content-Type': 'application/json'},
        StringIO('TESTS')
    )

    r, info = fetch_url(fake_distronode_module, 'http://distronode.khulnasoft.com/')

    assert info == {'msg': 'HTTP Error 500: Internal Server Error', 'body': 'TESTS',
                    'status': 500, 'url': 'http://distronode.khulnasoft.com/', 'content-type': 'application/json'}


def test_fetch_url_urlerror(open_url_mock, fake_distronode_module):
    open_url_mock.side_effect = urllib_error.URLError('TESTS')
    r, info = fetch_url(fake_distronode_module, 'http://distronode.khulnasoft.com/')
    assert info == {'msg': 'Request failed: <urlopen error TESTS>', 'status': -1, 'url': 'http://distronode.khulnasoft.com/'}


def test_fetch_url_socketerror(open_url_mock, fake_distronode_module):
    open_url_mock.side_effect = socket.error('TESTS')
    r, info = fetch_url(fake_distronode_module, 'http://distronode.khulnasoft.com/')
    assert info == {'msg': 'Connection failure: TESTS', 'status': -1, 'url': 'http://distronode.khulnasoft.com/'}


def test_fetch_url_exception(open_url_mock, fake_distronode_module):
    open_url_mock.side_effect = Exception('TESTS')
    r, info = fetch_url(fake_distronode_module, 'http://distronode.khulnasoft.com/')
    exception = info.pop('exception')
    assert info == {'msg': 'An unknown error occurred: TESTS', 'status': -1, 'url': 'http://distronode.khulnasoft.com/'}
    assert "Exception: TESTS" in exception


def test_fetch_url_badstatusline(open_url_mock, fake_distronode_module):
    open_url_mock.side_effect = httplib.BadStatusLine('TESTS')
    r, info = fetch_url(fake_distronode_module, 'http://distronode.khulnasoft.com/')
    assert info == {'msg': 'Connection failure: connection was closed before a valid response was received: TESTS', 'status': -1, 'url': 'http://distronode.khulnasoft.com/'}
