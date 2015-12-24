#!/usr/bin/env python

"""minipkg.py - install pkgsrc

Usage: python minipkg.py [-h | --help] [-v | --version]
"""


from __future__ import print_function
import hashlib
import os
import subprocess
import sys
try:
    from urllib2 import (
        Request as url_request,
        urlopen as url_open,
    )
except ImportError:
    import urllib.request.Request as url_request
    import urllib.request.urlopen as url_open


__author__ = 'Mansour Moufid'
__copyright__ = 'Copyright 2015, Mansour Moufid'
__email__ = 'mansourmoufid@gmail.com'
__license__ = 'ISC'
__status__ = 'Development'
__version__ = '1.0'


supported_sys = ('Linux', 'Darwin')

supported_mach = {
    'i386': '32',
    'x86_64': '64',
}

default_compiler = {
    'Linux': 'gcc',
    'Darwin': 'clang',
}

archives = [
    'http://minipkg.eliteraspberries.com/pkgsrc-2015Q3.tar.gz',
    'http://minipkg.eliteraspberries.com/pkgsrc-eliteraspberries-0.3.tar.gz',
]

hash_algorithm = hashlib.sha256

archive_hashes = [
    'f56599dece253113f64d92c528989b7fcb899f3888c7c9fc40f70f08ac91fea6',
    'db8ebcd1c12229e9d2da92f888cdb8505f9c486381f3f9b2cd8948a14a04b671',
]


def uname():
    p = subprocess.Popen(['uname', '-sm'], stdout=subprocess.PIPE)
    p.wait()
    assert p.returncode == 0, 'uname'
    (sys, mach) = p.stdout.read().split()
    return (sys, mach)


def fetch(url, hash):
    filename = os.path.basename(url)
    if not os.path.exists(filename):
        req = url_request(url)
        res = url_open(req)
        dat = res.read()
        with open(filename, 'wb') as f:
            f.write(dat)
    with open(filename, 'r') as f:
        dat = f.read()
    h = hash_algorithm(dat)
    assert h.hexdigest() == hash


def extract(tgz, path):
    if not os.path.exists(path):
        os.mkdir(path)
    tar = tgz.rstrip('.gz')
    if not os.path.exists(tar):
        err = subprocess.call(['gunzip', tgz])
        assert err == 0, 'gunzip'
    err = subprocess.call(['tar', '-xf', tar, '-C', path])
    assert err == 0, 'tar'


recommended_packages = [
    'nbpatch-20100124.tgz',
    'libfetch-2.36nb1.tgz',
    'digest-20121220.tgz',
    'libtool-base-2.4.2nb10.tgz',
    'gzip-1.6.tgz',
    'bzip2-1.0.6nb1.tgz',
    'ncurses-6.0nb1.tgz',
    'readline-6.3nb3.tgz',
    'zlib-1.2.8nb3.tgz',
    'gettext-lib-0.19.4.tgz',
    'perl-5.22.0.tgz',
    'p5-Scalar-List-Utils-1.42nb1.tgz',
    'p5-CPAN-Meta-2.150005.tgz',
    'p5-inc-latest-0.500.tgz',
    'p5-Module-Build-0.42140.tgz',
    'p5-Perl4-CoreLibs-0.003nb5.tgz',
    'sqlite3-3.8.11.1.tgz',
    'openssl-1.0.2d.tgz',
    'xz-5.2.1.tgz',
    'libarchive-3.1.2nb1.tgz',
    'pkgin-0.9.3.tgz',
]


def install_binary_package(repo, pkg):
    pkg_url = '/'.join([repo, pkg])
    ret = subprocess.call(['pkg_add', pkg_url])
    assert ret == 0, 'pkg_add'


if __name__ == '__main__':

    assert len(sys.argv) in (1, 2)
    if len(sys.argv) == 1:
        pass
    elif len(sys.argv) == 2:
        if sys.argv[1] in ('-h', '--help'):
            print(__doc__)
            print('Supported systems:', supported_sys)
            print('Supported architectures:', list(supported_mach.keys()))
            sys.exit(os.EX_OK)
        elif sys.argv[1] in ('-v', '--version'):
            print('minipkg version', __version__)
            sys.exit(os.EX_OK)
        else:
            print(__doc__)
            sys.exit(os.EX_USAGE)

    print('minipkg: version', __version__)

    # Step 1:
    # Determine some information about the machine.
    HOME = os.environ['HOME']
    OPSYS, mach = uname()
    assert OPSYS in supported_sys, 'unsupported system'
    assert mach in supported_mach, 'unsupported architecture'
    ABI = supported_mach[mach]
    CC = os.environ.get('CC', None) or default_compiler[OPSYS]
    print('minipkg: HOME:', HOME)
    print('minipkg: OPSYS:', OPSYS)
    print('minipkg: ABI:', ABI)
    print('minipkg: CC:', CC)

    # Step 2:
    # Fetch the pkgsrc archive.
    for (archive, hash) in zip(archives, archive_hashes):
        print('minipkg: fetching', archive, '...')
        fetch(archive, hash)

    # Step 3:
    # Extract the pkgsrc archive.
    home_usr = os.path.join(HOME, 'usr')
    for tgz in map(os.path.basename, archives):
        print('minipkg: extracting', tgz, '...')
        extract(tgz, home_usr)

    # Step 4:
    # Bootstrap pkgsrc.
    print('minipkg: bootstrapping ...')
    sh = os.environ.get('SH', '/bin/bash')
    sh = sh.split(os.pathsep)[0]
    assert os.path.exists(sh), sh
    os.environ.update({'SH': sh})
    bootstrap_path = os.path.join(HOME, 'usr', 'pkgsrc', 'bootstrap')
    if not os.path.exists(os.path.join(bootstrap_path, 'work')):
        os.chdir(bootstrap_path)
        p = subprocess.Popen(
            [
                './bootstrap',
                '--unprivileged',
                '--abi', ABI,
                '--compiler', CC,
                '--make-jobs', '4',
                '--prefer-pkgsrc', 'no',
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, err = p.communicate()
        log = os.path.join(HOME, 'pkgsrc-bootstrap-log.txt')
        with open(log, 'w') as f:
            f.write(out)
            f.write(err)
        assert p.returncode == 0, 'bootstrap'

    # Step 5:
    # Set environment variables.
    print('minipkg: setting environment variables ...')
    vars = [
        ('PATH', os.path.join(HOME, 'pkg', 'bin')),
        ('PATH', os.path.join(HOME, 'pkg', 'sbin')),
        ('MANPATH', os.path.join(HOME, 'pkg', 'man')),
    ]
    for (key, val) in vars:
        os.environ.update({
            key: val + os.pathsep + os.environ.get(key, ''),
        })
    script = [
        'export %s="%s:$%s"' % (key, val, key)
        for (key, val) in vars
    ]
    dotfile = os.path.join(HOME, '.bash_profile')
    try:
        with open(dotfile, 'r') as f:
            profile = f.read()
    except IOError:
        profile = ''
    with open(dotfile, 'w') as f:
        print('# generated by minipkg', file=f)
        for line in script:
            print(line, file=f)
        print('export SH=%s' % sh, file=f)
        print(profile, file=f)

    # Step 6:
    # Install recommended binary packages.
    print('minipkg: installing packages ...')
    repo = '/'.join([
        'http://minipkg.eliteraspberries.com/packages',
        OPSYS,
        mach,
        'All',
    ])
    for pkg in recommended_packages:
        install_binary_package(repo, pkg)

    print('minipkg: done!')
