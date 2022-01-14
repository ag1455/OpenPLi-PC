#!/bin/bash

TH="/media/hdd/timeshift"
PREFIX="/usr/local/e2/bin"
DVB_DEV0="/dev/dvb/adapter0"
LOG="/var/log/oscam/wait.log"
FIFO="/tmp/ENIGMA_FIFO.sc"

# Uncomment this line in case of failure after a system upgrade or if ca0 doesn't appear.
#systemctl restart rc-local.service

#export DISPLAY=:0.0

if [ -f $TH/timeshift.* ]; then
	rm -f $TH/* # Case broken pause.
fi
if [ -f $TH/enigma2_crash_*.log ]; then
	mv -f $TH/enigma2_crash_*.log /tmp # Case hangs up.
fi
if [ -f $FIFO ]; then
	rm -f $FIFO
fi
sleep 2

if [ $(ls $DVB_DEV0 | grep -w ca0) ]; then
	if [ $(pgrep -n oscam) ]; then
		echo " * Oscam already started!"
	else
		softcam start
		echo " * Oscam started" >> $LOG
	fi
fi

while [ 1 != 0 ]; do
	# Start  enigma2.
	if [ $(ps -A | grep -c enigma2) -eq 0 ]; then
		sleep 3 # If you want to autostart from boot.
		# Case screensaver is enabled.
		xterm +ah -bg black -geometry 1x1 -e $PREFIX/enigma2.sh &
		xset -dpms
		xset s off
		exit 0
	else
		sleep 1
	fi
done
