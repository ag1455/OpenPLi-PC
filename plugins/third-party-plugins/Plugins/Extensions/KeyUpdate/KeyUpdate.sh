#!/bin/sh

################################################################
# Title:.......KeyUpdate                                       #
# Author:......audi06_19    2018/2019                          #
# Support:.....www.dreamosat-forum.com                         #
# E-Mail:......admin@dreamosat-forum.com                       #
# Date:........26.11.2018                                      #
# Description:.KeyUpdate                                       #
################################################################

echo "=================================================="
echo "PLEASE WAIT"

URL="https://raw.githubusercontent.com/popking159/softcam/master"

TMP=`mktemp -d`
cd ${TMP}
[ -d /var/keys/ ] || mkdir -p /var/keys/

agent="--header='User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/600.1.17 (KHTML, like Gecko) Version/8.0 Safari/600.1.17'"
crt="--no-check-certificate"

wget -q $crt $agent $URL/SoftCam.Key

if [ -f ${TMP}/SoftCam.Key ] ; then
	chmod 0755 ${TMP}/SoftCam.Key -R
	if [ -f /var/keys/SoftCam.Key ] ; then
		check="/var/keys/SoftCam.Key"
	else
		echo "The SoftCam.Key file was not found.\n"
		echo "It was sent to the following folder."
		echo ": /var/keys/"
		check="/var/keys/SoftCam.Key"
	fi
	cp -rd ${TMP}/SoftCam.Key $check
else
	echo ""
	echo "Failed to download SoftCam.Key file !!!"
	echo ""
	rm -rf ${TMP} > /dev/null
	exit 0
fi

echo "SoftCam.Key file sent. $check"
echo ""
echo "SoftCam.Key updated. Do not forget to restart the EMU. good looking ..."
echo ""
echo "::: Thank you: by Serjoga :::"
echo "Support: www.dreamosat-forum.com "
echo "=================================================="
rm -rf ${TMP} > /dev/null
exit 0
