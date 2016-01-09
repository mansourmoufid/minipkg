#!/usr/bin/env python

from __future__ import print_function

import os
import subprocess
import sys


__author__ = 'Mansour Moufid'
__copyright__ = 'Copyright 2015, 2016, Mansour Moufid'
__email__ = 'mansourmoufid@gmail.com'
__license__ = 'ISC'
__status__ = 'Development'


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


def build(home, pkgpath):
    targets = [
        'build',
        'package',
        'install',
        'clean',
        'clean-depends',
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

    home = os.environ['HOME']
    localbase = os.path.join(home, 'usr', 'pkgsrc')

    lines = sys.stdin.readlines()
    pkgs = [line.rstrip('\n') for line in lines]
    pkgpaths = [pkg.split(' ')[0] for pkg in pkgs]
    for pkgpath in pkgpaths:
        print(pkgpath)
        pkgpath = os.path.join(localbase, pkgpath)
        os.chdir(pkgpath)
        build(home, pkgpath)
    bindir = os.path.join(localbase, 'pkg', 'bin')
    sbindir = os.path.join(localbase, 'pkg', 'sbin')
    for var in (bindir, sbindir):
        os.environ.update({
            'PATH': var + os.pathsep + os.environ['PATH'],
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
    p = subprocess.Popen(
        ['gzip', pkg_summary],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = p.communicate()
    assert p.returncode == 0, 'gzip'
