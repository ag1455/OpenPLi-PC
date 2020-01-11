#!/bin/bash

release=$(lsb_release -a 2>/dev/null | grep -i release | awk ' { print $2 } ')

# Build and install xine-lib:
LIB="libxine2"
PKG="xine-lib-1.2-1.2.9+hg-e2pc"
I=`dpkg -s $LIB | grep "Status"`

# Remove old package libxine2.
if [ -n "$I" ]; then
	apt -y purge libxine2*
else
	echo "$LIB not installed"
fi

# Remove old source libxine2.
if [ -d $PKG ]; then
	rm -rf $PKG
else
	rm -f $PKG
fi

# This is hg 1.2.9
hg clone -r b6cc71673eb9 http://hg.code.sf.net/p/xine/xine-lib-1.2 $PKG

if [ -d "$PKG" ]; then
	echo "-----------------------------------------"
	echo "         head now on b6cc71673eb9        "
	echo "-----------------------------------------"
	cp patches/xine-lib-1.2*.patch $PKG
else
	echo "-----------------------------------------"
	echo "        CHECK INTERNET CONNECTION!       "
	echo "-----------------------------------------"
fi

cd $PKG
patch -p1 < xine-lib-1.2*.patch
echo "-----------------------------------------"
echo "       patch for xine-lib applied        "
echo "-----------------------------------------"
dpkg-buildpackage -d -uc -us

cd ..
mv *.deb $PKG
rm -f xine-lib-1.2*

cd $PKG
dpkg -i *.deb
cd ..
