#!/usr/bin/env python3

"""fix-rpath.py - Fix run-time search paths

Usage:
    python fix-rpath.py <prefix>
    python fix-rpath.py [-h | --help]
"""


import functools
import os
import platform
import re
import stat
import subprocess
import sys


Popen = functools.partial(subprocess.Popen, universal_newlines=True)


__author__ = 'Mansour Moufid'
__copyright__ = 'Copyright 2015-2025, Mansour Moufid'
__email__ = 'mansourmoufid@gmail.com'
__license__ = 'ISC'
__status__ = 'Development'


def isexe(path):
    p = Popen(
        ['file', path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, _ = p.communicate()
    if not p.returncode == 0:
        return False
    x = out.split(': ')[1]
    return re.match(r'^Mach-O |^ELF ', x) is not None


def islib(path):
    return os.path.isfile(path) and (
        path.endswith('.so') or
        path.endswith('.dylib') or
        path.endswith('.bundle')
    )


def loaded_libs(bin):
    p = Popen(
        ['otool', '-L', bin],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, _ = p.communicate()
    assert p.returncode == 0, 'otool -L %s' % bin
    lines = out.split('\n')
    libs = [
        line.split()[0] for line in lines
        if line and not line.endswith(':')
    ]
    return libs


def issystem(path):
    system_dirs = [
        '/bin',
        '/opt',
        '/usr',
        '/Library',
        '/System',
    ]
    return any(path.startswith(dir) for dir in system_dirs)


def path_strip(prefix, path):
    if not prefix.endswith(os.path.sep):
        prefix += os.path.sep
    return path.split(prefix)[-1]


def set_id_name(lib, id):
    ret = subprocess.call(['install_name_tool', '-id', id, lib])
    assert ret == 0, 'install_name_tool -id %s %s' % (id, lib)


def change_install_name(bin, old, new):
    ret = subprocess.call([
        'install_name_tool',
        '-change', old, new,
        bin,
    ])
    assert ret == 0, 'install_name_tool'


def fix_rpath_lib(prefix, lib):
    set_id_name(lib, re.sub('.*{}'.format(prefix), r'@rpath', lib))


def add_rpath(bin, path):
    p = Popen(
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


def fix_rpath_exe(prefix, exe):
    dir = os.path.split(exe)[0]
    libs = loaded_libs(exe)
    libs = [lib for lib in libs if not issystem(lib)]
    for lib in libs:
        rpath = re.sub('.*{}'.format(prefix), '@rpath', lib)
        change_install_name(exe, lib, rpath)
    add_rpath(exe, prefix)


def relative_path(path, top):
    path = re.sub('.*{}'.format(top), '', path)
    base = path.split(os.path.sep)[:-1]
    dirs = ['..' for dir in base if dir != '']
    return os.path.sep.join(dirs)


def add_rpath_loader_path(destdir, prefix, bin):
    common_prefix = os.path.commonprefix([prefix, re.sub(destdir, '', bin)])
    loader_path = os.path.join(
        '@loader_path',
        relative_path(re.sub(destdir, '', bin), common_prefix),
    )
    add_rpath(bin, loader_path)


if __name__ == '__main__':

    if len(sys.argv) == 3:
        if sys.argv[1] in ('-h', '--help'):
            print(__doc__)
            sys.exit(os.EX_OK)
    else:
        print(__doc__)
        sys.exit(os.EX_USAGE)

    destdir = sys.argv[1]
    prefix = sys.argv[2]
    prefix = os.path.expanduser(prefix)
    prefix = os.path.abspath(prefix)

    system = platform.system()
    supported_systems = ['Darwin']
    if system not in supported_systems:
        print('warning: unsupported system', file=sys.stderr)
        sys.exit(0)

    for line in sys.stdin:
        path = line.rstrip('\n')
        if not os.path.exists(path) or not isexe(path):
            continue
        exe = os.path.abspath(path)
        print(exe)
        mode = os.stat(exe).st_mode
        os.chmod(exe, mode | stat.S_IRUSR | stat.S_IWUSR)
        try:
            if islib(exe):
                fix_rpath_lib(prefix, exe)
            fix_rpath_exe(prefix, exe)
            add_rpath_loader_path(destdir, prefix, exe)
        except AssertionError:
            pass
        os.chmod(exe, mode)
