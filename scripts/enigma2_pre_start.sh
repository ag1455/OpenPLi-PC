#!/bin/bash

# This is only for LCD!
#	ln -s /dev/fb0 /dev/fb1

sleep 5

#DVB_DEV="/dev/dvb/adapter0"

#if [ -d /sys/class/dvb/dvb0.frontend1 ]; then
#	rm $DVB_DEV/net1 $DVB_DEV/frontend1 $DVB_DEV/demux1 $DVB_DEV/dvr1 $DVB_DEV/net1
#fi

for i in $(find /dev/dvb -name demux0 | sed 's/.\{6\}$//')
	do
	echo "For $i"demux0" create symlink $i"demux1" "
	ln -s $i"demux0" $i"demux1"
	echo "For $i"dvr0" create symlink $i"dvr1" "
	ln -s $i"dvr0" $i"dvr1"
	done

# This is a bypass for kernel 4.18 bug. Module dvbsoftwareca already loaded by /etc/modules and must be reload.
	modprobe -r dvbsoftwareca
	modprobe dvbsoftwareca
	echo "dvbsoftwareca is restarted!" > /dev/null

sleep 1

	softcam restart &

exit 0
