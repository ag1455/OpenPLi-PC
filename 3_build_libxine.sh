#!/bin/bash

# Build and install xine-lib:
LIB="libxine2"
PKG="xine-lib-1.2-1.2.10+hg-e2pc"
I=`dpkg -s $LIB | grep "Status"`

# Remove old package libxine2.
if [ -n "$I" ]; then
	apt-get -y purge libxine2*
else
	echo "$LIB not installed"
fi

# Remove old source libxine2.
if [ -d $PKG ]; then
	rm -rf $PKG
else
	rm -f $PKG
fi

# This is hg 1.2.10
wget http://hg.code.sf.net/p/xine/xine-lib-1.2/archive/12ef7a7992ed.tar.bz2
tar -xvjf 12ef7a7992ed.tar.bz2
rm 12ef7a7992ed.tar.bz2
mv xine-lib-1-2-12ef7a7992ed $PKG

if [ -d "$PKG" ]; then
	echo "-----------------------------------------"
	echo "      head now on 14859:12ef7a7992ed"
	echo "-----------------------------------------"
	cp -fv patches/xine-lib-1.2-14859:12ef7a7992ed.patch $PKG
else
	echo "-----------------------------------------"
	echo "        CHECK INTERNET CONNECTION!"
	echo "-----------------------------------------"
fi

cd $PKG
patch -p1 < xine-lib-1.2-14859:12ef7a7992ed.patch
echo "-----------------------------------------"
echo "       patch for xine-lib applied"
echo "-----------------------------------------"
dpkg-buildpackage -d -uc -us

cd ..
mv *.deb $PKG
rm -f xine-lib-1.2*

cd $PKG
dpkg -i *.deb
cd ..
