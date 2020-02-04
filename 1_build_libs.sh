#!/bin/bash

# To build enigma2 on Ubuntu 14.04 (32/64-bit), 16.04 (32/64-bit), 18.04 (64-bit), 19.04 (64-bit), 19.10 (64-bit).
# Install these packages:

echo "-----------------------------------------"
echo "*** INSTALL REQUIRED PACKAGES ***"
echo "-----------------------------------------"

release=$(lsb_release -a 2>/dev/null | grep -i release | awk ' { print $2 } ')

REQPKG_ALL="ant aptitude autoconf automake autopoint avahi-daemon bash build-essential checkinstall chrpath cmake coreutils cvs debhelper desktop-file-utils docbook-utils \
	diffstat dropbear dvb-apps dvdbackup ethtool fakeroot flex ffmpeg gawk gettext git help2man linux-headers-`uname -r` libdvdnav-dev libfreetype6-dev libfribidi-dev \
	libpcsclite-dev libjpeg8-dev libgif-dev libjpeg-turbo8-dev libgiftiio0 libaio-dev libxinerama-dev libxt-dev libasound2-dev libcaca-dev libpulse-dev libvorbis-dev \
	libgtk2.0-dev libtool libxml2-dev libxml2-utils libxslt1-dev libssl-dev libvdpau-dev libcdio-dev libcrypto++-dev libudf-dev libvcdinfo-dev libusb-1.0-0-dev \
	libavcodec-dev libavformat-dev libpostproc-dev libavutil-dev libnl-3-dev libbluray-dev libmpcdec-dev libvpx-dev libnl-genl-3-dev libavahi-client3 libavahi-client-dev \
	libflac-dev libogg-dev libdts-dev libxcb-xv0-dev libxcb-shape0-dev libxv-dev libxvmc-dev libaa1-dev libmodplug-dev libjack-jackd2-dev libdirectfb-dev libmagickwand-dev \
	libwavpack-dev libspeex-dev libmng-dev libmad0-dev librsvg2-bin libtheora-dev libsmbclient-dev liblircclient-dev librtmp1 libmng2 libx11-6 libxext6 libglib2.0-dev \
	libelf-dev libmysqlclient-dev libupnp-dev libgiftiio-dev libgstreamer-plugins-base1.0-dev libgstreamer1.0-dev gstreamer1.0-libav mawk mercurial mingetty mock \
	mjpegtools net-tools ntpdate openssh-sftp-server pmccabe python-dev python-setuptools python-twisted python-twisted-web python-twisted-mail python-ipaddr \
	python-ipaddress python-pysqlite2 python-cryptography-vectors python-flickrapi python-lzma python-mechanize python-mutagen python-netifaces python-pyasn1-modules \
	python-pycryptopp python-sendfile python-simplejson python-pycurl python-pil python-bzrlib python-urllib3 python-openssl python-cheetah python-blessings python-httpretty \
	patch pyflakes pkg-config rpl rsyslog rtmpdump sdparm setserial smartmontools software-properties-common sphinx-common streamripper subversion texi2html texinfo unclutter unzip \
	uchardet youtube-dl w3m vsftpd xmlto xterm \
	"

for p in $REQPKG_ALL; do
	echo -n ">>> Checking \"$p\" : "
	dpkg -s $p >/dev/null
	if [[ "$?" -eq "0" ]]; then
		echo "package is installed, skip it"
	else
		echo "package NOT present, installing it"
		apt-get -y install $p
	fi
done

if [[ "$release" = "14.04" ]]; then
	echo ""
	echo "********************************************************"
	echo "                 *** release 14.04 ***                  "
	echo "********************************************************"
	echo ""
	if [ ! -f /etc/apt/sources.list.d/ubuntu-cloud-archive-liberty-staging-trusty.list ]; then
	add-apt-repository -y ppa:ubuntu-cloud-archive/liberty-staging
	apt-get update
	fi
	if [ ! -f /etc/apt/sources.list.d/ubuntu-toolchain-r-test-trusty.list ]; then
	add-apt-repository -y ppa:ubuntu-toolchain-r/test
	apt-get update
	fi
	REQPKG="flake gcc-6 g++-6 libgnomevfs2-dev libssl1.0.0 libsdl1.2-dev libpng12-dev libsigc++-1.2-dev libesd0-dev libva-dev libqtgstreamer-dev libupnp6-dev python-ntplib \
	python-daap python-transmissionrpc python-yenc python-gdata python-demjson swig2.0 \
	"
elif [[ "$release" = "16.04" ]]; then
	echo ""
	echo "********************************************************"
	echo "                 *** release 16.04 ***                  "
	echo "********************************************************"
	echo ""
	if [ ! -f /etc/apt/sources.list.d/ubuntu-toolchain-r-ubuntu-test-xenial.list ]; then
	add-apt-repository -y ppa:ubuntu-toolchain-r/test
	apt-get update
	fi
	REQPKG="flake8 gcc-7 g++-7 libgnomevfs2-dev libssl1.0.0 libsdl1.2-dev libesd0-dev libpng12-dev libsigc++-1.2-dev python-subprocess32 libva-dev libqt5gstreamer-dev \
	python-cryptodome python-pickleshare python-service-identity python-certifi python-restructuredtext-lint python-ntplib pylint python-daap python-transmissionrpc \
	python-yenc python-gdata python-demjson sphinx-rtd-theme-common libupnp6-dev swig2.0 yamllint \
	"
elif [[ "$release" = "18.04" ]]; then
	echo ""
	echo "********************************************************"
	echo "                 *** release 18.04 ***                  "
	echo "********************************************************"
	echo ""
	REQPKG="flake8 gcc-7 g++-7 libgnomevfs2-dev libssl1.1 libsdl2-dev libpng-dev libsigc++-2.0-dev libqt5gstreamer-dev python-subprocess32 python-langdetect python-pycryptodome \
	python-pickleshare pycodestyle python-service-identity python-certifi python-restructuredtext-lint python-daap python-ntplib python-transmissionrpc python-yenc python-gdata \
	python-demjson pylint sphinx-rtd-theme-common libupnp6-dev swig yamllint \
	"
elif [[ "$release" = "19.04" ]]; then
	echo ""
	echo "********************************************************"
	echo "                 *** release 19.04 ***                  "
	echo "********************************************************"
	echo ""
	REQPKG="flake8 gcc-8 g++-8 libssl1.1 libsdl2-dev libpng-dev libsigc++-2.0-dev libqt5gstreamer-dev python-subprocess32 python-langdetect python-pycryptodome python-pickleshare \
	pycodestyle python-service-identity python-certifi python-restructuredtext-lint python3-ntplib python3-transmissionrpc python-sabyenc python3-demjson pylint sphinx-rtd-theme-common \
	libupnp-dev swig swig3.0 yamllint \
	"
elif [[ "$release" = "19.10" ]]; then
	echo ""
	echo "********************************************************"
	echo "                 *** release 19.10 ***                  "
	echo "********************************************************"
	echo ""
	REQPKG="flake8 gcc-9 g++-9 libssl1.1 libsdl2-dev libpng-dev libsigc++-2.0-dev libqt5gstreamer-dev python-subprocess32 python-langdetect python-pycryptodome python-pickleshare \
	pycodestyle python-service-identity python-certifi python-restructuredtext-lint python3-ntplib python3-transmissionrpc python-sabyenc python3-demjson pylint sphinx-rtd-theme-common \
	libupnp-dev swig swig3.0 yamllint \
	"
fi

for p in $REQPKG; do
	echo -n ">>> Checking \"$p\" : "
	dpkg -s $p >/dev/null
	if [[ "$?" -eq "0" ]]; then
		echo "package is installed, skip it"
	else
		echo "package NOT present, installing it"
		apt-get -y install $p
	fi
done

cp -fv pre/sitecustomize.py /usr/local/lib/python2.7/site-packages

# Download dvb-firmwares
wget https://bitbucket.org/CrazyCat/media_build/downloads/dvb-firmwares.tar.bz2
tar -xvjf dvb-firmwares.tar.bz2 -C /lib/firmware
rm -f dvb-firmwares.tar.bz2

BUILD_DIR="libs"
if [ -d $BUILD_DIR ]; then
	rm -rf $BUILD_DIR
fi
mkdir $BUILD_DIR
cd $BUILD_DIR

# Build and install libdvbsi++-git:
LIB="libdvbsi++1"
#PKG="libdvbsi-"
PKG="libdvbsi++"
echo "-----------------------------------------"
echo "Build and install $LIB"
echo "-----------------------------------------"
I=`dpkg -s $LIB | grep "Status"`
if [ -n "$I" ]; then
	dpkg -r libdvbsi++1 libdvbsi++-dev
else
	echo "$LIB not installed"
fi
#git clone https://github.com/OpenDMM/$PKG.git
git clone git://git.opendreambox.org/git/obi/$PKG.git
cd $PKG
git checkout 64efce61
cd ../..
cp patches/fix_section_len_check.patch libs/$PKG
cp patches/ac3_descriptor-check-if-header-is-larger-than-descri.patch libs/$PKG
cd libs/$PKG
patch -p1 < fix_section_len_check.patch
patch -p1 < ac3_descriptor-check-if-header-is-larger-than-descri.patch
echo "-----------------------------------------"
echo "      Patch for libdvbsi++ applied       "
echo "-----------------------------------------"
#autoupdate
dpkg-buildpackage -uc -us
cd ..
mv libdvbsi++*.* $PKG
cd $PKG
dpkg -i *.deb
	cd ..

# Build and install libxmlccwrap-git:
if [ ! -f libdvbsi++/*.deb ]; then
	set -e
	set -o pipefail
else
	echo ""
	echo "**************************** OK. Go to the next step. ******************************"
	echo ""
	PKG="libxmlccwrap"
	echo "-----------------------------------------"
	echo "Build and install $PKG"
	echo "-----------------------------------------"
	I=`dpkg -s $PKG | grep "Status"`
	if [ -n "$I" ]; then
		dpkg -r libxmlccwrap libxmlccwrap-dev
	else
		echo "$PKG not installed"
	fi
	git clone https://github.com/OpenDMM/$PKG.git
#	git clone git://git.opendreambox.org/git/obi/$PKG.git
	cd $PKG
	rpl '(= ${Source-Version})' '(= ${binary:Version})' debian/control
#	autoupdate
	dpkg-buildpackage -uc -us
	cd ..
	mv libxmlccwrap*.* $PKG
	cd $PKG
	dpkg -i *.deb
	cd ..
fi

# Build and install libdvbcsa-git:
if [ ! -f libxmlccwrap/*.deb ]; then
	set -e
	set -o pipefail
else
	echo ""
	echo "**************************** OK. Go to the next step. ******************************"
	echo ""
	PKG="libdvbcsa"
	echo "-----------------------------------------"
	echo "Build and install $PKG"
	echo "-----------------------------------------"
	I=`dpkg -s $PKG | grep "Status"`
	if [ -n "$I" ]; then
		dpkg -r libdvbcsa libdvbcsa-dev tsdecrypt
	else
		echo "$PKG not installed"
	fi
	git clone https://code.videolan.org/videolan/$PKG.git
	cd $PKG
	git checkout bc6c0b16
	./bootstrap
	./configure --prefix=/usr --enable-sse2
	checkinstall -D --install=yes --default --pkgname=libdvbcsa --pkgversion=1.1.0 --maintainer=e2pc@gmail.com --pkggroup=video --autodoinst=yes --gzman=yes
	cd ..
fi

# Build and install libtuxtxt and tuxtxt:
if [ ! -f libdvbcsa/*.deb ]; then
	set -e
	set -o pipefail
else
	echo ""
	echo "**************************** OK. Go to the next step. ******************************"
	echo ""
	INSTALL_E2DIR="/usr/local/e2"
	INSTALL_LIB="/usr"
	SOURCE="tuxtxt-git"
	PKG1="libtuxtxt"
	PKG2="tuxtxt"
	if [ ! -d $INSTALL_E2DIR ]; then
		mkdir -p $INSTALL_E2DIR/lib/enigma2
	fi
	if [ -d $SOURCE ]; then
		dpkg -r libtuxtxt tuxtxt
		rm -rf $SOURCE
	fi
	if [ ! -d $INSTALL_LIB/lib/enigma2 ]; then
	ln -s $INSTALL_E2DIR/lib/enigma2 $INSTALL_LIB/lib/enigma2
	fi
	git clone https://github.com/OpenPLi/tuxtxt.git tuxtxt-git
	cd ..
	cp patches/tuxtxt.patch libs/$SOURCE
	cd libs/$SOURCE
	git checkout fa18f775
	patch -p1 < tuxtxt.patch
	echo "-----------------------------------------"
	echo " patches for tuxtxt and libtuxtxt applied"
	echo "-----------------------------------------"
	cd $PKG1
#	autoupdate
	autoreconf -i
	./configure --prefix=$INSTALL_LIB --with-boxtype=generic DVB_API_VERSION=5
	checkinstall -D --install=yes --default --pkgname=libtuxtxt --pkgversion=1.0 --maintainer=e2pc@gmail.com --pkggroup=video --autodoinst=yes --gzman=yes
	cd ..
fi

if [ ! -f libtuxtxt/*.deb ]; then
	set -e
	set -o pipefail
else
	echo ""
	echo "**************************** OK. Go to the next step. ******************************"
	echo ""
	cd $PKG2
#	autoupdate
	autoreconf -i
	./configure --prefix=$INSTALL_LIB --with-boxtype=generic --with-configdir=/usr/etc --with-fbdev=/dev/fb0 --with-textlcd DVB_API_VERSION=5
	checkinstall -D --install=yes --default --pkgname=tuxtxt --pkgversion=1.0 --maintainer=e2pc@gmail.com --pkggroup=video --autodoinst=yes --gzman=yes
	find $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/Tuxtxt -name "*.py[o]" -exec rm {} \;
	cd ../..
fi

# Build and install aio-grab-git:
if [ ! -f tuxtxt-git/tuxtxt/*.deb ]; then
	set -e
	set -o pipefail
else
	echo ""
	echo "**************************** OK. Go to the next step. ******************************"
	echo ""
	PKG="aio-grab"
	echo "-----------------------------------------"
	echo "Build and install $PKG"
	echo "-----------------------------------------"
	I=`dpkg -s $PKG | grep "Status"`
	if [ -n "$I" ]; then
		dpkg -r aio-grab
	else
		echo "$PKG not installed"
	fi
	git clone https://github.com/OpenPLi/aio-grab.git
	cd ..
	cp patches/aio-grab.patch libs/$PKG
	cd libs/$PKG
	git checkout c79e2641
	patch -p1 < aio-grab.patch
	autoreconf -i
	./configure --prefix=/usr
	checkinstall -D --install=yes --default --pkgname=aio-grab --pkgversion=1.0 --maintainer=e2pc@gmail.com --pkggroup=video --autodoinst=yes --gzman=yes
	cd ..
fi

# Build and install gst-plugin-dvbmediasink-git:
if [ ! -f aio-grab/*.deb ]; then
	set -e
	set -o pipefail
else
	echo ""
	echo "**************************** OK. Go to the next step. ******************************"
	echo ""
	LIB="libgstreamer-plugins-dvbmediasink"
	PKG="gst-plugin-dvbmediasink"
	echo "-----------------------------------------"
	echo "Build and install $LIB"
	echo "-----------------------------------------"
	I=`dpkg -s $LIB | grep "Status"`
	if [ -n "$I" ]; then
		dpkg -r $LIB
	else
		echo "$LIB not installed"
	fi
	git clone https://github.com/openpli/gst-plugin-dvbmediasink.git
	cd $PKG
	if [[ "$release" = "14.04" ]]; then
		git checkout 4ace22cf
		cd ../..
		cp patches/dvbmediasink-0.10.patch libs/$PKG
		cd libs/$PKG
		patch -p1 < dvbmediasink-0.10.patch
		echo "-----------------------------------------"
		echo "      Patch for dvbmediasink applied     "
		echo "-----------------------------------------"
#		autoupdate
		autoreconf -i
		./configure --prefix=/usr --with-wma --with-wmv --with-pcm --with-dtsdownmix --with-eac3 --with-mpeg4 --with-mpeg4v2 --with-h263 --with-h264 --with-h265
		checkinstall -D --install=yes --default --pkgname=libgstreamer-plugins-dvbmediasink --pkgversion=0.10.0 --maintainer=e2pc@gmail.com --pkggroup=video --autodoinst=yes --gzman=yes
	else
		git checkout 12511897
		cd ../..
		cp patches/dvbmediasink-1.0.patch libs/$PKG
		cd libs/$PKG
		patch -p1 < dvbmediasink-1.0.patch
		echo "-----------------------------------------"
		echo "      Patch for dvbmediasink applied     "
		echo "-----------------------------------------"
#		autoupdate
		autoreconf -i
		./configure --prefix=/usr --with-wma --with-wmv --with-pcm --with-dtsdownmix --with-eac3 --with-mpeg4 --with-mpeg4v2 --with-h263 --with-h264 --with-h265
		checkinstall -D --install=yes --default --pkgname=libgstreamer-plugins-dvbmediasink --pkgversion=0.10.0 --maintainer=e2pc@gmail.com --pkggroup=video --autodoinst=yes --gzman=yes
	fi
	cd ..
fi

# Build and install gst-plugin-subsink-git:
if [ ! -f gst-plugin-dvbmediasink/*.deb ]; then
	set -e
	set -o pipefail
else
	echo ""
	echo "**************************** OK. Go to the next step. ******************************"
	echo ""
	LIB="libgstreamer-plugins-subsink"
	PKG="gst-plugin-subsink"
	echo "-----------------------------------------"
	echo "Build and install $LIB"
	echo "-----------------------------------------"
	I=`dpkg -s $LIB | grep "Status"`
	if [ -n "$I" ]; then
		dpkg -r $LIB
	else
		echo "$LIB not installed"
	fi
		git clone https://github.com/OpenPLi/gst-plugin-subsink.git
		cd $PKG
		git checkout 2c4288bb
		echo "AC_CONFIG_MACRO_DIR([m4])" >> configure.ac
	if [[ "$release" = "14.04" ]]; then
#		autoupdate
		autoreconf -i
		./configure --prefix=/usr
		checkinstall -D --install=yes --default --pkgname=libgstreamer-plugins-subsink --pkgversion=0.10.0 --maintainer=e2pc@gmail.com --pkggroup=video --autodoinst=yes --gzman=yes
	else
		cd ../..
		cp patches/subsink_1.0.patch libs/$PKG
		cd libs/$PKG
		patch -p1 < subsink_1.0.patch
		echo "-----------------------------------------"
		echo "    Patch for subsink_1.0.patch applied  "
		echo "-----------------------------------------"
#		autoupdate
		autoreconf -i
		./configure --prefix=/usr
		checkinstall -D --install=yes --default --pkgname=libgstreamer-plugins-subsink --pkgversion=1.0 --maintainer=e2pc@gmail.com --pkggroup=video --autodoinst=yes --gzman=yes
	fi
	cd ..
fi

# Build and install libdreamdvd-git:
if [ ! -f gst-plugin-subsink/*.deb ]; then
	set -e
	set -o pipefail
else
	echo ""
	echo "**************************** OK. Go to the next step. ******************************"
	echo ""
	LIB="libdreamdvd-dev"
	PKG="libdreamdvd"
	echo "-----------------------------------------"
	echo "Build and install $PKG"
	echo "-----------------------------------------"
	I=`dpkg -s $LIB | grep "Status"`
	if [ -n "$I" ]; then
		dpkg -r libdreamdvd0 libdreamdvd-dev
	else
		echo "$PKG not installed"
	fi
	git clone https://github.com/mirakels/$PKG.git
	cd ..
	cp patches/libdreamdvd.patch libs/$PKG
	cd libs/$PKG
	git checkout 02a0e7cb
	patch -p1 < libdreamdvd.patch
	if [[ "$release" = "14.04" ]]; then #for very old Ubuntu-14.04
		export CFLAGS="-std=c99" #switch to с99
		dpkg-buildpackage -uc -us
		export CFLAGS="-std=c11" #return
	else
#	autoupdate
	dpkg-buildpackage -uc -us
	fi
	cd ..
	mv libdreamdvd*.* $PKG
	cd $PKG
	dpkg -i $PKG*.deb
	cd ..
fi

# Build and install pythonwifi-git:
if [ ! -f libdreamdvd/*.deb ]; then
	set -e
	set -o pipefail
else
	echo ""
	echo "**************************** OK. Go to the next step. ******************************"
	echo ""
	PKG="pythonwifi"
	echo "-----------------------------------------"
	echo "Build and install $PKG"
	echo "-----------------------------------------"
	git clone git://github.com/pingflood/$PKG
	cd $PKG
	python setup.py install
	cd ..
	rm -f /usr/local/INSTALL
	rm -f /usr/local/README
fi

# Build and install TwistedSNMP-0.3.13:
if [ ! -d pythonwifi ]; then
	set -e
	set -o pipefail
else
	echo ""
	echo "**************************** OK. Go to the next step. ******************************"
	echo ""
	PKG="TwistedSNMP-0.3.13"
	echo "-----------------------------------------"
	echo "Build and install $PKG"
	echo "-----------------------------------------"
	wget https://sourceforge.net/projects/twistedsnmp/files/twistedsnmp/0.3.13/TwistedSNMP-0.3.13.tar.gz
	tar -xvf TwistedSNMP-0.3.13.tar.gz
	rm -f TwistedSNMP-0.3.13.tar.gz
	cd $PKG
	python setup.py install
	cd ..
fi

# Build and install pysnmp-se-3.5.2:
if [ ! -d TwistedSNMP-0.3.13 ]; then
	set -e
	set -o pipefail
else
	echo ""
	echo "**************************** OK. Go to the next step. ******************************"
	echo ""
	PKG="pysnmp-se-3.5.2"
	echo "-----------------------------------------"
	echo "Build and install $PKG"
	echo "-----------------------------------------"
	wget https://sourceforge.net/projects/twistedsnmp/files/pysnmp-se/3.5.2/pysnmp-se-3.5.2.tar.gz
	tar -xvf pysnmp-se-3.5.2.tar.gz
	rm -f pysnmp-se-3.5.2.tar.gz
	cd $PKG
	python setup.py install
	cd ..
fi

# Build and install attrs-git:
if [ ! -d pysnmp-se-3.5.2 ]; then
	set -e
	set -o pipefail
else
	echo ""
	echo "**************************** OK. Go to the next step. ******************************"
	echo ""
	PKG="attrs"
	echo "-----------------------------------------"
	echo "Build and install $PKG"
	echo "-----------------------------------------"
	git clone https://github.com/python-attrs/attrs.git
	cd $PKG
	python setup.py install
	cd ..
fi

# Build and install constantly-git:
if [ ! -d attrs ]; then
	set -e
	set -o pipefail
else
	echo ""
	echo "**************************** OK. Go to the next step. ******************************"
	echo ""
	PKG="constantly"
	echo "-----------------------------------------"
	echo "Build and install $PKG"
	echo "-----------------------------------------"
	git clone https://github.com/twisted/constantly.git
	cd $PKG
	python setup.py install
	cd ..
fi

# Build and install hyperlink-git:
if [ ! -d constantly ]; then
	set -e
	set -o pipefail
else
	echo ""
	echo "**************************** OK. Go to the next step. ******************************"
	echo ""
	PKG="hyperlink"
	echo "-----------------------------------------"
	echo "Build and install $PKG"
	echo "-----------------------------------------"
	git clone https://github.com/python-hyper/hyperlink.git
	cd $PKG
	python setup.py install
	cd ..
fi

# Build and install incremental-git:
if [ ! -d hyperlink ]; then
	set -e
	set -o pipefail
else
	echo ""
	echo "**************************** OK. Go to the next step. ******************************"
	echo ""
	PKG="incremental"
	echo "-----------------------------------------"
	echo "Build and install $PKG"
	echo "-----------------------------------------"
	git clone https://github.com/twisted/incremental.git
	cd $PKG
	python setup.py install
	cd ..
fi

# Build and install Js2Py-0.50:
if [ ! -d incremental ]; then
	set -e
	set -o pipefail
	# Message if error at any point of script
	echo ""
	echo "************* Forced stop script execution. It maybe сompilation error, ************"
	echo "************** lost Internet connection or the server not responding. **************"
	echo "*********************** Check the log for more information. ************************"
	echo ""
else
	echo ""
	echo "**************************** OK. Go to the next step. ******************************"
	echo ""
	PKG="Js2Py-0.50"
	echo "-----------------------------------------"
	echo "Build and install $PKG"
	echo "-----------------------------------------"
	wget https://pypi.python.org/packages/69/73/9c05be6a463f01178749e551253994c1d938827c8c35b0e18c937761030d/Js2Py-0.50.tar.gz
	tar -xvf Js2Py-0.50.tar.gz
	rm -f Js2Py-0.50.tar.gz
	cd $PKG
	python setup.py install
	cd ../..
	echo ""
	echo "************************************ DONE! *****************************************"
fi
