--- pkgsrc/mk/compiler.mk.orig	2025-08-19 09:36:55
+++ pkgsrc/mk/compiler.mk	2025-08-19 09:37:16
@@ -188,7 +188,7 @@
 
 .if defined(_ACCEPTABLE_COMPILERS)
 .  for _acceptable_ in ${_ACCEPTABLE_COMPILERS}
-.    for _compiler_ in ${PKGSRC_COMPILER}
+.    for _compiler_ in ${PKGSRC_COMPILER:C/-.*//}
 .      if !empty(_ACCEPTABLE_COMPILERS:M${_compiler_}) && !defined(_COMPILER)
 _COMPILER=	${_compiler_}
 .      endif
