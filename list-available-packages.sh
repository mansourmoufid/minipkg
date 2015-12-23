#!/bin/sh
ALL=$HOME/usr/pkgsrc/packages/All
find $ALL -type f -name "*.tgz" \
    | xargs -n1 -- basename \
    | sort
