#!/bin/sh
aws s3 cp --recursive \
	$HOME/usr/pkgsrc/distfiles \
	s3://minipkg.eliteraspberries.com/distfiles \
	--acl public-read \
	--cache-control max-age=86400 \
	--exclude CVS/* --exclude .cvsignore
