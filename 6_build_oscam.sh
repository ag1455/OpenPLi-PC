#!/bin/bash

REQPKG="cmake"
SOURCE="oscam-patched"

for p in $REQPKG; do
	echo -n ">>> Checking \"$p\" : "
	dpkg -s $p >/dev/null
	if [ "$?" -eq "0" ]; then
		echo "package is installed, skip it"
	else
		echo "package NOT present, installing it"
		apt-get -y install $p
	fi
done
echo "-----------------------------------------"
echo "*** INSTALL OSCAM ***"
echo "-----------------------------------------"

cd oscam
if [ -d $SOURCE ]; then
	rm -fr $SOURCE
fi

git clone https://github.com/oscam-emu/oscam-patched.git
cp demux.patch $SOURCE
cd $SOURCE
patch -p1 < demux.patch
mkdir build
cd build
cmake --DHAVE_DVBAPI --DHAVE_WEBIF ../
make install
cd ../..

echo "-----------------------------------------"
echo "*** COPY CONFIG FILES in /etc/vdr/oscam ***"
echo "*** EDIT DATA FOR YOU ***"
echo "-----------------------------------------"

if [ ! -d /etc/vdr/oscam ]; then
mkdir -p /etc/vdr/oscam
fi
if [ ! -d /var/log/oscam ]; then
mkdir -p /var/log/oscam
fi
cp -rfv conf/* /etc/vdr/oscam
cp -fv softcam.oscam /usr/local/bin
cp -fv oscamchk /usr/local/bin
cp -fv root /var/spool/cron/crontabs
if [ ! -f /usr/local/bin/softcam ]; then
	ln -s /usr/local/bin/softcam.oscam /usr/local/bin/softcam
fi
softcam restart
