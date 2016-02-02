#!/usr/bin/env python

"""depends.py - print package dependencies

Usage: python depends.py [-h | --help]
"""


from __future__ import print_function

import os
import subprocess
import sys


def depends(home, pkgpath):
    os.chdir(os.path.join(home, 'usr', 'pkgsrc'))
    os.chdir(pkgpath)
    p = subprocess.Popen(
        ['bmake', 'show-depends-pkgpaths'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = p.communicate()
    assert p.returncode == 0, 'bmake show-depends-pkgpaths'
    lines = out.split('\n')
    deps = [line for line in lines if line]
    return deps


def all_depends(home, pkgs):
    if pkgs == []:
        return []
    else:
        pkg = pkgs.pop(0)
        deps = depends(home, pkg)
        return [pkg] + all_depends(home, deps + pkgs)


if __name__ == '__main__':

    if len(sys.argv) == 1:
        pass
    elif len(sys.argv) == 2 and sys.argv[1] in ('-h', '--help'):
        print(__doc__)
        sys.exit(os.EX_OK)
    else:
        print(__doc__)
        sys.exit(os.EX_USAGE)

    home = os.environ['HOME']

    lines = sys.stdin.readlines()
    pkgs = [line.rstrip('\n') for line in lines]
    pkgs = [pkg for pkg in pkgs if pkg]

    deps = []
    for dep in reversed(all_depends(home, pkgs)):
        if dep not in deps:
            deps.append(dep)
            print(dep)
