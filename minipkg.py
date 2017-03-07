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
__version__ = '2.1'


supported_sys = ('Linux', 'Darwin')

supported_mach = {
    'x86_64': '64',
}

host = 'https://s3.amazonaws.com/minipkg.eliteraspberries.com'

archives = [
    host + '/pkgsrc-2016Q4.tar.gz',
    host + '/pkgsrc-eliteraspberries-1.9.tar.gz',
]

hash_algorithm = hashlib.sha256

archive_hashes = [
    'a71b5f6f6091e9d9cd0505bcfc14e7b6a92d0cea0a86a8e9d72caf0f24ebcf1a',
    '89fcecfbbb5cf2f409fa4c0628f61b65dc3f72e7c29d161c8f2a623623c2a5e2',
]


def which(name):
    out = subprocess.check_output(['which', name], universal_newlines=True)
    return out.rstrip('\n')


def uname():
    out = subprocess.check_output(['uname', '-sm'], universal_newlines=True)
    (sys, mach) = out.split()
    return (sys, mach)


def fetch(url, path=None, hash=None):
    filename = path or os.path.abspath(os.path.basename(url))
    subprocess.check_call(['mkdir', '-p', os.path.dirname(filename)])
    if not os.path.exists(filename):
        try:
            subprocess.check_call(['curl', '-s', '-o', filename, url])
        except:
            req = url_request(url)
            res = url_open(req)
            with open(filename, 'a') as f:
                while True:
                    dat = res.read(1024)
                    if len(dat) == 0:
                        break
                    f.write(dat)
    if hash:
        with open(filename, 'r') as f:
            dat = f.read()
        h = hash_algorithm(dat)
        assert h.hexdigest() == hash


def extract(tgz, path):
    if not os.path.exists(path):
        os.mkdir(path)
    tar = tgz.rstrip('.gz')
    if not os.path.exists(tar):
        subprocess.check_call(['gunzip', tgz])
    subprocess.check_call(['tar', '-xf', tar, '-C', path])


all_packages = [
    'alt-ergo-1.01nb2.tgz',
    'autoconf-2.69nb7.tgz',
    'automake-1.15nb4.tgz',
    'bzip2-1.0.6nb1.tgz',
    'ca-certificates-20161003.tgz',
    'camlp4-4.02.7.tgz',
    'clang-3.8.0nb6.tgz',
    'cmake-3.7.0nb2.tgz',
    'coccinelle-1.0.6nb2.tgz',
    'curl-7.52.1.tgz',
    'cython-0.25.2.tgz',
    'digest-20160304.tgz',
    'fftw-3.3.6nb2.tgz',
    'frama-c-20151002nb3.tgz',
    'gettext-lib-0.19.8.1.tgz',
    'gettext-tools-0.19.8.1.tgz',
    'gmake-4.1nb3.tgz',
    'gmp-6.1.0nb2.tgz',
    'gsed-4.2.2nb4.tgz',
    'gzip-1.6.tgz',
    'help2man-1.47.4.tgz',
    'jpeg-9b.tgz',
    'libarchive-3.1.2.tgz',
    'libcxx-3.8.0nb3.tgz',
    'libffi-3.2.1nb3.tgz',
    'libpng-1.6.28.tgz',
    'libtool-base-2.4.2nb13.tgz',
    'lzip-1.18.tgz',
    'mbedtls-2.4.0nb2.tgz',
    'menhir-20151112nb4.tgz',
    'nbpatch-20151107.tgz',
    'ncurses-6.0nb3.tgz',
    'ocaml-4.02.3nb9.tgz',
    'ocaml-findlib-1.6.1nb5.tgz',
    'ocamlgraph-1.8.7nb2.tgz',
    'p5-gettext-1.07nb1.tgz',
    'parmap-1.0rc7nb5.tgz',
    'pcre-8.39.tgz',
    'pcre-ocaml-7.2.2nb3.tgz',
    'perl-5.24.0.tgz',
    'pkgconf-1.0.1.tgz',
    'python-2.7.13nb2.tgz',
    'python-docopt-0.6.2.tgz',
    'python-numpy-1.11.0.tgz',
    'python-pillow-3.3.0nb3.tgz',
    'python-setuptools-28.8.0.tgz',
    'python-wheel-0.29.0.tgz',
    'readline-6.3nb3.tgz',
    'scons-2.5.1.tgz',
    'sqlite3-3.15.2nb2.tgz',
    'tcl-8.6.5nb2.tgz',
    'tk-8.6.5.tgz',
    'xz-5.2.2.tgz',
    'zarith-1.4.1nb7.tgz',
    'zlib-1.2.8nb3.tgz',
]

recommended_packages = [
    'clang-*',
]


def install_binary_package(home, pkg):
    prefix = os.path.join(home, 'pkg')
    pkg_add = os.path.join(home, 'pkg', 'sbin', 'pkg_add')
    pkg_path = os.path.join(home, 'usr', 'pkgsrc', 'packages', 'All', pkg)
    subprocess.check_call([pkg_add, '-I', '-p', prefix, pkg_path])


cwd = os.path.split(os.path.abspath(__file__))[0]


def osx_version():
    sw_vers_out = subprocess.check_output(
        ['sw_vers', '-productVersion'],
        universal_newlines=True,
    )
    product_version = sw_vers_out.rstrip('\n')
    osx_version = product_version.split('.')
    return osx_version


def sdkroot(version):
    x, y = version[:2]
    sdk = 'macosx' + x + '.' + y
    xcrun_out = subprocess.check_output(
        ['xcrun', '--sdk', sdk, '--show-sdk-path'],
        universal_newlines=True,
    )
    sdkroot = xcrun_out.rstrip('\n')
    return sdkroot


minipkg_profile_template = """
export SH="$sh"
export PATH="$$HOME/pkg/bin:$PATH"
export PATH="$$HOME/pkg/sbin:$PATH"
export MANPATH="$$HOME/pkg/man:$MANPATH"
export FRAMAC_LIB="$$HOME/pkg/lib/frama-c"
export FRAMAC_SHARE="$$HOME/pkg/share/frama-c"
export COCCINELLE_HOME="$$HOME/pkg/lib/coccinelle"
export PYTHONHOME="$$HOME/pkg"
export PERL5LIB="$$HOME/pkg/lib/perl5:$PERL5LIB"
export CURL_CA_BUNDLE="$$HOME/pkg/etc/ca-certificates.pem"
"""

minipkg_profile_template_linux = """
"""

minipkg_profile_template_darwin = """
export MACOSX_DEPLOYMENT_TARGET="10.7"
export SDKROOT="$sdkroot"
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
        print('minipkg: fetching', os.path.basename(archive), '...')
        fetch(archive, hash=hash)

    # Step 3:
    # Extract the pkgsrc archive.
    home_usr = os.path.join(HOME, 'usr')
    for tgz in map(os.path.basename, archives):
        print('minipkg: extracting', tgz, '...')
        extract(tgz, home_usr)
    localbase = os.path.join(HOME, 'usr', 'pkgsrc')
    overwrite_pkgpaths = [
        'devel/cmake',
        'devel/gmp',
        'devel/libffi',
        'devel/ncurses',
        'devel/readline',
    ]
    for pkgpath in overwrite_pkgpaths:
        cat, pkg = pkgpath.split('/')
        os.chdir(localbase)
        subprocess.check_call(['rm', '-rf', pkgpath])
        subprocess.check_call([
            'ln', '-s',
            os.path.join(localbase, 'eliteraspberries', pkg),
            os.path.join(localbase, cat, pkg),
        ])

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
    if OPSYS == 'Darwin':
        x, y = osx_version()[:2]
        sdkroot = sdkroot((x, y))
        template = string.Template(minipkg_profile_template_darwin)
        profile_darwin = template.safe_substitute({
            'sdkroot': sdkroot,
        })
        with open(minipkg_profile, 'a+') as f:
            f.write(profile_darwin)
    if OPSYS == 'Linux':
        template = string.Template(minipkg_profile_template_linux)
        profile_linux = template.safe_substitute({
        })
        with open(minipkg_profile, 'a+') as f:
            f.write(profile_linux)
    for dotfile in ['.bash_profile', '.bashrc']:
        with open(os.path.join(dotfile), 'a+') as f:
            print('', file=f)
            print('. $HOME/.minipkg_profile', file=f)

    # Step 6:
    # Install binary packages.
    print('minipkg: fetching packages ...')
    repo = '/'.join([host, 'packages', OPSYS, mach])
    for pkg in all_packages:
        print('minipkg: fetching', pkg, '...')
        fetch(
            '/'.join([repo, 'All', pkg]),
            path=os.path.join(localbase, 'packages', 'All', pkg),
            hash=None,
        )
    for pkg in recommended_packages:
        print('minipkg: installing', pkg, '...')
        install_binary_package(HOME, pkg)

    print('minipkg: done!')
