--- pkgtools/bootstrap-mk-files/files/bsd.sys.mk.orig	2018-09-02 19:21:10.000000000 -0400
+++ pkgtools/bootstrap-mk-files/files/bsd.sys.mk	2018-09-02 19:21:21.000000000 -0400
@@ -22,7 +22,6 @@
 .endif
 
 .if !defined(NOGCCERROR)
-CFLAGS+= -Werror
 .endif
 CFLAGS+= ${CWARNFLAGS}
 
