--- mk/bsd.prefs.mk.orig	2018-05-23 07:26:54.000000000 -0400
+++ mk/bsd.prefs.mk	2018-09-08 15:53:33.000000000 -0400
@@ -765,13 +765,8 @@
 _PKGSRC_USE_STACK_CHECK=yes
 .endif
 
-# Enable cwrappers if not building the wrappers themselves, and if the user has
-# explicitly requested them, or if they haven't but the compiler/platform is
-# known to support them.
-.if empty(PKGPATH:Mpkgtools/cwrappers) && \
-    (${USE_CWRAPPERS:tl} == "yes" || \
-    (${USE_CWRAPPERS:tl} == "auto" && \
-     ${_OPSYS_SUPPORTS_CWRAPPERS:Uno} == "yes"))
+# Enable cwrappers if requested unless we're building the wrappers themselves.
+.if ${USE_CWRAPPERS:tl} != "no" && empty(PKGPATH:Mpkgtools/cwrappers)
 _USE_CWRAPPERS=		yes
 .else
 _USE_CWRAPPERS=		no
