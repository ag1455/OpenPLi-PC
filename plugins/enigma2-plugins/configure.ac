AC_INIT([enigma2-plugins],[4],[forum@openpli.org])
AM_INIT_AUTOMAKE([dist-bzip2 foreign no-define tar-pax])
AC_CONFIG_HEADERS([enigma2-plugins-config.h])

# Silent rules are available since 1.11, but older versions
# are still in use. So don't use them unconditionally.
m4_ifdef([AM_SILENT_RULES], [AM_SILENT_RULES([yes])])

AC_USE_SYSTEM_EXTENSIONS
AC_SYS_LARGEFILE

AC_PROG_CC
AC_PROG_CXX
m4_ifdef([LT_INIT], [LT_INIT], [AC_PROG_LIBTOOL])
AC_CONFIG_MACRO_DIR([m4])

AC_PATH_PROG(MSGFMT, msgfmt, AC_MSG_ERROR(Could not find msgfmt))

AM_PATH_PYTHON
AX_PYTHON_DEVEL
AX_PTHREAD

TUXBOX_APPS_DVB

PKG_CHECK_MODULES(ENIGMA2, enigma2)
PKG_CHECK_MODULES(GSTREAMER, gstreamer-1.0 gstreamer-pbutils-1.0)
PKG_CHECK_MODULES(LIBCRYPTO, libcrypto)

AC_ARG_WITH(tpm,
	AS_HELP_STRING([--with-tpm], [enable plugins that require a TPM]),
	[with_tpm="$withval"],[with_tpm="no"])
if test "$with_tpm" = "yes"; then
	AC_DEFINE([HAVE_TPM],[1],[Define to 1 to enable plugins that require a TPM])
fi
AM_CONDITIONAL(TPM, test "$with_tpm" = "yes")

AC_ARG_WITH(debug,
	AS_HELP_STRING([--without-debug],[disable debugging code]),
	[with_debug="$withval"],[with_debug="yes"])
if test "$with_debug" = "yes"; then
	DEBUG_CFLAGS="-ggdb3"
	AC_DEFINE([DEBUG],[1],[Define to 1 to enable debugging code])
fi
AC_SUBST(DEBUG_CFLAGS)

AC_ARG_WITH(po,
	AS_HELP_STRING([--with-po],[enable updating of po files]),
	[with_po="$withval"],[with_po="no"])
if test "$with_po" = "yes"; then
	AC_PATH_PROG(MSGINIT, msginit)
	AC_PATH_PROG(MSGMERGE, msgmerge)
	AC_PATH_PROG(MSGUNIQ, msguniq)
	AC_PATH_PROG(XGETTEXT, xgettext)
	if test -z "$MSGINIT" -o -z "$MSGMERGE" -o -z "$MSGUNIQ" -o -z "$XGETTEXT"; then
		AC_MSG_ERROR([Could not find required gettext tools])
	fi
fi
AM_CONDITIONAL(UPDATE_PO, test "$with_po" = "yes")

AC_CONFIG_FILES([
Makefile

antiscrollbar/Makefile
antiscrollbar/meta/Makefile
antiscrollbar/src/Makefile
antiscrollbar/po/Makefile

automaticvolumeadjustment/Makefile
automaticvolumeadjustment/src/Makefile
automaticvolumeadjustment/meta/Makefile
automaticvolumeadjustment/po/Makefile

bitrate/Makefile
bitrate/bitratetool/Makefile
bitrate/po/Makefile

epgsearch/Makefile
epgsearch/meta/Makefile
epgsearch/src/Makefile
epgsearch/src/icons/Makefile
epgsearch/po/Makefile

epgrefresh/Makefile
epgrefresh/src/Makefile
epgrefresh/src/webinterface/Makefile
epgrefresh/etc/Makefile
epgrefresh/meta/Makefile
epgrefresh/po/Makefile

ftpbrowser/Makefile
ftpbrowser/meta/Makefile
ftpbrowser/src/Makefile
ftpbrowser/src/images/Makefile
ftpbrowser/po/Makefile

filebrowser/Makefile
filebrowser/meta/Makefile
filebrowser/src/Makefile
filebrowser/po/Makefile

mphelp/Makefile
mphelp/meta/Makefile
mphelp/src/Makefile

permanentclock/Makefile
permanentclock/meta/Makefile
permanentclock/po/Makefile
permanentclock/src/Makefile
permanentclock/src/trad/Makefile

pluginhider/Makefile
pluginhider/meta/Makefile
pluginhider/src/Makefile
pluginhider/po/Makefile

recordinfobar/Makefile
recordinfobar/meta/Makefile
recordinfobar/src/Makefile
recordinfobar/po/Makefile

servicemp3/Makefile
servicemp3/plugin/Makefile
servicemp3/servicemp3/Makefile

systemtime/Makefile
systemtime/src/Makefile
systemtime/src/images/Makefile
systemtime/meta/Makefile
systemtime/po/Makefile

networkbrowser/Makefile
networkbrowser/meta/Makefile
networkbrowser/po/Makefile
networkbrowser/src/Makefile
networkbrowser/src/icons/Makefile
networkbrowser/src/lib/Makefile

])
AC_OUTPUT
