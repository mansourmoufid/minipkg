#!/usr/bin/env python

"""minipkg.py - install pkgsrc

Usage:
    python minipkg.py
    python minipkg.py [-h | --help] [-v | --version]
"""


from __future__ import print_function

import hashlib
import os
import string
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
__copyright__ = 'Copyright 2015, 2016, Mansour Moufid'
__email__ = 'mansourmoufid@gmail.com'
__license__ = 'ISC'
__status__ = 'Development'
__version__ = '1.8'


supported_sys = ('Linux', 'Darwin')

supported_mach = {
    'x86_64': '64',
}

archives = [
    'http://minipkg.eliteraspberries.com/pkgsrc-2015Q4.tar.gz',
    'http://minipkg.eliteraspberries.com/pkgsrc-eliteraspberries-1.4.tar.gz',
]

hash_algorithm = hashlib.sha256

archive_hashes = [
    'fe56b3e5c2596a4533180de4c8a145f7e9d0f06b573e6a667770ec59176b18d4',
    '76fdbe72f6839c17995e6d41696c0529bfe45038ba42565207ceeb92d525b1a5',
]


def which(name):
    p = subprocess.Popen(['which', name], stdout=subprocess.PIPE)
    p.wait()
    if not p.returncode == 0:
        return None
    out = p.stdout.read()
    return out.rstrip('\n')


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
        with open(filename, 'wb+') as f:
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
    'digest-20121220.tgz',
    'nbpatch-20151107.tgz',
    'libtool-base-2.4.2nb10.tgz',
    'bzip2-1.0.6nb1.tgz',
    'ncurses-6.0nb3.tgz',
    'gettext-lib-0.19.6.tgz',
    'xz-5.2.2.tgz',
    'gettext-tools-0.19.6.tgz',
    'gtar-base-1.28nb1.tgz',
    'gzip-1.6.tgz',
    'perl-5.22.0.tgz',
    'p5-gettext-1.07.tgz',
    'help2man-1.47.3.tgz',
    'autoconf-2.69nb6.tgz',
    'automake-1.15nb2.tgz',
    'gmake-4.1nb1.tgz',
    'zlib-1.2.8nb3.tgz',
    'pkg-config-0.29.tgz',
    'libarchive-3.1.2.tgz',
    'curl-7.48.0.tgz',
    'cmake-3.5.1.tgz',
    'libcxx-3.8.0nb3.tgz',
    'clang-3.8.0nb5.tgz',
    'ocaml-4.02.3nb7.tgz',
    'ocaml-findlib-1.6.1nb4.tgz',
    'pcre-8.38.tgz',
    'pcre-ocaml-7.2.2nb2.tgz',
    'parmap-1.0rc7nb4.tgz',
    'menhir-20151112nb3.tgz',
    'camlp4-4.02.6nb5.tgz',
    'coccinelle-1.0.4nb5.tgz',
    'fftw-3.3.4nb2.tgz',
    'lzip-1.17.tgz',
    'gmp-6.1.0nb2.tgz',
    'zarith-1.4.1nb7.tgz',
    'ocamlgraph-1.8.6nb8.tgz',
    'alt-ergo-1.01nb2.tgz',
    'frama-c-20151002.tgz',
    'tcl-8.6.4nb3.tgz',
    'tk-8.6.4nb5.tgz',
    'readline-6.3nb3.tgz',
    'libffi-3.2.1.tgz',
    'sqlite3-3.9.2.tgz',
    'python-2.7.11nb5.tgz',
    'python-setuptools-20.4.tgz',
    'python-wheel-0.29.0.tgz',
    'gsed-4.2.2nb4.tgz',
]


def install_binary_package(home, repo, pkg):
    pkg_url = '/'.join([repo, 'All', pkg])
    prefix = os.path.join(home, 'pkg')
    ret = subprocess.call([
        os.path.join(home, 'pkg', 'sbin', 'pkg_add'),
        '-I',
        '-p', prefix,
        pkg_url,
    ])
    assert ret == 0, 'pkg_add'


cwd = os.path.split(os.path.abspath(__file__))[0]


minipkg_profile_template = """
export SH="$sh"
export PATH="$home/pkg/bin:$PATH"
export PATH="$home/pkg/sbin:$PATH"
export MANPATH="$home/pkg/man:$MANPATH"
export FRAMAC_LIB="$home/pkg/lib/frama-c"
export FRAMAC_SHARE="$home/pkg/share/frama-c"
export COCCINELLE_HOME="$home/pkg/lib/coccinelle"
export PYTHONHOME="$home/pkg"
export PERL5LIB="$home/pkg/lib/perl5:$PERL5LIB"
"""


if __name__ == '__main__':

    if len(sys.argv) == 1:
        pass
    elif len(sys.argv) == 2:
        if sys.argv[1] in ('-h', '--help'):
            print(__doc__)
            print('Supported systems:', supported_sys)
            print('Supported architectures:', list(supported_mach.keys()))
            sys.exit(os.EX_OK)
        elif sys.argv[1] in ('-v', '--version'):
            print(os.path.basename(sys.argv[0]), 'version', __version__)
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
    CC = os.environ.get('CC', 'clang')
    assert which(CC), CC
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
    localbase = os.path.join(HOME, 'usr', 'pkgsrc')
    overwrite_pkgpaths = [
        'devel/gmp',
        'devel/libffi',
        'devel/ncurses',
        'devel/readline',
    ]
    for pkgpath in overwrite_pkgpaths:
        cat, pkg = pkgpath.split('/')
        os.chdir(localbase)
        ret = subprocess.call(['rm', '-rf', pkgpath])
        assert ret == 0, 'rm'
        ret = subprocess.call([
            'ln', '-s',
            os.path.join(localbase, 'eliteraspberries', pkg),
            os.path.join(localbase, cat, pkg),
        ])
        assert ret == 0, 'ln'

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
                '--mk-fragment', os.path.join(cwd, 'mk.conf'),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, err = p.communicate()
        log = os.path.join(HOME, 'pkgsrc-bootstrap-log.txt')
        with open(log, 'w+') as f:
            f.write(out)
            f.write(err)
        assert p.returncode == 0, 'bootstrap'
        try:
            os.remove(log)
        except OSError:
            pass

    # Step 5:
    # Set environment variables.
    print('minipkg: setting environment variables ...')
    template = string.Template(minipkg_profile_template)
    profile = template.safe_substitute({
        'home': HOME,
        'sh': sh,
    })
    minipkg_profile = os.path.join(HOME, '.minipkg_profile')
    with open(minipkg_profile, 'w+') as f:
        print('# generated by minipkg', file=f)
        f.write(profile)
    dotfile = os.path.join(HOME, '.bash_profile')
    try:
        with open(dotfile, 'r') as f:
            profile = f.read()
    except IOError:
        profile = ''
    with open(dotfile, 'w+') as f:
        print('source %s' % (minipkg_profile), file=f)
        print('', file=f)
        f.write(profile)

    # Step 6:
    # Install recommended binary packages.
    print('minipkg: installing packages ...')
    repo = '/'.join([
        'http://minipkg.eliteraspberries.com/packages',
        OPSYS,
        mach,
    ])
    for pkg in recommended_packages:
        install_binary_package(HOME, repo, pkg)

    print('minipkg: done!')
