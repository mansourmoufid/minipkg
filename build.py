#!/usr/bin/env python

from __future__ import print_function

import os
import subprocess
import sys


def build(pkgpath):
    os.chdir(pkgpath)
    targets = [
        'build',
        'package',
        'install',
        'clean',
        'clean-depends',
    ]
    for target in targets:
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
        assert p.returncode == 0, '%s %s' % (pkg, target)


if __name__ == '__main__':

    home = os.environ['HOME']
    localbase = os.path.join(home, 'usr', 'pkgsrc')

    lines = sys.stdin.readlines()
    pkgs = [line.rstrip('\n') for line in lines]
    pkgpaths = [pkg.split(' ')[0] for pkg in pkgs]
    for pkgpath in pkgpaths:
        print(pkgpath)
        os.chdir(localbase)
        assert os.path.exists(os.path.join(localbase, pkgpath))
        build(pkgpath)
    bindir = os.path.join(localbase, 'pkg', 'bin')
    sbindir = os.path.join(localbase, 'pkg', 'sbin')
    for var in (bindir, sbindir):
        os.environ.update({
            'PATH': var + os.pathsep + os.environ['PATH'],
        })
