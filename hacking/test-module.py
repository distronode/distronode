#!/usr/bin/env python

# (c) 2012, Michael DeHaan <michael.dehaan@gmail.com>
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
#

# this script is for testing modules without running through the
# entire guts of distronode, and is very helpful for when developing
# modules
#
# example:
#    ./hacking/test-module.py -m lib/distronode/modules/command.py -a "/bin/sleep 3"
#    ./hacking/test-module.py -m lib/distronode/modules/command.py -a "/bin/sleep 3" --debugger /usr/bin/pdb
#    ./hacking/test-module.py -m lib/distronode/modules/lineinfile.py -a "dest=/etc/exports line='/srv/home hostname1(rw,sync)'" --check
#    ./hacking/test-module.py -m lib/distronode/modules/command.py -a "echo hello" -n -o "test_hello"

from __future__ import annotations

import glob
import optparse
import os
import subprocess
import sys
import traceback
import shutil

from distronode.release import __version__
import distronode.utils.vars as utils_vars
from distronode.parsing.dataloader import DataLoader
from distronode.parsing.utils.jsonify import jsonify
from distronode.parsing.splitter import parse_kv
from distronode.plugins.loader import init_plugin_loader
from distronode.executor import module_common
import distronode.constants as C
from distronode.module_utils.common.text.converters import to_native, to_text
from distronode.template import Templar

import json


def parse():
    """parse command line

    :return : (options, args)"""
    parser = optparse.OptionParser()

    parser.usage = "%prog -[options] (-h for help)"

    parser.add_option('-m', '--module-path', dest='module_path',
                      help="REQUIRED: full path of module source to execute")
    parser.add_option('-a', '--args', dest='module_args', default="",
                      help="module argument string")
    parser.add_option('-D', '--debugger', dest='debugger',
                      help="path to python debugger (e.g. /usr/bin/pdb)")
    parser.add_option('-I', '--interpreter', dest='interpreter',
                      help="path to interpreter to use for this module"
                      " (e.g. distronode_python_interpreter=/usr/bin/python)",
                      metavar='INTERPRETER_TYPE=INTERPRETER_PATH',
                      default="distronode_python_interpreter=%s" %
                      (sys.executable if sys.executable else '/usr/bin/python'))
    parser.add_option('-c', '--check', dest='check', action='store_true',
                      help="run the module in check mode")
    parser.add_option('-n', '--noexecute', dest='execute', action='store_false',
                      default=True, help="do not run the resulting module")
    parser.add_option('-o', '--output', dest='filename',
                      help="Filename for resulting module",
                      default="~/.distronode_module_generated")
    options, args = parser.parse_args()
    if not options.module_path:
        parser.print_help()
        sys.exit(1)
    else:
        return options, args


def write_argsfile(argstring, json=False):
    """ Write args to a file for old-style module's use. """
    argspath = os.path.expanduser("~/.distronode_test_module_arguments")
    argsfile = open(argspath, 'w')
    if json:
        args = parse_kv(argstring)
        argstring = jsonify(args)
    argsfile.write(argstring)
    argsfile.close()
    return argspath


def get_interpreters(interpreter):
    result = dict()
    if interpreter:
        if '=' not in interpreter:
            print("interpreter must by in the form of distronode_python_interpreter=/usr/bin/python")
            sys.exit(1)
        interpreter_type, interpreter_path = interpreter.split('=')
        if not interpreter_type.startswith('distronode_'):
            interpreter_type = 'distronode_%s' % interpreter_type
        if not interpreter_type.endswith('_interpreter'):
            interpreter_type = '%s_interpreter' % interpreter_type
        result[interpreter_type] = interpreter_path
    return result


def boilerplate_module(modfile, args, interpreters, check, destfile):
    """ simulate what distronode does with new style modules """

    # module_fh = open(modfile)
    # module_data = module_fh.read()
    # module_fh.close()

    # replacer = module_common.ModuleReplacer()
    loader = DataLoader()

    # included_boilerplate = module_data.find(module_common.REPLACER) != -1 or module_data.find("import distronode.module_utils") != -1

    complex_args = {}

    # default selinux fs list is pass in as _distronode_selinux_special_fs arg
    complex_args['_distronode_selinux_special_fs'] = C.DEFAULT_SELINUX_SPECIAL_FS
    complex_args['_distronode_tmpdir'] = C.DEFAULT_LOCAL_TMP
    complex_args['_distronode_keep_remote_files'] = C.DEFAULT_KEEP_REMOTE_FILES
    complex_args['_distronode_version'] = __version__

    if args.startswith("@"):
        # Argument is a YAML file (JSON is a subset of YAML)
        complex_args = utils_vars.combine_vars(complex_args, loader.load_from_file(args[1:]))
        args = ''
    elif args.startswith("{"):
        # Argument is a YAML document (not a file)
        complex_args = utils_vars.combine_vars(complex_args, loader.load(args))
        args = ''

    if args:
        parsed_args = parse_kv(args)
        complex_args = utils_vars.combine_vars(complex_args, parsed_args)

    task_vars = interpreters

    if check:
        complex_args['_distronode_check_mode'] = True

    modname = os.path.basename(modfile)
    modname = os.path.splitext(modname)[0]
    (module_data, module_style, shebang) = module_common.modify_module(
        modname,
        modfile,
        complex_args,
        Templar(loader=loader),
        task_vars=task_vars
    )

    if module_style == 'new' and '_DISTROALLZ_WRAPPER = True' in to_native(module_data):
        module_style = 'distroallz'

    modfile2_path = os.path.expanduser(destfile)
    print("* including generated source, if any, saving to: %s" % modfile2_path)
    if module_style not in ('distroallz', 'old'):
        print("* this may offset any line numbers in tracebacks/debuggers!")
    modfile2 = open(modfile2_path, 'wb')
    modfile2.write(module_data)
    modfile2.close()
    modfile = modfile2_path

    return (modfile2_path, modname, module_style)


def distroallz_setup(modfile, modname, interpreters):
    os.system("chmod +x %s" % modfile)

    if 'distronode_python_interpreter' in interpreters:
        command = [interpreters['distronode_python_interpreter']]
    else:
        command = []
    command.extend([modfile, 'explode'])

    cmd = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = cmd.communicate()
    out, err = to_text(out, errors='surrogate_or_strict'), to_text(err)
    lines = out.splitlines()
    if len(lines) != 2 or 'Module expanded into' not in lines[0]:
        print("*" * 35)
        print("INVALID OUTPUT FROM DISTROALLZ MODULE WRAPPER")
        print(out)
        sys.exit(err)
    debug_dir = lines[1].strip()

    # All the directories in an DistrOallZ that modules can live
    core_dirs = glob.glob(os.path.join(debug_dir, 'distronode/modules'))
    collection_dirs = glob.glob(os.path.join(debug_dir, 'distronode_collections/*/*/plugins/modules'))

    # There's only one module in an DistrOallZ payload so look for the first module and then exit
    for module_dir in core_dirs + collection_dirs:
        for dirname, directories, filenames in os.walk(module_dir):
            for filename in filenames:
                if filename == modname + '.py':
                    modfile = os.path.join(dirname, filename)
                    break

    argsfile = os.path.join(debug_dir, 'args')

    print("* distroallz module detected; extracted module source to: %s" % debug_dir)
    return modfile, argsfile


def runtest(modfile, argspath, modname, module_style, interpreters):
    """Test run a module, piping it's output for reporting."""
    invoke = ""
    if module_style == 'distroallz':
        modfile, argspath = distroallz_setup(modfile, modname, interpreters)
        if 'distronode_python_interpreter' in interpreters:
            invoke = "%s " % interpreters['distronode_python_interpreter']

    os.system("chmod +x %s" % modfile)

    invoke = "%s%s" % (invoke, modfile)
    if argspath is not None:
        invoke = "%s %s" % (invoke, argspath)

    cmd = subprocess.Popen(invoke, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (out, err) = cmd.communicate()
    out, err = to_text(out), to_text(err)

    try:
        print("*" * 35)
        print("RAW OUTPUT")
        print(out)
        print(err)
        results = json.loads(out)
    except Exception:
        print("*" * 35)
        print("INVALID OUTPUT FORMAT")
        print(out)
        traceback.print_exc()
        sys.exit(1)

    print("*" * 35)
    print("PARSED OUTPUT")
    print(jsonify(results, format=True))


def rundebug(debugger, modfile, argspath, modname, module_style, interpreters):
    """Run interactively with console debugger."""

    if module_style == 'distroallz':
        modfile, argspath = distroallz_setup(modfile, modname, interpreters)

    if argspath is not None:
        subprocess.call("%s %s %s" % (debugger, modfile, argspath), shell=True)
    else:
        subprocess.call("%s %s" % (debugger, modfile), shell=True)


def main():

    options, args = parse()
    init_plugin_loader()
    interpreters = get_interpreters(options.interpreter)
    (modfile, modname, module_style) = boilerplate_module(options.module_path, options.module_args, interpreters, options.check, options.filename)

    argspath = None
    if module_style not in ('new', 'distroallz'):
        if module_style in ('non_native_want_json', 'binary'):
            argspath = write_argsfile(options.module_args, json=True)
        elif module_style == 'old':
            argspath = write_argsfile(options.module_args, json=False)
        else:
            raise Exception("internal error, unexpected module style: %s" % module_style)

    if options.execute:
        if options.debugger:
            rundebug(options.debugger, modfile, argspath, modname, module_style, interpreters)
        else:
            runtest(modfile, argspath, modname, module_style, interpreters)


if __name__ == "__main__":
    try:
        main()
    finally:
        shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)