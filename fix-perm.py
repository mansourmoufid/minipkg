#!/usr/bin/env python

"""fix-perm.py - Fix file permissions
"""


from __future__ import print_function

import io
import os
import stat
import sys


if __name__ == '__main__':

    for line in sys.stdin:
        path = line.rstrip('\n')
        if path == '':
            continue
        if not os.path.isfile(path):
            continue
        st = os.stat(path)
        mode = int('644', 8)
        if st.st_mode & stat.S_IXUSR != 0:
            mode = int('755', 8)
        with io.open(path, 'rb') as f:
            x = f.read(2)
            if x == b'#!':
                mode = int('755', 8)
        os.chmod(path, mode)
