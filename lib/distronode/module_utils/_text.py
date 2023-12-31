# Copyright (c), Toshio Kuratomi <tkuratomi@khulnasoft.com> 2016
# Simplified BSD License (see licenses/simplified_bsd.txt or https://opensource.org/licenses/BSD-2-Clause)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

"""
.. warn:: Use distronode.module_utils.common.text.converters instead.
"""

# Backwards compat for people still calling it from this package
# pylint: disable=unused-import
import codecs

from distronode.module_utils.six import PY3, text_type, binary_type

from distronode.module_utils.common.text.converters import to_bytes, to_native, to_text
