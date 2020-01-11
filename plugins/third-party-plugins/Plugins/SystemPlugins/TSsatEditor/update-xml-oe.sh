#!/bin/sh


case $1 in
	dvbs)
		SRC="https://raw.githubusercontent.com/oe-alliance/oe-alliance-tuxbox-common/master/src/satellites.xml"
		DEST=/etc/enigma2/satellites.xml
		if which curl >/dev/null 2>&1 ; then
			curl -o $DEST.new $SRC
		else
			echo >&2 "update-xml-oe: cannot find curl"
			opkg update && opkg install curl
			exit 1
		fi
		if ! [ -f $DEST.new ] ; then
			echo >&2 "update-xml-oe: download failed"
			exit 1
		fi
		if ! grep >/dev/null "satellites" $DEST.new ; then
			echo >&2 "update-xml-oe: missing class satellites, probably truncated file"
			rm -f $DEST.new
			exit 1
		fi
		mv $DEST.new $DEST
		exit 0
	;;
	dvbt)
		SRC="https://raw.githubusercontent.com/oe-alliance/oe-alliance-tuxbox-common/master/src/terrestrial.xml"
		DEST=/etc/enigma2/terrestrial.xml
		if which curl >/dev/null 2>&1 ; then
			curl -o $DEST.new $SRC
		else
			echo >&2 "update-xml-oe: cannot find curl"
			opkg update && opkg install curl
			exit 1
		fi
		if ! [ -f $DEST.new ] ; then
			echo >&2 "update-xml-oe: download failed"
			exit 1
		fi
		if ! grep >/dev/null "locations" $DEST.new ; then
			echo >&2 "update-xml-oe: missing class locations, probably truncated file"
			rm -f $DEST.new
			exit 1
		fi
		mv $DEST.new $DEST
		exit 0
	;;
	dvbc)
		SRC="https://raw.githubusercontent.com/oe-alliance/oe-alliance-tuxbox-common/master/src/cables.xml"
		DEST=/etc/enigma2/cables.xml
		if which curl >/dev/null 2>&1 ; then
			curl -o $DEST.new $SRC
		else
			echo >&2 "update-xml-oe: cannot find curl"
			opkg update && opkg install curl
			exit 1
		fi
		if ! [ -f $DEST.new ] ; then
			echo >&2 "update-xml-oe: download failed"
			exit 1
		fi
		if ! grep >/dev/null "cables" $DEST.new ; then
			echo >&2 "update-xml-oe: missing class cables, probably truncated file"
			rm -f $DEST.new
			exit 1
		fi
		mv $DEST.new $DEST
		exit 0
	;;
	*)
		echo " "
		echo "Options: $0 {dvbs|dvbt|dvbc}"
		echo " "
esac

echo "Done..."

exit 0

