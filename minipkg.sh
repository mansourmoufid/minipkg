#!/bin/sh
set -e
set -x
dir="$(cd $(dirname $0) && pwd)"
usr=$(pwd)/usr
pkg=$(pwd)/pkg
mkdir -p $pkg
test -f pkgsrc.tgz ||
    curl -L -O https://cdn.netbsd.org/pub/pkgsrc/stable/pkgsrc.tgz
mkdir -p $usr
test -d $usr/pkgsrc ||
    gunzip < pkgsrc.tgz| tar -f - -x -C $usr
patches=" \
    patch-bootstrap \
    patch-compiler.mk \
    patch-Darwin.mk \
"
for patch in $patches; do
    test -f $dir/$patch && patch -b -d $usr -p0 < $dir/$patch
done
cd $usr/pkgsrc
test -d eliteraspberries ||
    git clone \
        https://github.com/mansourmoufid/pkgsrc-eliteraspberries \
        eliteraspberries
cd eliteraspberries &&
    git fetch &&
    git merge
overwrite_packages=" \
    devel/cmake \
"
for pkgpath in $overwrite_packages; do
    category="$(echo $pkgpath | awk -F'/' '{print $1}')"
    package="$(echo $pkgpath | awk -F'/' '{print $2}')"
    (
        cd $usr/pkgsrc/$category
        rm -rf $package
        ln -F -s ../eliteraspberries/$package $package
    )
done
export CC=clang
export CXX=clang++
if test "$(uname)" = "Darwin"; then
    export MACOSX_DEPLOYMENT_TARGET="11.0"
    export SDKROOT="$(xcrun --sdk macosx --show-sdk-path)"
    export CC="$(xcrun --find clang)"
    export CXX="$(xcrun --find clang++)"
fi
test -d $usr/pkgsrc/bootstrap/work &&
    rm -rf $usr/pkgsrc/bootstrap/work
cd $usr/pkgsrc/bootstrap &&
    ./bootstrap \
        --compiler clang \
        --cwrappers no \
        --mk-fragment $dir/mk.conf \
        --prefix $pkg \
        --unprivileged ||
    (
        cat $usr/pkgsrc/bootstrap/work/bmake/config.log
    )
scripts=" \
    fix-perm.py \
    fix-rpath.py \
    fix-shebang.py \
    spatch.py \
"
for script in $scripts; do
    cp -f $dir/$script $pkg/sbin/
    chmod a+x $pkg/sbin/$script
done
cat << EOF > $pkg/.profile
export PATH="$pkg/bin:\$PATH"
export PATH="$pkg/sbin:\$PATH"
export MANPATH="$pkg/man:\$MANPATH"
export FRAMAC_LIB="$pkg/lib/frama-c"
export FRAMAC_SHARE="$pkg/share/frama-c"
export COCCINELLE_HOME="$pkg/lib/coccinelle"
export PYTHONPATH="$pkg/lib/python:\$PYTHONPATH"
export PYTHONPATH="$pkg/lib/coccinelle/python:\$PYTHONPATH"
export PERL5LIB="$pkg/lib/perl5:\$PERL5LIB"
export PKG_CONFIG_PATH="$pkg/lib/pkgconfig:\$PKG_CONFIG_PATH"
export PYSDL2_DLL_PATH="$pkg/lib"
export CURL_CA_BUNDLE="$pkg/etc/openssl/certs/ca-certificates.crt"
EOF
. $pkg/.profile
cat $dir/packages.txt | while read pkg; do (
    cd $usr/pkgsrc/$pkg
    bmake configure
    bmake build
    bmake install
    bmake clean clean-depends
) done
