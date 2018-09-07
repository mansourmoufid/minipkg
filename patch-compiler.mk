--- mk/compiler.mk.orig	2018-01-26 08:14:35.000000000 -0500
+++ mk/compiler.mk	2018-09-08 15:50:04.000000000 -0400
@@ -120,7 +120,7 @@
 
 .if defined(_ACCEPTABLE_COMPILERS)
 .  for _acceptable_ in ${_ACCEPTABLE_COMPILERS}
-.    for _compiler_ in ${PKGSRC_COMPILER}
+.    for _compiler_ in ${PKGSRC_COMPILER:C/-.*//}
 .      if !empty(_ACCEPTABLE_COMPILERS:M${_compiler_}) && !defined(_COMPILER)
 _COMPILER=	${_compiler_}
 .      endif
