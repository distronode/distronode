# (c) 2012-2014, Michael DeHaan <michael.dehaan@gmail.com>
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

from __future__ import annotations

from abc import abstractmethod

from distronode.errors import DistronodeFileNotFound
from distronode.plugins import DistronodePlugin
from distronode.utils.display import Display

display = Display()

__all__ = ['LookupBase']


class LookupBase(DistronodePlugin):

    def __init__(self, loader=None, templar=None, **kwargs):

        super(LookupBase, self).__init__()

        self._loader = loader
        self._templar = templar

        # Backwards compat: self._display isn't really needed, just import the global display and use that.
        self._display = display

    def get_basedir(self, variables):
        if 'role_path' in variables:
            return variables['role_path']
        else:
            return self._loader.get_basedir()

    @staticmethod
    def _flatten(terms):
        ret = []
        for term in terms:
            if isinstance(term, (list, tuple)):
                ret.extend(term)
            else:
                ret.append(term)
        return ret

    @staticmethod
    def _combine(a, b):
        results = []
        for x in a:
            for y in b:
                results.append(LookupBase._flatten([x, y]))
        return results

    @staticmethod
    def _flatten_hash_to_list(terms):
        ret = []
        for key in terms:
            ret.append({'key': key, 'value': terms[key]})
        return ret

    @abstractmethod
    def run(self, terms, variables=None, **kwargs):
        """
        When the playbook specifies a lookup, this method is run.  The
        arguments to the lookup become the arguments to this method.  One
        additional keyword argument named ``variables`` is added to the method
        call.  It contains the variables available to distronode at the time the
        lookup is templated.  For instance::

            "{{ lookup('url', 'https://toshio.fedorapeople.org/one.txt', validate_certs=True) }}"

        would end up calling the lookup plugin named url's run method like this::
            run(['https://toshio.fedorapeople.org/one.txt'], variables=available_variables, validate_certs=True)

        Lookup plugins can be used within playbooks for looping.  When this
        happens, the first argument is a list containing the terms.  Lookup
        plugins can also be called from within playbooks to return their
        values into a variable or parameter.  If the user passes a string in
        this case, it is converted into a list.

        Errors encountered during execution should be returned by raising
        DistronodeError() with a message describing the error.

        Any strings returned by this method that could ever contain non-ascii
        must be converted into python's unicode type as the strings will be run
        through jinja2 which has this requirement.  You can use::

            from distronode.module_utils.common.text.converters import to_text
            result_string = to_text(result_string)
        """
        pass

    def find_file_in_search_path(self, myvars, subdir, needle, ignore_missing=False):
        '''
        Return a file (needle) in the task's expected search path.
        '''

        if 'distronode_search_path' in myvars:
            paths = myvars['distronode_search_path']
        else:
            paths = [self.get_basedir(myvars)]

        result = None
        try:
            result = self._loader.path_dwim_relative_stack(paths, subdir, needle)
        except DistronodeFileNotFound:
            if not ignore_missing:
                self._display.warning("Unable to find '%s' in expected paths (use -vvvvv to see paths)" % needle)

        return result

    def _deprecate_inline_kv(self):
        # TODO: place holder to deprecate in future version allowing for long transition period
        # self._display.deprecated('Passing inline k=v values embedded in a string to this lookup. Use direct ,k=v, k2=v2 syntax instead.', version='2.18')
        pass
