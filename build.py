#!/usr/bin/env python

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
    for pkg in pkgs:
        print pkg
        os.chdir(localbase)
        assert os.path.exists(os.path.join(localbase, pkg))
        build(pkg)
