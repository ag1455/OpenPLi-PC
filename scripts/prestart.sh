#!/bin/sh

# This is only for LCD!
# ln -s /dev/fb0 /dev/fb1

#if [ -d /sys/class/dvb/dvb0.frontend1 ]; then
#	rm $DVB_DEV/net1 $DVB_DEV/frontend1 $DVB_DEV/demux1 $DVB_DEV/dvr1 $DVB_DEV/net1
#fi

DVB_DEV="/dev/dvb/adapter0"
LOG="/var/log/oscam/wait.log"

if [ ! -f $LOG ]; then
	touch "$LOG"
fi

while [ 1 != 0 ]; do # The script will run in a loop until frontend0 appears.
	if [ $(ls $DVB_DEV | grep -w frontend0) ]; then
		ln -s $DVB_DEV/demux0 $DVB_DEV/demux1
		ln -s $DVB_DEV/dvr0 $DVB_DEV/dvr1
		modprobe -v dvbsoftwareca
		chmod 660 $DVB_DEV/ca0
		chown root:video $DVB_DEV/ca0
		sleep 10
		softcam start
#		echo " * Oscam started" >> $LOG
		exit 0
	else
#		echo " * Waiting ca0" >> $LOG
		sleep 1
	fi
done
