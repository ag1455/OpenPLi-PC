#!/bin/bash

SOURCE="oscam-patched"
CONF="/etc/vdr/oscam"
BIN="/usr/local/bin"

echo "-------------------------------------------"
echo "          *** INSTALL OSCAM ***"
echo "-------------------------------------------"

cd oscam

if [ -d $SOURCE ]; then
	rm -fr $SOURCE
fi

git clone https://github.com/oscam-emu/oscam-patched.git
cd $SOURCE
./config.sh -E WITH_SSL MODULE_CONSTCW
make

mv -v Distribution/*.debug Distribution/oscam.debug
cp -fv Distribution/oscam-* $BIN/oscam
cd ..

echo "-------------------------------------------"
echo "*** COPY CONFIG FILES in /etc/vdr/oscam ***"
echo "       *** EDIT DATA FOR YOU ***"
echo "-------------------------------------------"

if [ ! -d $CONF ]; then
	mkdir -p $CONF
fi

if [ ! -d /var/log/oscam ]; then
	mkdir -p /var/log/oscam
fi

cp -rfv conf/* $CONF
cp -fv softcam.oscam $BIN
cp -fv oscamchk $BIN
cp -fv root /var/spool/cron/crontabs

if [ ! -f $BIN/softcam ]; then
	ln -s $BIN/softcam.oscam $BIN/softcam
fi

if [ ! -f $CONF/SoftCam.Key ]; then
	ln -s /var/keys/SoftCam.Key $CONF
	ln -s /var/keys/AutoRoll.Key $CONF
	ln -s /var/keys/Autoupdate.Key $CONF
fi

softcam restart
