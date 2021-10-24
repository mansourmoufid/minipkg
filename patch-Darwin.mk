--- mk/platform/Darwin.mk.orig	2021-05-28 19:54:57.000000000 -0400
+++ mk/platform/Darwin.mk	2021-05-28 19:55:32.000000000 -0400
@@ -114,8 +114,7 @@
 OSX_SDK_PATH!=	/usr/bin/xcrun \
 		    --sdk macosx${OSX_SDK_MAP.${OSX_VERSION}:U${OSX_VERSION}} \
 		    --show-sdk-path 2>/dev/null || echo /nonexistent
-OSX_TOLERATE_SDK_SKEW?=	no
-.    if ${OSX_SDK_PATH} == "/nonexistent" && !empty(OSX_TOLERATE_SDK_SKEW:M[Yy][Ee][Ss])
+.    if ${OSX_SDK_PATH} == "/nonexistent"
 OSX_SDK_PATH!=	/usr/bin/xcrun --sdk macosx --show-sdk-path 2>/dev/null || echo /nonexistent
 .    endif
 MAKEFLAGS+=	OSX_SDK_PATH=${OSX_SDK_PATH:Q}
