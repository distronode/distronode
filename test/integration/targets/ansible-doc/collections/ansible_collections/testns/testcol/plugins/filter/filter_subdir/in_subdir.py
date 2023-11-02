# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import annotations

from distronode.utils.display import Display

display = Display()


def nochange(a):
    return a


class FilterModule(object):
    ''' Distronode core jinja2 filters '''

    def filters(self):
        return {
            'noop': nochange,
            'nested': nochange,
        }
