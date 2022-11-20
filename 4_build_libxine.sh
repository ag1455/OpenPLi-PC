#!/bin/bash

# Build and install xine-lib:
LIB="libxine2"
PKG="xine-lib-1.2-1.2.12+hg-e2pc"
VER="9d0073aaae1a"

I=`dpkg -s $LIB | grep "Status"`

# Remove old package libxine2.
if [ -n "$I" ]; then
	apt-get -y purge libxine2*
else
	echo "$LIB not installed"
fi

# Remove old source libxine2.
if [ -d xine-lib-* ]; then
	rm -rf xine-lib-*
fi

# Case of failure.
if [ -f xine-lib-* ]; then
	rm -f xine-lib-*
fi

# This is hg 1.2.12
wget http://hg.code.sf.net/p/xine/xine-lib-1.2/archive/$VER.tar.bz2
tar -xvjf $VER.tar.bz2
rm $VER.tar.bz2
mv xine-lib-1-2-$VER $PKG

if [ -d "$PKG" ]; then
	echo "-----------------------------------------"
	echo "         head now on $VER"
	echo "-----------------------------------------"
	cp -fv patches/xine-lib-1.2-$VER.patch $PKG
else
	echo "-----------------------------------------"
	echo "        CHECK INTERNET CONNECTION!"
	echo "-----------------------------------------"
fi

cd $PKG
patch -p1 < xine-lib-1.2-$VER.patch
echo "-----------------------------------------"
echo "       patch for xine-lib applied"
echo "-----------------------------------------"
dpkg-buildpackage -b -d -uc -us

cd ..
mv *.deb $PKG
rm -f xine-lib-1.2*

cd $PKG
dpkg -i *.deb
cd ..
