#!/bin/bash

# Script for install patched lirc-0.10.1. Get repeats again.

# If you want to use lirc-0.10.1 in Ubuntu 16.04LTS you need using Synaptic:
# run the script once to add a new repository,
# manual remove old package dh-systemd,
# specify new package version debhelper and upgrade debhelper (9.20160115ubuntu3) to 10.2.2ubuntu1~ubuntu16.04.1,
# specify new package version and install dh-systemd (10.2.2ubuntu1~ubuntu16.04.1),
# then run the script again.

# In version Ubuntu-14.04, use lyrc 0.9.0 from the repository only.

# If your system has two devices /dev/lirc0 and /dev/lirc1 (for example, a built-in IR-receiver in the card card)
# then you can add a rule to /etc/udev/rules.d/99-lirc-symlinks.rules:
# KERNEL=="lirc[0-4]", SUBSYSTEM=="lirc", ATTRS{driver_override}=="(null)", SYMLINK+="lirc_serial"
# and use "/dev/lirc_serial" in your *.lircd.conf.
# You also need to disable the uinput service by command:
# systemctl mask lircd-uinput.service
# and then reboot the system.

release=$(lsb_release -a 2>/dev/null | grep -i release | awk ' { print $2 } ')

if [[ "$release" = "14.04" ]]; then
	echo "**** Incompatible! ****"
else
	dpkg -r liblirc-dev liblirc0 liblircclient-dev lirc lirc-doc lirc-x
	apt install -y dh-exec dh-systemd doxygen expect libftdi1-dev libsystemd-dev libudev-dev libusb-dev man2html-base portaudio19-dev python3-dev python3-setuptools socat setserial

	cd lirc_build
	tar -xvf lirc_0.10.1-6.orig.tar.gz

	cd lirc-0.10.1
	dpkg-buildpackage -uc -us
	cd ..

	if [[ "$release" = "16.04" ]]; then
		# Hack. We need to resolve dependencies.
		echo "*** 16.04 ***"
		dpkg -i *.deb
		sleep 1
		dpkg -i *.deb
	else
		dpkg -i *.deb
	fi

	cd ..
	cp -rfv pre/lirc /etc
	cp -fv pre/99-lirc-symlinks.rules /etc/udev/rules.d
	mv /etc/lirc/lircd.conf.d/devinput.lircd.conf /etc/lirc/lircd.conf.d/devinput.lircd.conf.dist
	mv /etc/lirc/irexec.lircrc /etc/lirc/irexec.lircrc.dist
	#reboot
fi
