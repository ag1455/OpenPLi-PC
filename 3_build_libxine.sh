#!/bin/bash

# Build and install xine-lib:
LIB="libxine2"
PKG="xine-xine-lib-1.2"
PAT="xine-lib-1.2.13"
DIR="xine-xine-lib"

I=`dpkg -s $LIB | grep "Status"`

# Remove old package libxine2.
if [ -n "$I" ]; then
	apt-get -y purge libxine2*
else
	echo "$LIB not installed"
fi

# Remove old source libxine2.
if [ -d $DIR-* ]; then
	rm -rf $DIR-*
fi

# Case of failure.
if [ -f $DIR-* ]; then
	rm -f $DIR-*
fi

# This is hg 1.2.13
wget https://launchpad.net/ubuntu/+archive/primary/+sourcefiles/xine-lib-1.2/1.2.13+hg20230710-2.1/xine-lib-1.2_1.2.13+hg20230710.orig.tar.gz
tar -xvf *.tar.gz
rm -f *.tar.gz

if [ -d "$PKG" ]; then
	echo "-----------------------------------------"
	echo "             release is $PKG"
	echo "-----------------------------------------"
	cp -fv patches/$PAT+e2pc.patch $PKG
else
	echo "-----------------------------------------"
	echo "        CHECK INTERNET CONNECTION!"
	echo "-----------------------------------------"
fi

cd $PKG
patch -p1 < $PAT+e2pc.patch
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
