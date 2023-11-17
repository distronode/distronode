# Copyright: (c) 2023, Distronode Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


from distronode.module_utils.six import text_type


class NativeJinjaText(text_type):
    pass
