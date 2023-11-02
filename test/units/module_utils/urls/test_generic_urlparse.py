# -*- coding: utf-8 -*-
# (c) 2018 Matt Martz <matt@sivel.net>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import annotations

from distronode.module_utils.urls import generic_urlparse
from distronode.module_utils.six.moves.urllib.parse import urlparse, urlunparse


def test_generic_urlparse():
    url = 'https://distronode.github.io/blog'
    parts = urlparse(url)
    generic_parts = generic_urlparse(parts)
    assert generic_parts.as_list() == list(parts)

    assert urlunparse(generic_parts.as_list()) == url


def test_generic_urlparse_netloc():
    url = 'https://distronode.github.io:443/blog'
    parts = urlparse(url)
    generic_parts = generic_urlparse(parts)
    assert generic_parts.hostname == parts.hostname
    assert generic_parts.hostname == 'distronode.github.io'
    assert generic_parts.port == 443
    assert urlunparse(generic_parts.as_list()) == url
