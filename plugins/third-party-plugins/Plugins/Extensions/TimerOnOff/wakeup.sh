#!/bin/sh
	wget -q http://root@localhost/web/powerstate -O - | fgrep -i true || exit
	wget -O /dev/null -q http://root@localhost/web/remotecontrol?command=116
	wget -qO - http://root@localhost/web/vol?set=up
	wget -qO - http://root@localhost/web/vol?set=setxx
