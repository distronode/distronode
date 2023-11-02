# (c) 2017, Matt Martz <matt@sivel.net>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import annotations

import functools

from distronode.plugins.inventory.toml import HAS_TOML, toml_dumps
try:
    from distronode.plugins.inventory.toml import toml
except ImportError:
    pass

from distronode.errors import DistronodeFilterError
from distronode.module_utils.common.text.converters import to_text
from distronode.module_utils.common._collections_compat import MutableMapping
from distronode.module_utils.six import string_types


def _check_toml(func):
    @functools.wraps(func)
    def inner(o):
        if not HAS_TOML:
            raise DistronodeFilterError('The %s filter plugin requires the python "toml" library' % func.__name__)
        return func(o)
    return inner


@_check_toml
def from_toml(o):
    if not isinstance(o, string_types):
        raise DistronodeFilterError('from_toml requires a string, got %s' % type(o))
    return toml.loads(to_text(o, errors='surrogate_or_strict'))


@_check_toml
def to_toml(o):
    if not isinstance(o, MutableMapping):
        raise DistronodeFilterError('to_toml requires a dict, got %s' % type(o))
    return to_text(toml_dumps(o), errors='surrogate_or_strict')


class FilterModule(object):
    def filters(self):
        return {
            'to_toml': to_toml,
            'from_toml': from_toml
        }