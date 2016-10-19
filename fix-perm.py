#!/usr/bin/env python

"""fix-perm.py - Fix file permissions
"""


from __future__ import print_function

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
        mode = st.st_mode
        os.chmod(path, mode | stat.S_IRUSR | stat.S_IWUSR)
