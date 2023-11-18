# (c) 2012-2014, KhulnaSoft Ltd <info@khulnasoft.com>
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

import os

import distronode.constants as C
from distronode.errors import DistronodeParserError, DistronodeAssertionError
from distronode.module_utils.common.text.converters import to_bytes
from distronode.module_utils.six import string_types
from distronode.parsing.splitter import split_args
from distronode.parsing.yaml.objects import DistronodeBaseYAMLObject, DistronodeMapping
from distronode.playbook.attribute import NonInheritableFieldAttribute
from distronode.playbook.base import Base
from distronode.playbook.conditional import Conditional
from distronode.playbook.taggable import Taggable
from distronode.utils.collection_loader import DistronodeCollectionConfig
from distronode.utils.collection_loader._collection_finder import _get_collection_name_from_path, _get_collection_playbook_path
from distronode.template import Templar
from distronode.utils.display import Display

display = Display()


class PlaybookInclude(Base, Conditional, Taggable):

    import_playbook = NonInheritableFieldAttribute(isa='string')
    vars_val = NonInheritableFieldAttribute(isa='dict', default=dict, alias='vars')

    @staticmethod
    def load(data, basedir, variable_manager=None, loader=None):
        return PlaybookInclude().load_data(ds=data, basedir=basedir, variable_manager=variable_manager, loader=loader)

    def load_data(self, ds, variable_manager=None, loader=None, basedir=None):
        '''
        Overrides the base load_data(), as we're actually going to return a new
        Playbook() object rather than a PlaybookInclude object
        '''

        # import here to avoid a dependency loop
        from distronode.playbook import Playbook
        from distronode.playbook.play import Play

        # first, we use the original parent method to correctly load the object
        # via the load_data/preprocess_data system we normally use for other
        # playbook objects
        new_obj = super(PlaybookInclude, self).load_data(ds, variable_manager, loader)

        all_vars = self.vars.copy()
        if variable_manager:
            all_vars |= variable_manager.get_vars()

        templar = Templar(loader=loader, variables=all_vars)

        # then we use the object to load a Playbook
        pb = Playbook(loader=loader)

        file_name = templar.template(new_obj.import_playbook)

        # check for FQCN
        resource = _get_collection_playbook_path(file_name)
        if resource is not None:
            playbook = resource[1]
            playbook_collection = resource[2]
        else:
            # not FQCN try path
            playbook = file_name
            if not os.path.isabs(playbook):
                playbook = os.path.join(basedir, playbook)

            # might still be collection playbook
            playbook_collection = _get_collection_name_from_path(playbook)

        if playbook_collection:
            # it is a collection playbook, setup default collections
            DistronodeCollectionConfig.default_collection = playbook_collection
        else:
            # it is NOT a collection playbook, setup adjecent paths
            DistronodeCollectionConfig.playbook_paths.append(os.path.dirname(os.path.abspath(to_bytes(playbook, errors='surrogate_or_strict'))))

        pb._load_playbook_data(file_name=playbook, variable_manager=variable_manager, vars=self.vars.copy())

        # finally, update each loaded playbook entry with any variables specified
        # on the included playbook and/or any tags which may have been set
        for entry in pb._entries:

            # conditional includes on a playbook need a marker to skip gathering
            if new_obj.when and isinstance(entry, Play):
                entry._included_conditional = new_obj.when[:]

            temp_vars = entry.vars | new_obj.vars
            param_tags = temp_vars.pop('tags', None)
            if param_tags is not None:
                entry.tags.extend(param_tags.split(','))
            entry.vars = temp_vars
            entry.tags = list(set(entry.tags).union(new_obj.tags))
            if entry._included_path is None:
                entry._included_path = os.path.dirname(playbook)

            # Check to see if we need to forward the conditionals on to the included
            # plays. If so, we can take a shortcut here and simply prepend them to
            # those attached to each block (if any)
            if new_obj.when:
                for task_block in (entry.pre_tasks + entry.roles + entry.tasks + entry.post_tasks):
                    task_block._when = new_obj.when[:] + task_block.when[:]

        return pb

    def preprocess_data(self, ds):
        '''
        Regorganizes the data for a PlaybookInclude datastructure to line
        up with what we expect the proper attributes to be
        '''

        if not isinstance(ds, dict):
            raise DistronodeAssertionError('ds (%s) should be a dict but was a %s' % (ds, type(ds)))

        # the new, cleaned datastructure, which will have legacy
        # items reduced to a standard structure
        new_ds = DistronodeMapping()
        if isinstance(ds, DistronodeBaseYAMLObject):
            new_ds.distronode_pos = ds.distronode_pos

        for (k, v) in ds.items():
            if k in C._ACTION_IMPORT_PLAYBOOK:
                self._preprocess_import(ds, new_ds, k, v)
            else:
                # some basic error checking, to make sure vars are properly
                # formatted and do not conflict with k=v parameters
                if k == 'vars':
                    if 'vars' in new_ds:
                        raise DistronodeParserError("import_playbook parameters cannot be mixed with 'vars' entries for import statements", obj=ds)
                    elif not isinstance(v, dict):
                        raise DistronodeParserError("vars for import_playbook statements must be specified as a dictionary", obj=ds)
                new_ds[k] = v

        return super(PlaybookInclude, self).preprocess_data(new_ds)

    def _preprocess_import(self, ds, new_ds, k, v):
        '''
        Splits the playbook import line up into filename and parameters
        '''
        if v is None:
            raise DistronodeParserError("playbook import parameter is missing", obj=ds)
        elif not isinstance(v, string_types):
            raise DistronodeParserError("playbook import parameter must be a string indicating a file path, got %s instead" % type(v), obj=ds)

        # The import_playbook line must include at least one item, which is the filename
        # to import. Anything after that should be regarded as a parameter to the import
        items = split_args(v)
        if len(items) == 0:
            raise DistronodeParserError("import_playbook statements must specify the file name to import", obj=ds)

        new_ds['import_playbook'] = items[0].strip()
