#!/bin/sh
	wget -q http://root@localhost/web/powerstate -O - | fgrep -i false || exit
	wget -O /dev/null -q http://root@localhost/web/powerstate?newstate=0
