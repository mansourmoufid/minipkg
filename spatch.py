#!/usr/bin/env python

'''spatch.py - apply semantic patches recursively

Usage:
    spatch.py <x.cocci> ... (<dir> | <file>) ...
    spatch.py -h | --help
'''

from __future__ import print_function

import functools
import io
import os
import subprocess
import sys


Popen = functools.partial(subprocess.Popen, universal_newlines=True)

encoding = sys.stdin.encoding


def copy(src, dst):
    with io.open(src, 'rt', encoding=encoding, errors='replace') as x:
        with io.open(dst, 'wt', encoding=encoding) as y:
            for line in x:
                y.write(line)


def ext(x):
    filename = os.path.basename(x)
    return filename.split('.')[-1]


def find(dir):
    for dirpath, dirnames, filenames in os.walk(dir):
        for filename in filenames:
            yield os.path.join(dirpath, filename)
        for dirname in dirnames:
            path = os.path.join(dirpath, dirname)
            yield path
            find(path)


def sed(sp, filename):
    copy(filename, filename + '.orig')
    p = Popen(
        ['sed', '-f', sp, filename + '.orig'],
        stdout=subprocess.PIPE,
    )
    with open(filename, 'wt') as f:
        for line in p.stdout:
            f.write(line)


def cocci(sp, filename):
    copy(filename, filename + '.orig')
    cmd = [
        'spatch',
        '--disable-worth-trying-opt',
        '--in-place',
        '--include-headers',
        '--local-includes',
        '--sp-file', sp,
        '--timeout', '120',
        '--very-quiet',
        filename
    ]
    p = Popen(cmd, stdout=subprocess.PIPE)
    _, _ = p.communicate()


def spatch(sp, filename):
    if not os.path.isfile(filename):
        return
    try:
        tty = open(os.ctermid(), 'w')
    except:
        tty = os.devnull
    w = 80 - 2
    os.chmod(filename, int('644', 8))
    for i in range(100):
        status = u'{}: {} {}'.format(
            os.path.basename(__file__),
            os.path.basename(sp),
            filename
        )
        tty.write(status[:w].ljust(w))
        tty.flush()
        if ext(sp) == 'sed':
            sed(sp, filename)
        if ext(sp) == 'cocci':
            cocci(sp, filename)
        tty.write(u'\r')
        tty.flush()
        p = Popen(
            ['diff', '-u', filename + '.orig', filename],
            stdout=subprocess.PIPE,
        )
        n = 0
        for line in p.stdout:
            sys.stdout.write(line)
            n = n + 1
        if n == 0:
            break
    os.remove(filename + '.orig')
    tty.write(u'\r' + w * ' ' + '\r')
    tty.close()


if __name__ == '__main__':

    os.environ.update(LANG='C')

    if len(sys.argv) == 2 and sys.argv[1] in ('-h', '--help'):
        sys.stdout.write(__doc__)
        sys.exit(os.EX_OK)
    if len(sys.argv) < 2:
        sys.stdout.write(__doc__)
        sys.exit(os.EX_USAGE)

    SPATCH = os.environ.get('SPATCH', '')
    if SPATCH == 'no':
        sys.exit(os.EX_OK)

    exts = []
    if SPATCH == 'all':
        exts += ['sed', 'cocci']
    else:
        exts += SPATCH.split(' ')
    def ispatch(x):
        return os.path.isfile(x) and ext(x) in exts

    def iscode(x):
        return os.path.isfile(x) and ext(x) in ('c', 'h')

    args = sys.argv[1:]
    patches = map(os.path.abspath, filter(ispatch, args))
    paths = map(os.path.abspath, filter(lambda x: not ispatch(x), args))

    for sp in patches:
        for path in paths:
            if os.path.isdir(path):
                os.chdir(path)
                for filename in filter(iscode, find(path)):
                    spatch(sp, filename.lstrip(path))
            else:
                spatch(sp, path)
