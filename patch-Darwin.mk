--- pkgsrc/mk/platform/Darwin.mk.orig	2025-04-12 04:41:11
+++ pkgsrc/mk/platform/Darwin.mk	2025-08-13 21:08:10
@@ -46,7 +46,7 @@
 .else
 ECHO_N?=	${ECHO} -n
 .endif
-LDD?=		/usr/bin/otool -L
+LDD=
 IMAKE_MAKE?=	${MAKE}		# program which gets invoked by imake
 PKGLOCALEDIR?=	share
 PS?=		/bin/ps
@@ -100,44 +100,6 @@
 .endif
 
 #
-# If the user has set MACOSX_DEPLOYMENT_TARGET (ideally at bootstrap
-# time) to select a specific SDK then we prefer that.  An example of
-# an sdk name acceptable to xcrun is "macosx15.1".  Because the code
-# prepends macosx, one would invoke
-#   bmake MACOSX_DEPLOYMENT_TARGET=14.5 package
-# (SDK names are not directory names, and need to be the full version,
-# rather than major only; "MacOSX15" will fail.)
-.if defined(MACOSX_DEPLOYMENT_TARGET)
-.  if !defined(OSX_SDK_PATH)
-OSX_SDK_PATH!=	/usr/bin/xcrun --sdk macosx${MACOSX_DEPLOYMENT_TARGET} \
-		    --show-sdk-path 2>/dev/null || echo /nonexistent
-.  endif
-.  if !exists(${OSX_SDK_PATH})
-PKG_FAIL_REASON+=	"Unable to find macOS SDK at ${OSX_SDK_PATH}"
-PKG_FAIL_REASON+=	"Check MACOSX_DEPLOYMENT_TARGET points to a valid SDK"
-.  endif
-ALL_ENV+=		MACOSX_DEPLOYMENT_TARGET=${MACOSX_DEPLOYMENT_TARGET}
-MAKEFLAGS+=		OSX_SDK_PATH=${OSX_SDK_PATH:Q}
-_OPSYS_INCLUDE_DIRS?=	${OSX_SDK_PATH}/usr/include
-CWRAPPERS_APPEND.cc+=	-isysroot ${OSX_SDK_PATH}
-CWRAPPERS_APPEND.cxx+=	-isysroot ${OSX_SDK_PATH}
-_WRAP_EXTRA_ARGS.CC+=	-isysroot ${OSX_SDK_PATH}
-_WRAP_EXTRA_ARGS.CXX+=	-isysroot ${OSX_SDK_PATH}
-.elif exists(/usr/include/stdio.h)
-_OPSYS_INCLUDE_DIRS?=	/usr/include
-.elif exists(/usr/bin/xcrun)
-.  if !defined(OSX_SDK_PATH)
-OSX_SDK_PATH!=	/usr/bin/xcrun --sdk macosx --show-sdk-path 2>/dev/null || echo /nonexistent
-MAKEFLAGS+=	OSX_SDK_PATH=${OSX_SDK_PATH:Q}
-.  endif
-.  if exists(${OSX_SDK_PATH}/usr/include/stdio.h)
-_OPSYS_INCLUDE_DIRS?=	${OSX_SDK_PATH}/usr/include
-.  else
-PKG_FAIL_REASON+=	"No suitable Xcode SDK or Command Line Tools installed."
-.  endif
-.endif
-
-#
 # Newer macOS releases remove library files from the file system.  The only way
 # to test them is via dlopen(), which is obviously impractical for many things.
 #
@@ -181,9 +143,9 @@
 _OPSYS_PREFER.mit-krb5?=	native
 _OPSYS_PREFER.openssl?=		pkgsrc	# builtin deprecated from 10.7 onwards
 
-_OPSYS_SUPPORTS_CWRAPPERS=	yes
+_OPSYS_SUPPORTS_CWRAPPERS=	no
 
-_OPSYS_CAN_CHECK_SHLIBS=	yes # check shared libraries using otool(1)
+_OPSYS_CAN_CHECK_SHLIBS=	no
 
 # OSX strip(1) tries to remove relocatable symbols and fails on certain
 # objects, resulting in non-zero exit status.  We can't modify strip arguments
