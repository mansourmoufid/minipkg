#!/usr/bin/env python

from __future__ import print_function

import os
import platform
import subprocess
import sys


__author__ = 'Mansour Moufid'
__copyright__ = 'Copyright 2015, 2016, Mansour Moufid'
__email__ = 'mansourmoufid@gmail.com'
__license__ = 'ISC'
__status__ = 'Development'


home = os.environ['HOME']
system = platform.system()


def bmake(pkgpath, target):
    os.chdir(pkgpath)
    p = subprocess.Popen(
        ['bmake', target],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = p.communicate()
    log = 'bmake-' + target + '-log.txt'
    with open(log, 'w+') as f:
        f.write(out)
        f.write(err)
    assert p.returncode == 0, '%s %s' % (pkgpath, target)
    try:
        os.remove(log)
    except OSError:
        pass


def find(dir, type=None, name=None):
    if type is None:
        type = 'f'
    if name is None:
        name = '*'
    p = subprocess.Popen(
        ['find', dir, '-type', type, '-name', name],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = p.communicate()
    assert p.returncode == 0, 'find'
    lines = out.split('\n')
    files = [line for line in lines if line]
    return files


def wrksrc(pkgpath):
    os.chdir(pkgpath)
    p = subprocess.Popen(
        ['bmake', 'show-var', 'VARNAME=WRKSRC'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, _ = p.communicate()
    assert p.returncode == 0
    dir = out.rstrip('\n')
    return dir


def build(pkgpath):
    os.chdir(pkgpath)
    targets = [
        'clean',
        'build',
        'package',
        'install',
        'clean',
    ]
    for target in targets:
        bmake(pkgpath, target)


def pkg_info(pkgnames):
    p = subprocess.Popen(
        ['pkg_info', '-X'] + pkgnames,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, _ = p.communicate()
    assert p.returncode == 0, 'pkg_info'
    info = out.split('\n')
    info = [s for s in info if 'REQUIRES=' not in s]
    info = [s for s in info if 'PROVIDES=' not in s]
    return info


if __name__ == '__main__':

    localbase = os.path.join(home, 'usr', 'pkgsrc')
    library_path = os.path.join(home, 'pkg', 'lib')
    if system == 'Darwin':
        os.environ.update({
            'DYLD_LIBRARY_PATH': library_path,
        })
    if system == 'Linux':
        os.environ.update({
            'LD_LIBRARY_PATH': library_path,
        })

    lines = sys.stdin.readlines()
    pkgs = [line.rstrip('\n') for line in lines]
    pkgs = [pkg for pkg in pkgs if pkg]
    pkgpaths = [pkg.split(' ')[0] for pkg in pkgs]
    for pkgpath in pkgpaths:
        print(pkgpath)
        pkgpath = os.path.join(localbase, pkgpath)
        build(pkgpath)
    os.environ.update({
        'PATH': os.pathsep.join([
            os.path.join(home, 'pkg', 'bin'),
            os.path.join(home, 'pkg', 'sbin'),
            os.environ.get('PATH', ''),
        ]),
    })

    pkgnames = [
        pkg.split(' ')[1] if ' ' in pkg else pkg.split('/')[1]
        for pkg in pkgs
    ]
    info = pkg_info(pkgnames)
    pkg_summary = os.path.join(localbase, 'packages', 'pkg_summary')
    try:
        os.remove(pkg_summary + '.gz')
    except OSError:
        pass
    with open(pkg_summary, 'w+') as f:
        print('\n'.join(info), file=f)
    ret = subprocess.call(['gzip', pkg_summary])
    assert ret == 0, 'gzip %s' % (pkg_summary)
