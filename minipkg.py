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
    from urllib2 import Request
    from urllib2 import urlopen
except ImportError:
    from urllib.request import Request
    from urllib.request import urlopen


__author__ = 'Mansour Moufid'
__copyright__ = 'Copyright 2015-2020, Mansour Moufid'
__email__ = 'mansourmoufid@gmail.com'
__license__ = 'ISC'
__status__ = 'Development'
__version__ = '2.2'


supported_sys = ('Linux', 'Darwin')

supported_mach = {
    'x86_64': '64',
}

host = '/'.join([
    'https://github.com/eliteraspberries/pkgsrc-eliteraspberries',
    'releases',
    'download',
    'v2.3',
])

archives = [
    'pkgsrc-2019Q4.tar.gz',
    'pkgsrc-eliteraspberries-2.3.tar.gz',
]

hash_algorithm = hashlib.sha256

archive_hashes = [
    'b7cbca4a0b338812f231db306cd82647cdbf890394f9b77be4f38ac26e2e2a6d',
    '2ac9a389be45fdeb79e918cc4d626d95314664824b377fa3c7b394ed224708ad',
]

patches = [
    'patch-bootstrap',
    'patch-compiler.mk',
    'patch-bsd.prefs.mk',
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
            subprocess.check_call(['curl', '-s', '-L', '-o', filename, url])
        except:
            req = Request(url)
            res = urlopen(req)
            with open(filename, 'ab') as f:
                while True:
                    dat = res.read(1024)
                    if len(dat) == 0:
                        break
                    f.write(dat)
    if hash:
        with open(filename, 'rb') as f:
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

recommended_packages = [
    'digest-*',
    'nbpatch-*',
    'clang-*',
]


cwd = os.path.dirname(os.path.abspath(__file__))


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


minipkg_profile_templates = {}

minipkg_profile_templates['All'] = """
export SH="$sh"
export PATH="$$HOME/pkg/bin:$PATH"
export PATH="$$HOME/pkg/sbin:$PATH"
export MANPATH="$$HOME/pkg/man:$MANPATH"
export FRAMAC_LIB="$$HOME/pkg/lib/frama-c"
export FRAMAC_SHARE="$$HOME/pkg/share/frama-c"
export COCCINELLE_HOME="$$HOME/pkg/lib/coccinelle"
export PYTHONPATH="$$HOME/pkg/lib/coccinelle/python:$$PYTHONPATH"
export PERL5LIB="$$HOME/pkg/lib/perl5:$PERL5LIB"
export CURL_CA_BUNDLE="$$HOME/pkg/etc/ca-certificates.pem"
export PKG_CONFIG_PATH="$$HOME/pkg/lib/pkgconfig:$$PKG_CONFIG_PATH"
export PYSDL2_DLL_PATH="$$HOME/pkg/lib"
export CC="clang"
export CXX="clang++"
export CPPFLAGS="-isystem $${HOME}/pkg/include $${CPPFLAGS}"
export CPPFLAGS="-cxx-isystem $${HOME}/pkg/include/c++/v1 $${CPPFLAGS}"
export CXXFLAGS="-std=c++11 -stdlib=libc++ -nostdinc++ $${CXXFLAGS}"
export LDFLAGS="-lc++ -lc++abi $${LDFLAGS}"
export LDFLAGS="-Wl,-L$${HOME}/pkg/lib $${LDFLAGS}"
"""

minipkg_profile_templates['Linux'] = """
"""

minipkg_profile_templates['Darwin'] = """
export MACOSX_DEPLOYMENT_TARGET="10.9"
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
        print('minipkg: fetching', archive, '...')
        fetch('/'.join([host, archive]), hash=hash)

    # Step 3:
    # Extract the pkgsrc archive.
    for tgz in map(os.path.basename, archives):
        print('minipkg: extracting', tgz, '...')
        extract(tgz, os.path.join(HOME, 'usr'))
    usrpkgsrc = os.path.join(HOME, 'usr', 'pkgsrc')
    for patch in patches:
        fetch('/'.join([host, patch]), path=os.path.join(usrpkgsrc, patch))
        try:
            subprocess.check_call([
                'patch',
                '-d', usrpkgsrc,
                '-f',
                '-i', os.path.join(usrpkgsrc, patch),
                '-p0',
            ])
        except:
            pass
    overwrite_pkgpaths = [
        'devel/cmake',
        'devel/gmp',
        'devel/libffi',
        'devel/ncurses',
        'devel/readline',
    ]
    for pkgpath in overwrite_pkgpaths:
        cat, pkg = pkgpath.split('/')
        os.chdir(os.path.join(usrpkgsrc, cat))
        subprocess.check_call(['rm', '-rf', pkg])
        subprocess.check_call([
            'ln', '-F', '-s',
            os.path.join('..', 'eliteraspberries', pkg),
            os.path.join(pkg),
        ])

    # Step 4:
    # Bootstrap pkgsrc.
    print('minipkg: bootstrapping ...')
    sh = os.environ.get('SH', '/bin/bash')
    sh = sh.split(os.pathsep)[0]
    assert os.path.exists(sh), sh
    os.environ.update({'SH': sh})
    bootstrap_path = os.path.join(HOME, 'usr', 'pkgsrc', 'bootstrap')
    mk_conf = os.path.join(cwd, 'mk.conf')
    assert os.path.exists(mk_conf)
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
                '--mk-fragment', mk_conf,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
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
    if OPSYS == 'Darwin':
        x, y = osx_version()[:2]
        sdkroot = sdkroot((x, y))
    else:
        sdkroot = ''
    minipkg_profile = os.path.join(HOME, '.minipkg_profile')
    with open(minipkg_profile, 'w+') as f:
        print('# generated by minipkg', file=f)
        for sys in ['All', OPSYS]:
            minipkg_profile_template = minipkg_profile_templates[sys]
            template = string.Template(minipkg_profile_template)
            profile = template.safe_substitute({
                'sdkroot': sdkroot,
                'sh': sh,
            })
            f.write(profile)
    for dotfile in ['.bash_profile', '.bashrc']:
        with open(os.path.join(dotfile), 'a+') as f:
            print('', file=f)
            print('. $HOME/.minipkg_profile', file=f)

    # Step 6:
    # Copy scripts to PATH.
    print('minipkg: copying scripts ...')
    scripts = [
        'fix-perm.py',
        'fix-rpath.py',
        'fix-shebang.py',
        'spatch.py',
    ]
    localbase = os.path.join(HOME, 'pkg')
    for script in scripts:
        path = os.path.join(localbase, 'sbin', script)
        with open(os.path.join(cwd, script), 'rt') as x:
            with open(path, 'wt') as y:
                for line in x:
                    y.write(line)
        os.chmod(path, int('755', 8))

    print('minipkg: done!')
