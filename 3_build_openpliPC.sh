#!/bin/bash

BACKUP_E2="etc/tuxbox/timezone.xml etc/tuxbox/satellites.xml etc/enigma2"

DO_BACKUP=1
DO_RESTORE=1
DO_XINE=1
DO_CONFIGURE=1
DO_PARALLEL=9
DO_MAKEINSTALL=1

INSTALL_E2DIR="/usr/local/e2"

e2_backup() {
echo ""
echo "********************************************************"
echo "                    BACKUP E2 CONFIG"
echo "********************************************************"
echo ""

# Wrevention of damage your old data
if [ -f $INSTALL_E2DIR/etc/enigma2/lamedb ]; then
	cp -fv $INSTALL_E2DIR/etc/enigma2/lamedb $INSTALL_E2DIR/etc/enigma2/lamedb~
	cp -fv $INSTALL_E2DIR/etc/enigma2/lamedb5 $INSTALL_E2DIR/etc/enigma2/lamedb5~
	cp -fv $INSTALL_E2DIR/etc/tuxbox/nim_sockets $INSTALL_E2DIR/etc/tuxbox/nim_sockets~
	cp -fv $INSTALL_E2DIR/etc/enigma2/settings $INSTALL_E2DIR/etc/enigma2/settings~
	cp -fv $INSTALL_E2DIR/etc/enigma2/profile $INSTALL_E2DIR/etc/enigma2/profile~
fi

if [ -d $INSTALL_E2DIR ]; then
	tar -C $INSTALL_E2DIR -vczf e2backup.tgz $BACKUP_E2
	echo ""
	echo "********************************************************"
	echo "           BACKUP COMPLITE. BUILDIND $PKG."
	echo "********************************************************"
else
	echo ""
	echo "********************************************************"
	echo "   NOTHING BACKUP. YOU FIRST INSTALL. BUILDIND $PKG."
	echo "********************************************************"
fi
}

e2_restore() {
echo ""
echo "********************************************************"
echo "                 RESTORE OLD E2 CONFIG."
echo "********************************************************"
echo ""

if [ -f e2backup.tgz ]; then
	tar -C $INSTALL_E2DIR -vxzf e2backup.tgz
fi
}

usage() {
echo "Usage:"
echo " -b : backup E2 conf file before re-compile"
echo " -r : restore E2 conf file after re-compile"
echo " -x : don't compile xine-lib (compile only enigma2)"
echo " -nc: don't start configure/autoconf"
echo " -py: parallel compile (y threads) e.g. -p2"
echo " -ni: only execute make and no make install"
echo " -h : this help"
echo ""
echo "common usage:"
echo "  $0 -b -r : make E2 backup, compile E2, restore E2 conf files"
echo ""
}

while [ "$1" != "" ]; do
	case $1 in
	-b ) DO_BACKUP=1
		shift
		;;
	-r ) DO_RESTORE=1
		shift
		;;
		-x ) DO_XINE=0
		shift
		;;
		-nc ) DO_CONFIGURE=0
		shift
		;;
	-ni ) DO_MAKEINSTALL=0
		shift
		;;
	-p* ) if [ "`expr substr "$1" 3 3`" = "" ]; then
		echo "Number threads is missing"
		usage
		exit
		else
		DO_PARALLEL=`expr substr "$1" 3 3`
	fi
		shift
		;;
		-h ) usage
		exit
		;;
		* ) echo "Unknown parameter $1"
		usage
		exit
		;;
	esac
done

if [ "$DO_BACKUP" -eq "1" ]; then
	e2_backup
fi

PKG="enigma2"

if [ -d $PKG ]; then
	cd $PKG
	make uninstall
	cd ..
	rm -rf $PKG
fi

rm -f $INSTALL_E2DIR/share/fonts/fallback.font

# W: this is unexpected line in the new xile-lib with gcc >= 6.x
rpl "//#define ENABLE_NLS" "#define ENABLE_NLS" /usr/include/xine/xineintl.h
rpl "//#define XINE_TEXTDOMAIN" "#define XINE_TEXTDOMAIN" /usr/include/xine/xineintl.h

git clone https://github.com/OpenPLi/$PKG.git
cd $PKG
git reset --hard 42fd2b44
cd ..
cp -fv $PKG/data/skin_display_default.xml $PKG/data/skin_display.xml

release=$(lsb_release -a 2>/dev/null | grep -i release | awk ' { print $2 } ')

if [[ "$release" = "14.04" ]]; then
	echo ""
	echo "********************************************************"
	echo "                 *** RELEASE 14.04 ***"
	echo "                  *** USED g++-6 ***"
	echo "        *** PICLOAD PATCH FOR 14.04 APPLIED.  ***"
	echo "********************************************************"
	echo ""
	export CXX=/usr/bin/g++-6
	cp patches/patch-42fd2b44-to-PC.patch $PKG
	cp patches/ubuntu-14.04.patch $PKG
	cd $PKG
	patch -p1 < patch-42fd2b44-to-PC.patch
	patch -p1 < ubuntu-14.04.patch
elif [[ "$release" = "16.04" ]]; then
	echo ""
	echo "********************************************************"
	echo "                 *** RELEASE 16.04 ***"
	echo "                  *** USED g++-7 ***"
	echo "********************************************************"
	echo ""
	export CXX=/usr/bin/g++-7
	cp patches/patch-42fd2b44-to-PC.patch $PKG
	cp patches/4_1X_kernel.patch $PKG
	cd $PKG
	patch -p1 < patch-42fd2b44-to-PC.patch
elif [[ "$release" = "18.04" ]]; then
	echo ""
	echo "********************************************************"
	echo "                 *** RELEASE 18.04 ***"
	echo "                  *** USED g++-7 ***"
	echo "********************************************************"
	export CXX=/usr/bin/g++-7
	cp patches/patch-42fd2b44-to-PC-sigc2.patch $PKG
	cp patches/4_1X_kernel.patch $PKG
	cd $PKG
	patch -p1 < patch-42fd2b44-to-PC-sigc2.patch
elif [[ "$release" = "19.04" ]]; then
	echo ""
	echo "********************************************************"
	echo "                 *** RELEASE 19.04 ***"
	echo "                  *** USED g++-8 ***"
	echo "********************************************************"
	echo ""
	export CXX=/usr/bin/g++-8
	cp patches/patch-42fd2b44-to-PC-sigc2.patch $PKG
	cp patches/4_1X_kernel.patch $PKG
	# This is just a hack. The configurator does't work in ubuntu-19.04 !
	cp -rfv  pre/.deps $PKG/lib
	# end hack
	cd $PKG
	patch -p1 < patch-42fd2b44-to-PC-sigc2.patch
fi

KERNEL=`uname -r | mawk -F. '{ printf("%d.%d\n",$1,$2); }'`

if [[ $KERNEL > "4.10" ]]; then
	echo ""
	echo "********************************************************"
	echo "                Your kernel is $KERNEL."
	echo "Since yor kernel > 4.1 X, 'dvbsoftwareca' patch must be"
	echo "applied."
	echo "Also necessary to replace the linux-headers video.h,"
	echo "audio.h and ca.h with the headers from this archive."
	echo "********************************************************"
	echo ""
	patch -p1 < 4_1X_kernel.patch
	cd ..
	cp -fv pre/dvb/* /usr/include/linux/dvb
	cp -fv pre/dvb/* /usr/src/linux-headers-$KERNEL*/include/uapi/linux/dvb
	echo ""
	cd $PKG
else
	echo ""
	echo "********************************************************"
	echo "                 Your kernel is $KERNEL."
	echo "            No additional patches required."
	echo "********************************************************"
	echo ""
fi

if [ "$DO_CONFIGURE" -eq "1" ]; then
	echo "********************************************************"
	echo " Configuring OpenPliPC $PKG with native lirc support."
	echo "   Please edit $INSTALL_E2DIR/etc/enigma2/remote.conf."
	echo "       Build OpenPliPC $PKG, please wait..."
	echo "********************************************************"
	echo ""
	# Create symlinks in /usr diectory before compile enigma2
	if [ ! -d /usr/include/netlink ]; then
		ln -s /usr/include/libnl3/netlink /usr/include
	fi
#	autoupdate
#	autoreconf -v -f -i -W all
	autoreconf -i
#	./configure --prefix=$INSTALL_E2DIR --with-xlib --with-fbdev=/dev/fb0 --with-boxtype=generic
	./configure --prefix=$INSTALL_E2DIR --with-xlib --with-libsdl=no --with-boxtype=nobox --enable-dependency-tracking ac_cv_prog_c_openmp=-fopenmp --with-gstversion=1.0 --with-textlcd
	# generate pot
	#./configure --prefix=$INSTALL_E2DIR --with-xlib --with-debug --with-po
fi

if [ "$DO_MAKEINSTALL" -eq "0" ]; then
	make -j"$DO_PARALLEL" CXXFLAGS=-std=c++11
	if [ ! $? -eq 0 ]; then
		echo ""
	echo "*********************************************************"
	echo "AN ERROR OCCURED WHILE BUILDING OpenPliPC - SECTION MAKE!"
	echo "*********************************************************"
		echo ""
		exit
	fi
	else
	echo ""
	echo "********************************************************"
	echo "          INSTALLING $PKG IN $INSTALL_E2DIR."
	echo "********************************************************"
	echo ""
	make uninstall
	make -j"$DO_PARALLEL" install
	if [ ! $? -eq 0 ]; then
		echo ""
		echo "*****************************************************************"
		echo "AN ERROR OCCURED WHILE BUILDING OpenPliPC - SECTION MAKE INSTALL!"
		echo "*****************************************************************"
		echo ""
		exit
	fi
fi

# Remove old kernel module
modprobe -r dvbsoftwareca
rm /dev/dvb/adapter0/dvr1
rm /dev/dvb/adapter0/demux1

# Make dvbsoftwareca
cd dvbsoftwareca
make -j"$DO_PARALLEL"
if [ ! $? -eq 0 ]; then
	echo ""
	echo "******************************************************************"
	echo "AN ERROR OCCURED WHILE BUILDING OpenPliPC - SECTION DVBSOFTWARECA!"
	echo "******************************************************************"
	echo ""
	exit
fi
cp -fv dvbsoftwareca.ko /lib/modules/`uname -r`/kernel/drivers/media/dvb-frontends
depmod -a

# Insert module dvbsoftwareca and create symlink
if [ $(lsmod | grep -c dvbsoftwareca) -eq 0 ]; then
	modprobe dvbsoftwareca
	ln -s /dev/dvb/adapter0/dvr0 /dev/dvb/adapter0/dvr1
	ln -s /dev/dvb/adapter0/demux0 /dev/dvb/adapter0/demux1
fi

cd ../..

echo ""
echo "********************************************************"
echo "          FINAL STEP: INSTALLING E2 CONF FILES."
echo "********************************************************"
echo ""

# Remove unused plugins
rm -rf /usr/local/e2/lib/enigma2/python/Plugins/SystemPlugins/VideoEnhancement
rm -rf $INSTALL_E2DIR/lib/enigma2/python/Plugins/SystemPlugins/SoftwareManager

# Create symlinks in /usr diectory post install enigma2 and copying needed files
mkdir -p $INSTALL_E2DIR/etc
mkdir -p /home/hdd/movies
mkdir -p /usr/local/etc
if [ ! -d /home/hdd/movie ]; then
	ln -s /home/hdd/movies /home/hdd/movie
fi
if [ ! -d /media/hdd ]; then
	ln -s /home/hdd /media
fi
if [ ! -d  /usr/local/etc/stb ]; then
	ln -s $INSTALL_E2DIR/etc/stb /usr/local/etc/stb
fi
if [ ! -d /etc/enigma2 ]; then
	ln -s $INSTALL_E2DIR/etc/enigma2 /etc
fi
if [ ! -d /etc/tuxbox ]; then
	ln -s $INSTALL_E2DIR/etc/tuxbox /etc
fi
if [ ! -d /usr/local/lib/enigma2 ]; then
	ln -s $INSTALL_E2DIR/lib/enigma2 /usr/local/lib
fi
if [ ! -d /usr/lib/enigma2 ]; then
	ln -s $INSTALL_E2DIR/lib/enigma2 /usr/lib
fi
if [ ! -d /usr/local/share/enigma2 ]; then
	ln -s $INSTALL_E2DIR/share/enigma2 /usr/local/share
fi
if [ ! -d /usr/share/enigma2 ]; then
	ln -s $INSTALL_E2DIR/share/enigma2 /usr/share
fi
if [ ! -d /usr/include/enigma2 ]; then
	ln -s $INSTALL_E2DIR/include/enigma2 /usr/include
fi
if [ ! -f /usr/local/bin/enigma2.sh ]; then
	ln -sf $INSTALL_E2DIR/bin/enigma2.sh /usr/local/bin
fi
if [ ! -f ./e2bin ]; then
	ln -sf $INSTALL_E2DIR/bin/enigma2 ./e2bin
fi

# Create symlinks in /lib diectory post install enigma2
if [ ! -f /lib/libc.so.6 ]; then
	ARCH_MY=`uname -i`
	ln -s `ls /lib/"$ARCH_MY"-linux-gnu/libc-2.??.so` /lib/libc.so.6
fi
if [ -d /lib/i386-linux-gnu ]; then
	if [ ! -d /lib/i686-linux-gnu ]; then
	ln -s /lib/i386-linux-gnu /lib/i686-linux-gnu
	fi
fi

# Strip binary
strip $INSTALL_E2DIR/bin/enigma2

# Use xine.conf for vaapi
GPU=`lspci 2>/dev/null | grep -E "VGA|3D" | grep -Eiwo "NVIDIA|INTEL|ATI"`
if [ $GPU == "Intel" ]; then
	echo ""
	echo "********************************************************"
	echo "                  YOUR HAVE VAAPI GPU!"
	echo "                USED xine.conf FOR VAAPI!"
	echo "********************************************************"
	echo ""
	mv -f /usr/local/e2/share/enigma2/xine.conf.vaapi /usr/local/e2/share/enigma2/xine.conf
fi

# Copy missing headers
cp -fv enigma2/lib/gdi/gxlibdc.h $INSTALL_E2DIR/include/enigma2/lib/gdi
cp -fv enigma2/lib/gdi/gmaindc.h $INSTALL_E2DIR/include/enigma2/lib/gdi
cp -fv enigma2/lib/gdi/xineLib.h $INSTALL_E2DIR/include/enigma2/lib/gdi
cp -fv enigma2/lib/gdi/post.h $INSTALL_E2DIR/include/enigma2/lib/gdi

# Copy files
cd pre
cp -rfv enigma2 $INSTALL_E2DIR/etc
cp -rfv stb $INSTALL_E2DIR/etc
cp -rfv tuxbox $INSTALL_E2DIR/etc
cp -fv rc.local /etc
cp -fv enigmasquared.jpg $INSTALL_E2DIR/share/enigma2
cp -fv enigmasquared2.jpg $INSTALL_E2DIR/share/enigma2
cp -fv xine.conf $INSTALL_E2DIR/share/enigma2
cp -fv xine.conf.vaapi $INSTALL_E2DIR/share/enigma2
cp -fv logo.mvi $INSTALL_E2DIR/share/enigma2
cp -fv e2pc.desktop ~/.local/share/applications
cp -fv kill_e2pc.desktop ~/.local/share/applications
cp -fv modules /etc
cd ..
cp -fv scripts/* $INSTALL_E2DIR/bin
cp -fv /etc/NetworkManager/NetworkManager.conf /etc/NetworkManager/NetworkManager.conf~
cp -fv /etc/network/interfaces /etc/network/interfaces~
ln -sv /etc/modules /etc/modules-load.d/modules.conf

# Create symlink for tuxtxt font
if [ ! -f $INSTALL_E2DIR/share/fonts/tuxtxt.otb ]; then
	ln -s /usr/share/fonts/tuxtxt.otb $INSTALL_E2DIR/share/fonts/tuxtxt.otb
fi
if [ ! -f $INSTALL_E2DIR/share/fonts/tuxtxt.ttf ]; then
	ln -s /usr/share/fonts/tuxtxt.otb $INSTALL_E2DIR/share/fonts/tuxtxt.ttf
fi

# Removing compiled now pyo or pyc files
find $INSTALL_E2DIR/lib/enigma2/python/ -name "*.py[o]" -exec rm {} \;

# Restore
if [ "$DO_RESTORE" -eq "1" ]; then
	e2_restore
fi

# Disable screensaver
gsettings set org.gnome.desktop.lockdown disable-lock-screen 'true'
gsettings set org.gnome.desktop.screensaver lock-enabled false
gsettings set org.gnome.desktop.screensaver idle-activation-enabled false
# Test result
echo "disable-lock-screen:"
gsettings get org.gnome.desktop.lockdown disable-lock-screen
echo "lock-enabled:"
gsettings get org.gnome.desktop.screensaver lock-enabled
echo "idle-activation-enabled:"
gsettings get org.gnome.desktop.screensaver idle-activation-enabled
echo ""
echo "********************************************************"
echo "If you want to return screensaver back, then you must"
echo "do the opposite as user, but not as root."
echo "********************************************************"
echo ""

echo ""
echo "********************************************************"
echo "            AUTOMATIC CREATION nim_sockets."
echo "********************************************************"
echo ""

cd util
./build_create_nim_sockets.sh
./create_nim_sockets -d
mv nim_sockets $INSTALL_E2DIR/etc/tuxbox
cd ..

echo ""
echo "********************************************************"
echo "      Enigma2PC and folders installed successfully."
echo "    If you have own settings, then they are restored."
echo ""
echo "                    Now check please:"
echo "           /usr/local/e2/etc/tuxbox/nim_sockets"
echo "      according to your /dev/dvb/adapter?/frontend?"
echo ""
echo ""
echo "         Example for dvb-S2 card in one slot:"
echo "                   NIM Socket 0:"
echo "                   Type DVB-S2"
echo "                   Name: YOURCARDNAME"
echo "                   Has_Outputs: no"
echo "                   Frontend_Device: 0"
echo ""
echo ""
echo "         Example for dvb-Т2 card in one slot:"
echo "                   NIM Socket 0:"
echo "                   Type: DVB-T2"
echo "                   Name: YOURCARDNAME"
echo "                   Has_Outputs: no"
echo "                   Frontend_Device: 0"
echo ""
echo ""
echo " Example for dvb-S2/T2 card in one or different slots:"
echo "                   NIM Socket 0:"
echo "                   Type DVB-S2"
echo "                   Name: YOURCARDNAME"
echo "                   Has_Outputs: no"
echo "                   Frontend_Device: 0"
echo ""
echo "                   NIM Socket 1:"
echo "                   Type: DVB-T2"
echo "                   Name: YOURCARDNAME"
echo "                   Has_Outputs: no"
echo "                   Frontend_Device: 1"
echo ""
echo ""
echo "      At the first start you can skip the network"
echo "  configuration, since this is already set in Ubuntu."
echo "********************************************************"