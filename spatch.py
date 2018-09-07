#!/usr/bin/env python


from __future__ import print_function

import functools
import multiprocessing
import os
import signal
import subprocess
import sys


Popen = functools.partial(subprocess.Popen, universal_newlines=True)

Popen_stdout = functools.partial(Popen, stdout=subprocess.PIPE)


def find(dirs):
    p = Popen_stdout(['find', '-L'] + dirs)
    for line in p.stdout.readlines():
        path = line.rstrip('\n')
        if not os.path.isfile(path):
            continue
        yield path


def ext(path):
    return path.split('.')[-1]


def sed_cmd(path):
    return ['sed', '-f', path]


def spatch_cmd(path):
    return [
        'spatch',
        '--very-quiet',
        '--timeout', '120',
        '--in-place',
        '--include-headers',
        '--local-includes',
        '--disable-worth-trying-opt',
        '--sp-file', path,
    ]


def patch_file(sp, _f):
    os.chmod(_f, int('644', 8))
    for i in range(100):
        subprocess.check_call(['cp', _f, _f + '.orig'])
        if ext(sp) == 'sed':
            p = Popen_stdout(sed_cmd(sp) + [_f + '.orig'])
            with open(_f, 'w') as f:
                for line in p.stdout.readlines():
                    f.write(line)
        if ext(sp) == 'cocci':
            p = Popen_stdout(spatch_cmd(sp) + [_f])
            _, _ = p.communicate()
        p = Popen_stdout(['diff', '-u', _f + '.orig', _f])
        n = 0
        for line in p.stdout.readlines():
            sys.stdout.write(line)
            n += 1
        if n == 0:
            break
    os.remove(_f + '.orig')


if __name__ == '__main__':

    os.environ.update(LANG='C')

    spatch = os.environ.get('SPATCH', '')
    localpatches = os.environ.get('LOCALPATCHES')
    pkgpath = os.environ.get('PKGPATH')
    spatches = os.environ.get('SPATCHES')
    wrksrc = os.environ.get('WRKSRC')

    if spatch == 'yes':
        exts = ['sed', 'cocci']
    elif spatch == 'no':
        exts = []
    else:
        exts = spatch.split()
    patches = find([spatches, os.path.join(localpatches, pkgpath)])
    patches = filter(lambda f: ext(f) in exts, patches)
    patches.sort(key=os.path.basename)
    files = find([wrksrc])
    files = filter(lambda f: ext(f) in ('c', 'h'), files)

    signal.signal(signal.SIGINT, signal.SIG_IGN)
    pool = multiprocessing.Pool(4)
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    for sp in patches:
        pf = functools.partial(patch_file, sp)
        try:
            pool.map(pf, files)
        except KeyboardInterrupt:
            pool.terminate()
