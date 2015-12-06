#!/usr/bin/env python

"""minipkg.py - install pkgsrc

Usage: python minipkg.py [-h | --help] [-v | --version]
"""


from __future__ import print_function
import os
import subprocess
import sys
import urllib2


__author__ = 'Mansour Moufid'
__copyright__ = 'Copyright 2015, Mansour Moufid'
__email__ = 'mansourmoufid@gmail.com'
__license__ = 'ISC'
__status__ = 'Development'
__version__ = '0.1'


if __name__ == '__main__':

    assert len(sys.argv) in (1, 2)
    if len(sys.argv) == 1:
        pass
    elif len(sys.argv) == 2:
        if sys.argv[1] in ('-h', '--help'):
            print(__doc__)
            sys.exit(os.EX_OK)
        elif sys.argv[1] in ('-v', '--version'):
            print('minipkg version', __version__)
            sys.exit(os.EX_OK)
        else:
            print(__doc__)
            sys.exit(os.EX_USAGE)

    # Determine some information about the machine.
    supported_sys = ('Linux', 'Darwin')
    supported_mach = {
        'i386': '32',
        'x86_64': '64',
    }
    default_compiler = {
        'Linux': 'gcc',
        'Darwin': 'clang',
    }
    HOME = os.environ['HOME']
    p = subprocess.Popen(['uname', '-ms'], stdout=subprocess.PIPE)
    p.wait()
    assert p.returncode == 0, 'uname'
    (sys, mach) = p.stdout.read().split()
    assert sys in supported_sys, 'unsupported system'
    assert mach in supported_mach, 'unsupported architecture'
    OPSYS = sys
    ABI = supported_mach[mach]
    CC = os.environ.get('CC', None) or default_compiler[OPSYS]
    print('minipkg: HOME:', HOME)
    print('minipkg: OPSYS:', OPSYS)
    print('minipkg: ABI:', ABI)
    print('minipkg: CC:', CC)

    # Fetch the pkgsrc archive.
    url = 'http://ftp.netbsd.org/pub/pkgsrc/stable/pkgsrc-2015Q3.tar.gz'
    tgz = os.path.basename(url)
    print('minipkg: fetching', tgz, '...')
    if not os.path.exists(tgz):
        req = urllib2.Request(url)
        res = urllib2.urlopen(req)
        dat = res.read()
        with open(tgz, 'wb') as f:
            f.write(dat)

    # Extract the pkgsrc archive.
    print('minipkg: extracting', tgz, '...')
    home_usr = os.path.join(HOME, 'usr')
    if not os.path.exists(home_usr):
        err = subprocess.call(['gunzip', tgz])
        assert err == 0, 'gunzip'
        tar = tgz.rstrip('.gz')
        os.mkdir(home_usr)
        err = subprocess.call(['tar', '-xf', tar, '-C', home_usr])
        assert err == 0, 'tar'

    # Bootstrap pkgsrc.
    print('minipkg: bootstrapping ...')
    sh = os.environ['SH']
    sh = sh.split(os.pathsep)[0]
    if not sh:
        sh = '/bin/bash'
    assert os.path.exists(sh), sh
    os.putenv('SH', sh)
    bootstrap_path = os.path.join(HOME, 'usr', 'pkgsrc', 'bootstrap')
    if not os.path.exists(os.path.join(bootstrap_path, 'work')):
        os.chdir(bootstrap_path)
        log = os.path.join(HOME, 'pkgsrc-bootstrap-log.txt')
        with open(log, 'w') as f:
            p = subprocess.Popen(
                [
                    './bootstrap',
                    '--unprivileged',
                    '--abi', ABI,
                    '--compiler', CC,
                    '--make-jobs', '4',
                ],
                stdout=f,
                stderr=f,
            )
            p.wait()
        assert p.returncode == 0, 'bootstrap'

    # Set environment variables.
    print('minipkg: setting environment variables ...')
    vars = [
        ('PATH', '$HOME/pkg/bin'),
        ('PATH', '$HOME/pkg/sbin'),
        ('MANPATH', '$HOME/pkg/man'),
        ('SH', sh),
    ]
    script = [
        'export %s="%s:$%s"' % (key, val, key)
        for (key, val) in vars
    ]
    profile = os.path.join(HOME, '.profile')
    with open(profile, 'a') as f:
        for line in script:
            f.write(line + '\n')

    print('minipkg: done!')
