#!/bin/sh

# This is only for LCD!
# ln -s /dev/fb0 /dev/fb1

DVB_DEV0="/dev/dvb/adapter0"
DVB_DEV1="/dev/dvb/adapter1"
LOG="/var/log/oscam/wait.log"

# Single with 1 frontend but named "1"
if [ -d /sys/class/dvb/dvb0.frontend0 ]; then
	ln -s $DVB_DEV0/frontend0 $DVB_DEV0/frontend1
	ln -s $DVB_DEV0/demux0 $DVB_DEV0/demux1
	ln -s $DVB_DEV0/dvr0 $DVB_DEV0/dvr1
	ln -s $DVB_DEV0/net0 $DVB_DEV0/net1
	ln -s $DVB_DEV0/ca0 $DVB_DEV0/ca1
fi

# Dual or 2 single with 1 frontend
if [ -d /sys/class/dvb/dvb1.frontend0 ]; then
	rm -f $DVB_DEV0/frontend1 $DVB_DEV0/demux1 $DVB_DEV0/dvr1 $DVB_DEV0/net1 $DVB_DEV0/ca1
	ln -s $DVB_DEV1/frontend0 $DVB_DEV1/frontend1
	ln -s $DVB_DEV1/demux0 $DVB_DEV1/demux1
	ln -s $DVB_DEV1/dvr0 $DVB_DEV1/dvr1
	ln -s $DVB_DEV1/net0 $DVB_DEV1/net1
	ln -s $DVB_DEV1/ca0 $DVB_DEV1/ca1
fi

if [ ! -f $LOG ]; then
	touch "$LOG"
fi

while [ 1 != 0 ]; do # The script will run in a loop until frontend0 appears.
	if [ $(ls $DVB_DEV0 | grep -w frontend0) ]; then
		modprobe -v dvbsoftwareca
		chmod 660 $DVB_DEV0/ca0
		chown root:video $DVB_DEV0/ca0
		sleep 10
		softcam start
#		echo " * Oscam started" >> $LOG
		exit 0
	else
#		echo " * Waiting ca0" >> $LOG
		sleep 1
	fi
done
