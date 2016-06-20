#!/bin/sh
SYS=$(uname -s)
ARCH=$(uname -m)
LOCAL="$HOME/usr/pkgsrc/packages"
REMOTE="s3://minipkg.eliteraspberries.com/packages"
OPTS="--acl public-read --cache-control max-age=86400"
aws s3 cp $OPTS $LOCAL/pkg_summary.gz $REMOTE/$SYS/$ARCH/
aws s3 cp --recursive $OPTS $LOCAL/All $REMOTE/$SYS/$ARCH/All/
