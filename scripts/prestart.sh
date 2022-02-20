#!/bin/sh

# This is only for LCD!
# ln -s /dev/fb0 /dev/fb1

DVB_DEV0="/dev/dvb/adapter0"
LOG="/var/log/oscam/wait.log"

# Case single with 1 frontend but named "1"
#if [ -d /sys/class/dvb/dvb0.frontend0 ]; then
#	ln -s $DVB_DEV0/frontend0 $DVB_DEV0/frontend1
#	ln -s $DVB_DEV0/demux0 $DVB_DEV0/demux1
#	ln -s $DVB_DEV0/dvr0 $DVB_DEV0/dvr1
#fi

if [ ! -f $LOG ]; then
	touch $LOG
else
	rm -f $LOG
	touch $LOG
fi

while [ 1 != 0 ]; do # The script will run in a loop until appears frontend0.
	if [ $(ls $DVB_DEV0 | grep -w frontend0) ]; then
		modprobe -v dvbsoftwareca
#		chmod 660 $DVB_DEV0/ca0
#		chown root:video $DVB_DEV0/ca0
		echo " * Started ca0" >> $LOG
		exit 0
	else
		echo " * Waiting ca0" >> $LOG
		sleep 1
	fi
done
