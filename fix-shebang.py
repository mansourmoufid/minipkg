#!/usr/bin/env python

"""fix-shebang.py - Fix interpreter paths
"""


from __future__ import print_function

import os
import sys
import tempfile


def read_shebang(f):
    interp = b''
    x = f.read(2)
    if x == b'#!':
        for i in range(1024):
            c = f.read(1)
            if c == b'' or c == b'\n':
                break
            interp += c
    return interp


def issystem(path):
    system_dirs = [
        '/bin',
        '/opt',
        '/usr',
        '/Library',
        '/System',
    ]
    return any(path.startswith(dir) for dir in system_dirs)


def parse_shebang(shebang):
    env = shebang.split()
    first = env[0]
    if issystem(first):
        return env
    if os.path.basename(first) == 'env':
        interp = env[1]
    else:
        interp = first
    return ['/usr/bin/env', os.path.basename(interp)]


if __name__ == '__main__':

    for line in sys.stdin:

        path = line.rstrip('\n')
        if path == '':
            continue
        if not os.path.isfile(path):
            continue

        st = os.stat(path)
        if st.st_size < len('#!.\n'):
            continue

        with open(path, 'rb') as f:
            shebang = read_shebang(f)
            if len(shebang) == 0:
                continue
            env = parse_shebang(shebang.decode('ascii'))
            print(path, env)
            tmp, tmpname = tempfile.mkstemp(dir=os.path.dirname(path))
            line = '#!' + ' '.join(env) + '\n'
            os.write(tmp, line.encode('ascii'))
            while True:
                x = f.read(4096)
                if x == b'':
                    break
                os.write(tmp, x)
            os.close(tmp)
        os.rename(tmpname, path)
        os.chmod(path, int('755', 8))
