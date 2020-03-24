#!/bin/sh

HDD="/media/hdd"
PREFIX="/usr/local/e2/bin"

#systemctl restart rc-local.service # Uncomment this line in case of failure after a system upgrade or if ca0 doesn't appear.
rm -f $HDD/timeshift.* # Case broken pause.

while [ 1 != 0 ]; do
	# Start  enigma2.
	if [ $(ps -A | grep -c enigma2) -eq 0 ]; then
		sleep 2 # If you want to autostart from boot.
		# Case screensaver is enabled.
		xterm -bg black -geometry 1x1 -e $PREFIX/enigma2.sh &
		xset -dpms
		xset s off
		exit 0
	else
		sleep 1
	fi
done
