#!/usr/bin/env python

"""fix-rpath.py - Fix run-time search paths

Usage:
    python fix-rpath.py <prefix>
    python fix-rpath.py [-h | --help]
"""


from __future__ import print_function

import os
import platform
import re
import stat
import subprocess
import sys


__author__ = 'Mansour Moufid'
__copyright__ = 'Copyright 2015, 2016, Mansour Moufid'
__email__ = 'mansourmoufid@gmail.com'
__license__ = 'ISC'
__status__ = 'Development'


def isexe(exe_pat, path):
    p = subprocess.Popen(
        ['file', path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, _ = p.communicate()
    if not p.returncode == 0:
        return False
    type = out.split(': ')[1]
    return exe_pat.match(type) is not None


def islib(path):
    return os.path.isfile(path) and (
        path.endswith('.so') or
        path.endswith('.dylib')
    )


def install_names(bin):
    p = subprocess.Popen(
        ['otool', '-L', bin],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, _ = p.communicate()
    assert p.returncode == 0, 'otool -L %s' % bin
    lines = out.split('\n')
    names = [
        line.split()[0] for line in lines
        if line and not line.endswith(':')
    ]
    return names


def issystem(path):
    system_dirs = [
        '/bin',
        '/opt',
        '/usr',
        '/Library',
        '/System',
    ]
    return any(path.startswith(dir) for dir in system_dirs)


def path_strip(path, prefix):
    if not prefix.endswith(os.path.sep):
        prefix += os.path.sep
    if path.startswith(prefix):
        return path[len(prefix):]
    return path


def change_id_name(lib, id):
    ret = subprocess.call(['install_name_tool', '-id', id, lib])
    assert ret == 0, 'install_name_tool -id %s %s' % (id, lib)


def change_install_name(bin, old, new):
    ret = subprocess.call([
        'install_name_tool',
        '-change', old, new,
        bin,
    ])
    assert ret == 0, 'install_name_tool'


def fix_rpath_lib(lib):
    basename = os.path.basename(lib)
    rpath = os.path.join('@rpath', basename)
    change_id_name(lib, rpath)


def fix_rpath_exe(prefix, exe):
    names = install_names(exe)
    names = [name for name in names if not issystem(name)]
    for name in names:
        basename = path_strip(name, os.path.join(prefix, 'lib'))
        basename = path_strip(basename, '@rpath')
        rpath = os.path.join('@rpath', basename)
        change_install_name(exe, name, rpath)


def add_rpath(bin, path):
    p = subprocess.Popen(
        ['install_name_tool', '-delete_rpath', path, bin],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    p.wait()
    ret = subprocess.call([
        'install_name_tool',
        '-add_rpath', path,
        bin,
    ])
    assert ret == 0, 'install_name_tool'


def add_rpath_loader_path(bin):
    loader_path = os.path.join('@loader_path', '..', 'lib')
    add_rpath(bin, loader_path)


if __name__ == '__main__':

    if len(sys.argv) == 2:
        if sys.argv[1] in ('-h', '--help'):
            print(__doc__)
            sys.exit(os.EX_OK)
    else:
        print(__doc__)
        sys.exit(os.EX_USAGE)

    prefix = sys.argv[1]
    prefix = os.path.expanduser(prefix)
    prefix = os.path.abspath(prefix)

    system = platform.system()
    supported_systems = ['Darwin']
    if system not in supported_systems:
        print('warning: unsupported system', file=sys.stderr)
        sys.exit(0)
    system_exe_pat = {
        'Darwin': 'Mach-O( .*)? (executable|shared library)',
    }
    exe_pat = re.compile(system_exe_pat[system])

    lines = sys.stdin.readlines()
    paths = (line.rstrip('\n') for line in lines)
    paths = (path for path in paths if os.path.exists(path))

    exes = (path for path in paths if isexe(exe_pat, path))
    for exe in exes:
        print(exe)
        mode = os.stat(exe).st_mode
        os.chmod(exe, mode | stat.S_IRUSR | stat.S_IWUSR)
        if islib(exe):
            fix_rpath_lib(exe)
        fix_rpath_exe(prefix, exe)
        add_rpath_loader_path(exe)
        os.chmod(exe, mode)
