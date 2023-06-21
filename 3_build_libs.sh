#!/bin/bash

# To build enigma2 on Ubuntu 14.04 LTS (32/64-bit), 16.04 LTS (32/64-bit), 18.04 LTS (64-bit), 20.04 LTS (64-bit) and 22.04 (64-bit) with startup option "Ubuntu on Xorg".

# Be sure that the version of Ubuntu is determined
#if [ ! -d /usr/share/pyshared ]; then
#	cp -rfv pre/pyshared /usr/share
#fi

if [ ! -f /usr/lib/python3/dist-packages/lsb_release.py ]; then
	ln -s /usr/share/pyshared/lsb_release.py /usr/lib/python3/dist-packages/lsb_release.py
fi

echo ""
echo "                       *** INSTALL REQUIRED PACKAGES ***"
echo ""

release=$(lsb_release -a 2>/dev/null | grep -i release | awk ' { print $2 } ')

REQPKG_ALL="ant aptitude autoconf automake autopoint avahi-daemon bash build-essential checkinstall chrpath cmake coreutils cvs debhelper desktop-file-utils docbook-utils \
	diffstat dvb-apps dvdbackup ethtool fakeroot flex ffmpeg gawk gettext git help2man linux-headers-`uname -r` libdvdnav-dev libfreetype6-dev libfribidi-dev libsigc++-2.0-dev \
	libpcsclite-dev libjpeg8-dev libgif-dev libjpeg-turbo8-dev libgiftiio0 libaio-dev libxinerama-dev libxt-dev libasound2-dev libcaca-dev libpulse-dev libvorbis-dev \
	libgtk2.0-dev libtool libxml2-dev libxml2-utils libxslt1-dev libssl-dev libvdpau-dev libcdio-dev libcrypto++-dev libudf-dev libvcdinfo-dev libusb-1.0-0-dev \
	libavcodec-dev libavformat-dev libpostproc-dev libavutil-dev libnl-3-dev libbluray-dev libmpcdec-dev libvpx-dev libnl-genl-3-dev libavahi-client3 libavahi-client-dev \
	libflac-dev libogg-dev libxcb-xv0-dev libxcb-shape0-dev libxv-dev libxvmc-dev libaa1-dev libmodplug-dev libjack-jackd2-dev libdirectfb-dev libmagickwand-dev \
	libwavpack-dev libspeex-dev libmng-dev libmad0-dev librsvg2-bin libtheora-dev libsmbclient-dev liblircclient-dev librtmp1 libmng2 libx11-6 libxext6 libglib2.0-dev \
	libelf-dev libmysqlclient-dev libupnp-dev libgiftiio-dev libgstreamer-plugins-base1.0-dev libgstreamer1.0-dev gstreamer1.0-libav mawk mercurial mingetty mjpegtools \
	net-tools ntpdate openssh-sftp-server pmccabe patch pkg-config rpl rsyslog rtmpdump sdparm setserial smartmontools software-properties-common sphinx-common streamripper \
	subversion texi2html texinfo unclutter unzip uchardet youtube-dl w3m vsftpd xmlto xterm ubuntu-restricted-extras wavpack \
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
	echo "************************************************************************************"
	echo "                             *** release 14.04 ***"
	echo "************************************************************************************"
	echo ""
	if [ ! -f /etc/apt/sources.list.d/ubuntu-cloud-archive-liberty-staging-trusty.list ]; then
	add-apt-repository -y ppa:ubuntu-cloud-archive/liberty-staging
	apt-get update
	fi
	if [ ! -f /etc/apt/sources.list.d/ubuntu-toolchain-r-test-trusty.list ]; then
	add-apt-repository -y ppa:ubuntu-toolchain-r/test
	apt-get update
	fi
	REQPKG="flake gcc-8 g++-8 libgnomevfs2-dev libssl1.0.0 libsdl1.2-dev libpng12-dev libesd0-dev libqtgstreamer-dev libupnp6-dev libva-glx1 libva-dev libdts-dev mock python-ipaddress \
	pyflakes python-pysqlite2 python-cryptography-vectors python-netifaces python-pyasn1-modules python-pycryptopp python-simplejson python-pycurl python-pil python-openssl python-cheetah \
	python-flickrapi python-lzma python-mechanize python-sendfile python-bzrlib python-blessings python-httpretty python-ntplib python-daap python-transmissionrpc python-yenc python-gdata \
	python-cffi python-demjson python-mutagen python-twisted python-twisted-web python-twisted-mail python-ipaddr python-urllib3 python-dev python-setuptools swig2.0 \
	"
	if [[ $(uname -m) = "i686" ]]; then
		echo "Your system is 32-bit"
		wget --no-check-certificate https://ftp.fau.de/ubuntu/ubuntu/pool/main/g/giflib/libgif7_5.1.9-2_i386.deb
		wget --no-check-certificate https://ftp.fau.de/ubuntu/ubuntu/pool/main/g/giflib/libgif-dev_5.1.9-2_i386.deb
	else
		echo "Your system is 64-bit"
		wget --no-check-certificate http://archive.ubuntu.com/ubuntu/pool/main/g/giflib/libgif7_5.1.4-2_amd64.deb
		wget --no-check-certificate http://archive.ubuntu.com/ubuntu/pool/main/g/giflib/libgif-dev_5.1.4-2_amd64.deb
	fi
	dpkg -i *deb
	rm -f *deb
elif [[ "$release" = "16.04" ]]; then
	echo ""
	echo "************************************************************************************"
	echo "                             *** release 16.04 ***"
	echo "************************************************************************************"
	echo ""
	if [ ! -f /etc/apt/sources.list.d/ubuntu-toolchain-r-ubuntu-test-xenial.list ]; then
	add-apt-repository -y ppa:ubuntu-toolchain-r/test
	apt-get update
	fi
	REQPKG="flake8 gcc-8 g++-8 libgnomevfs2-dev libssl1.0.0 libsdl1.2-dev libtool-bin libesd0-dev libpng12-dev libva-glx1 libva-dev libqt5gstreamer-dev libupnp6-dev libdts-dev mock python-ipaddress \
	pyflakes python-pysqlite2 python-cryptography-vectors python-netifaces python-pyasn1-modules python-pycryptopp python-simplejson python-pycurl python-pil python-openssl python-cheetah \
	python-setuptools python-flickrapi python-lzma python-mechanize python-sendfile python-bzrlib python-blessings python-httpretty python-subprocess32 python-cryptodome python-pickleshare \
	python-service-identity python-certifi python-restructuredtext-lint python-daap python-ntplib python-transmissionrpc python-yenc python-gdata python-demjson python-mutagen python-ipaddr \
	python-urllib3 python-sphinx-rtd-theme python-sphinx python-sphinxcontrib.httpdomain python-dev pylint python-requests python-requests-toolbelt python-jwt python-blinker python-oauthlib \
	python-requests-oauthlib python-configobj python-future python-openssl python-twisted python-twisted-core python-twisted-bin python-twisted-web python-twisted-names python-twisted-mail \
	python-cffi sphinx-rtd-theme-common swig2.0 yamllint \
	"
elif [[ "$release" = "18.04" ]]; then
	echo ""
	echo "************************************************************************************"
	echo "                             *** release 18.04 ***"
	echo "************************************************************************************"
	echo ""
	REQPKG="flake8 gcc-8 g++-8 libgnomevfs2-dev libssl1.1 libsdl2-dev libtool-bin libpng-dev libqt5gstreamer-dev libva-glx2 libva-dev libupnp6-dev libvdpau1 libvdpau-va-gl1 libdts-dev mock \
	python-ipaddress pyflakes python-pysqlite2 python-cryptography-vectors python-netifaces python-pyasn1-modules python-pycryptopp python-simplejson python-pycurl python-pil python-openssl \
	python-cheetah python-setuptools python-flickrapi python-lzma python-mechanize python-sendfile python-bzrlib python-blessings python-httpretty python-subprocess32 python-langdetect \
	python-pycryptodome python-pickleshare pycodestyle python-service-identity python-certifi python-restructuredtext-lint python-daap python-ntplib python-transmissionrpc python-yenc python-gdata \
	python-demjson python-mutagen python-ipaddr python-urllib3 python-sphinx-rtd-theme python-sphinx python-sphinxcontrib.websupport python-sphinxcontrib.httpdomain python-dev pylint \
	python-incremental python-sabyenc python-requests python-requests-toolbelt python-jwt python-blinker python-oauthlib python-requests-oauthlib python-configobj python-future python-openssl \
	python-twisted python-twisted-core python-twisted-bin python-twisted-web python-twisted-names python-twisted-mail sphinx-rtd-theme-common swig yamllint \
	"
elif [[ "$release" = "20.04" ]]; then
	echo ""
	echo "************************************************************************************"
	echo "                             *** release 20.04 ***"
	echo "************************************************************************************"
	echo ""
	# Add new repositories
	if [ ! -f /etc/apt/sources.list.d/oibaf-ubuntu-graphics-drivers-focal.list ]; then
		add-apt-repository -y ppa:oibaf/graphics-drivers
	fi
	if [ ! -f /etc/apt/sources.list.d/mamarley-ubuntu-updates-focal.list ]; then
		add-apt-repository -y ppa:mamarley/updates
		apt-get update
		apt-get -y upgrade
	else
		echo ""
		echo "                         *** Packages already updated. ***"
		echo ""
	fi
	REQPKG="flake8 gcc-9 g++-9 libssl1.1 libsdl2-dev libtool-bin libpng-dev libqt5gstreamer-dev libva-glx2 libva-dev libdts-dev libupnp-dev libvdpau1 libvdpau-va-gl1 python-ipaddress pyflakes \
	python-pysqlite2 python-cryptography-vectors python-netifaces python-pyasn1-modules python-pycryptopp python-simplejson python-pycurl python-pil python-openssl python-cheetah python-setuptools \
	python2-dev python-subprocess32 python-pycryptodome pycodestyle python-service-identity python-certifi python-dev-is-python2 python-automat python-constantly python-hyperlink python-zope.interface \
	python-chardet python-docutils python-pygments python-roman python3-langdetect python3-restructuredtext-lint python3-ntplib python3-transmissionrpc python3-sabyenc python-pyflakes python3-flickrapi \
	python3-demjson python3-mechanize python3-sendfile python3-blessings python3-httpretty python3-mutagen python3-urllib3 pylint python-ipaddress python-attr sphinx-rtd-theme-common swig swig3.0 yamllint \
	"
# Download 2.7 paskages
	wget --no-check-certificate http://archive.ubuntu.com/ubuntu/pool/main/i/incremental/python-incremental_16.10.1-3_all.deb \
	http://old-releases.ubuntu.com/ubuntu/pool/universe/t/twisted/python-twisted-web_18.9.0-3_all.deb \
	http://old-releases.ubuntu.com/ubuntu/pool/universe/t/twisted/python-twisted-names_18.9.0-3_all.deb \
	http://old-releases.ubuntu.com/ubuntu/pool/universe/t/twisted/python-twisted-mail_18.9.0-3_all.deb \
	http://old-releases.ubuntu.com/ubuntu/pool/universe/t/twisted/python-twisted-bin_18.9.0-3_amd64.deb \
	http://old-releases.ubuntu.com/ubuntu/pool/universe/t/twisted/python-twisted-core_18.9.0-3_all.deb \
	http://old-releases.ubuntu.com/ubuntu/pool/universe/t/twisted/python-twisted-conch_18.9.0-3_all.deb \
	http://archive.ubuntu.com/ubuntu/pool/universe/b/blinker/python-blinker_1.4+dfsg1-0.3ubuntu1_all.deb\
	http://archive.ubuntu.com/ubuntu/pool/universe/p/python-mechanize/python-mechanize_0.2.5-3_all.deb \
	http://archive.ubuntu.com/ubuntu/pool/main/c/configobj/python-configobj_5.0.6-2_all.deb \
	http://ftp.br.debian.org/debian/pool/main/p/python-ipaddr/python-ipaddr_2.2.0-2_all.deb \
	http://ftp.br.debian.org/debian/pool/main/p/python-urllib3/python-urllib3_1.24.1-1_all.deb \
	http://ftp.br.debian.org/debian/pool/main/b/bzr/python-bzrlib_2.7.0+bzr6622-15_amd64.deb \
	http://ftp.br.debian.org/debian/pool/main/p/pysendfile/python-sendfile_2.0.1-2_amd64.deb \
	http://ftp.br.debian.org/debian/pool/main/p/python-lzma/python-lzma_0.5.3-4_amd64.deb \
	http://ftp.br.debian.org/debian/pool/main/b/blessings/python-blessings_1.6-2_all.deb \
	http://ftp.br.debian.org/debian/pool/main/p/python-langdetect/python-langdetect_1.0.7-3_all.deb \
	http://ftp.br.debian.org/debian/pool/main/p/pickleshare/python-pickleshare_0.7.5-1_all.deb \
	http://ftp.br.debian.org/debian/pool/main/p/python-sabyenc/python-sabyenc_3.3.5-1_amd64.deb \
	http://ftp.br.debian.org/debian/pool/main/r/requests/python-requests_2.21.0-1_all.deb \
	http://ftp.br.debian.org/debian/pool/main/p/python-requests-toolbelt/python-requests-toolbelt_0.8.0-1_all.deb \
	http://ftp.br.debian.org/debian/pool/main/p/pyjwt/python-jwt_1.7.0-2_all.deb \
	http://ftp.br.debian.org/debian/pool/main/p/python-oauthlib/python-oauthlib_2.1.0-1_all.deb \
	http://ftp.br.debian.org/debian/pool/main/p/python-requests-oauthlib/python-requests-oauthlib_1.0.0-0.1_all.deb \
	http://ftp.br.debian.org/debian/pool/main/p/python-flickrapi/python-flickrapi_2.1.2-5_all.deb \
	http://ftp.br.debian.org/debian/pool/main/p/python-click/python-click_7.0-1_all.deb \
	http://ftp.br.debian.org/debian/pool/main/p/python-colorama/python-colorama_0.3.7-1_all.deb
	dpkg -i *deb
	apt-get -f install -y
	rm -f *deb
elif [[ "$release" = "22.04" ]]; then
	echo ""
	echo "************************************************************************************"
	echo "                             *** release 22.04 ***"
	echo "************************************************************************************"
	echo ""
	REQPKG="flake8 gcc-11 g++-11 libdca-dev libssl3 libsdl2-dev libtool-bin libpng-dev libqt5gstreamer-dev libva-glx2 libva-dev liba52-0.7.4-dev libffi7 python2-minimal libpython2-dev \
	libpython2-stdlib python2 python2-dev libfuture-perl pycodestyle python3-sphinx-rtd-theme python3-sphinxcontrib.websupport python3-sphinxcontrib.httpdomain python3-langdetect \
	python3-restructuredtext-lint python3-ntplib python3-transmissionrpc python3-sabyenc python3-flickrapi python3-demjson python3-mechanize python3-sendfile python3-blessings python3-httpretty \
	python3-mutagen python3-urllib3 pylint sphinx-rtd-theme-common libupnp-dev libvdpau1 libvdpau-va-gl1 swig swig3.0 yamllint neurodebian-popularity-contest popularity-contest \
	"
	apt-get -f install -y
	wget --no-check-certificate http://archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.1f-1ubuntu2.19_amd64.deb
	dpkg -i libssl1.1_1.1.1f-1ubuntu2.19_amd64.deb
	rm -f *deb
# Unfortunately e2pc doesn't work with wayland
#	cp -fv /etc/gdm3/custom.conf /etc/gdm3/custom.conf~
#	rpl '#WaylandEnable=false' 'WaylandEnable=false' /etc/gdm3/custom.conf
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

HEADERS="/usr/src/linux-headers-`uname -r`/include/uapi/linux/dvb"
INCLUDE="/usr/include/linux/dvb"
BUILD_DIR="libs"

cp -fv pre/dvb/* $INCLUDE
cp -fv pre/dvb/* $HEADERS

# Download dvb-firmwares
wget --no-check-certificate https://github.com/crazycat69/media_build/releases/download/latest/dvb-firmwares.tar.bz2
tar -xvjf dvb-firmwares.tar.bz2 -C /lib/firmware
rm -f dvb-firmwares.tar.bz2

if [ -d $BUILD_DIR ]; then
	rm -rf $BUILD_DIR
fi
mkdir -v $BUILD_DIR
cd $BUILD_DIR

# Build and install libdvbsi++-git:
LIB="libdvbsi++1"
PKG="libdvbsi++"
#PKG="libdvbsi-"
echo ""
echo "                    *** Build and install $PKG ***"
echo ""
I=`dpkg -s $LIB | grep "Status"`
if [ -n "$I" ]; then
	dpkg -P $LIB $LIB-dbgsym $PKG-dev
else
	echo "$PKG not installed"
fi
if [ -d $PKG ]; then
	rm -rf $PKG
fi
#git clone https://github.com/OpenDMM/$PKG.git
git clone --depth 1 git://git.opendreambox.org/git/obi/$PKG.git
cd $PKG
#autoupdate
dpkg-buildpackage -b -d -uc -us
cd ..
mv $PKG*.* $PKG
cd $PKG
dpkg -i *deb
rm -f *.tar.xz
make distclean
cd ..

# Build and install libxmlccwrap-git:
if [ ! -d libdvbsi++ ]; then
	set -e
	set -o pipefail
else
	PKG="libxmlccwrap"
	echo ""
	echo "**************************** OK. Go to the next step. ******************************"
	echo ""
	echo "                     *** Build and install $PKG ***"
	echo ""
	I=`dpkg -s $PKG | grep "Status"`
	if [ -n "$I" ]; then
		dpkg -P $PKG $PKG-dev $PKG-dbgsym
	else
		echo "$PKG not installed"
	fi
	if [ -d $PKG ]; then
		rm -rf $PKG
	fi
	git clone https://github.com/OpenDMM/$PKG.git
#	git clone git://git.opendreambox.org/git/obi/$PKG.git
	cd $PKG
	rpl '5' '10' debian/compat
	rpl 'Source-Version' 'binary:Version' debian/control
	sed -i 's/-$(MAKE) clean//g' debian/rules
	sed -i 's/-$(MAKE) distclean//g' debian/rules
#	autoupdate
	dpkg-buildpackage -b -d -uc -us
	cd ..
	mv $PKG*.* $PKG
	cd $PKG
	dpkg -i *deb
	rm -f *.tar.gz
	make distclean
	cd ..
fi

# Build and install libdvbcsa-git:
if [ ! -d libxmlccwrap ]; then
	set -e
	set -o pipefail
else
	PKG="libdvbcsa"
	PKG1="libdvbcsa1"
	VER="bc6c0b164a87ce05e9925785cc6fb3f54c02b026"
	echo ""
	echo "**************************** OK. Go to the next step. ******************************"
	echo ""
	echo "                       *** Build and install $PKG ***"
	echo ""
	I=`dpkg -s $PKG | grep "Status"`
	if [ -n "$I" ]; then
		dpkg -P $PKG $PKG-dev $PKG1 tsdecrypt
	else
		echo "$PKG not installed"
	fi
	I=`dpkg -s $PKG1 | grep "Status"`
	if [ -n "$I" ]; then
		dpkg -P $PKG1 $PKG-dev tsdecrypt
	else
		echo "$PKG not installed"
	fi
	if [ -d $PKG ]; then
		rm -rf $PKG
	fi
	wget --no-check-certificate https://code.videolan.org/videolan/$PKG/-/archive/$VER/$PKG-$VER.zip
	unzip $PKG-$VER.zip
	rm $PKG-$VER.zip
	mv $PKG-$VER $PKG
	cd $PKG
	./bootstrap
	./configure --prefix=/usr --enable-sse2
	checkinstall -D --install=yes --default --pkgname=$PKG --pkgversion=1.2.0 --maintainer=e2pc@gmail.com --pkggroup=video --gzman=yes
	rm -f *.tgz
	make distclean
	cd ..
fi

# Build and install libtuxtxt:
if [ ! -d libdvbcsa ]; then
	set -e
	set -o pipefail
else
	INSTALL_E2DIR="/usr/local/e2"
	SOURCE="tuxtxt-git"
	PKG="libtuxtxt"
	PKG_="tuxtxt"
	VER="1402795d660955757d87967b8ff1e3790625f9c1"
	echo ""
	echo "**************************** OK. Go to the next step. ******************************"
	echo ""
	echo "                       *** Build and install $PKG ***"
	echo ""
	I=`dpkg -s $PKG | grep "Status"`
	if [ -n "$I" ]; then
		dpkg -P $PKG
	else
		echo "$PKG not installed"
	fi
	if [ ! -d $INSTALL_E2DIR ]; then
		mkdir -p $INSTALL_E2DIR/lib/enigma2
	fi
	if [ -d $SOURCE ]; then
		dpkg -r $PKG $PKG_
		rm -rf $SOURCE
	fi
	if [ ! -d $INSTALL_E2DIR/lib/enigma2 ]; then
		mkdir -p $INSTALL_E2DIR/lib/enigma2
		ln -s $INSTALL_E2DIR/lib/enigma2 /usr/lib
	fi
	if [ -d $SOURCE ]; then
		rm -rf $SOURCE
	fi
	wget --no-check-certificate https://github.com/OpenPLi/$PKG_/archive/$VER.zip
	unzip $VER.zip
	rm $VER.zip
	mv $PKG_-$VER $SOURCE
	cd ..
	cp -v patches/$PKG_.patch libs/$SOURCE
	cd libs/$SOURCE
	patch -p1 < $PKG_.patch
	echo ""
	echo "                       *** patches for $PKG applied ***"
	echo ""
	cd $PKG
#	autoupdate
	autoreconf -i
	./configure --prefix=/usr --with-boxtype=generic DVB_API_VERSION=5
	checkinstall -D --install=yes --default --pkgname=$PKG --pkgversion=1.0 --maintainer=e2pc@gmail.com --pkggroup=video --gzman=yes
	rm -f *.tgz
	make distclean
	cd ..
fi

# Build and install tuxtxt:
if [ ! -d libtuxtxt ]; then
	set -e
	set -o pipefail
else
	PKG="tuxtxt"
	echo ""
	echo "**************************** OK. Go to the next step. ******************************"
	echo ""
	echo "                        *** Build and install $PKG ***"
	echo ""
	I=`dpkg -s $PKG | grep "Status"`
	if [ -n "$I" ]; then
		dpkg -P $PKG
	else
		echo "$PKG not installed"
	fi
	cd $PKG
#	autoupdate
	autoreconf -i
	./configure --prefix=/usr --with-boxtype=generic --with-configdir=/usr/etc --with-fbdev=/dev/fb0 --with-textlcd DVB_API_VERSION=5
	checkinstall -D --install=yes --default --pkgname=$PKG --pkgversion=1.0 --maintainer=e2pc@gmail.com --pkggroup=video --gzman=yes
	find $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/Tuxtxt -name "*.py[o]" -exec rm {} \;
	rm -f *.tgz
	make distclean
	cd ../..
fi

# Build and install aio-grab-git:
if [ ! -d tuxtxt-git/tuxtxt ]; then
	set -e
	set -o pipefail
else
	PKG="aio-grab"
	VER="cf62da47eedb6afe4c44949253ef0b876deb2105"
	echo ""
	echo "**************************** OK. Go to the next step. ******************************"
	echo ""
	echo "                       *** Build and install $PKG ***"
	echo ""
	I=`dpkg -s $PKG | grep "Status"`
	if [ -n "$I" ]; then
		dpkg -P $PKG
	else
		echo "$PKG not installed"
	fi
	if [ -d $PKG ]; then
		rm -rf $PKG
	fi
	wget --no-check-certificate https://github.com/OpenPLi/$PKG/archive/$VER.zip
	unzip $VER.zip
	rm $VER.zip
	mv $PKG-$VER $PKG
	cd $PKG
	autoreconf -i
	./configure --prefix=/usr
	checkinstall -D --install=yes --default --pkgname=$PKG --pkgversion=1.0 --maintainer=e2pc@gmail.com --pkggroup=video --gzman=yes
	rm -f *.tgz
	make distclean
	cd ..
fi

# Build and install gst-plugin-dvbmediasink-git:
if [ ! -d aio-grab ]; then
	set -e
	set -o pipefail
else
	LIB="libgstreamer-plugins-dvbmediasink"
	PKG="gst-plugin-dvbmediasink"
	PKG_="dvbmediasink"
	VER="1d197313832d39fdaf430634f62ad95a33029db0"
	echo ""
	echo "**************************** OK. Go to the next step. ******************************"
	echo ""
	echo "                 *** Build and install $PKG ***"
	echo ""
	I=`dpkg -s $LIB | grep "Status"`
	if [ -n "$I" ]; then
		dpkg -P $LIB
	else
		echo "$LIB not installed"
	fi
	if [ -d $PKG ]; then
		rm -rf $PKG
	fi
	wget --no-check-certificate https://github.com/OpenPLi/$PKG/archive/$VER.zip
	unzip $VER.zip
	rm $VER.zip
	mv $PKG-$VER $PKG
	cd $PKG
#	autoupdate
	autoreconf -i
	./configure --prefix=/usr --with-wma --with-wmv --with-pcm --with-dtsdownmix --with-eac3 --with-mpeg4 --with-mpeg4v2 --with-h263 --with-h264 --with-h265
	checkinstall -D --install=yes --default --pkgname=$LIB --pkgversion=1.0.0 --maintainer=e2pc@gmail.com --pkggroup=video --gzman=yes
	rm -f *.tgz
	make distclean
	cd ..
fi

# Build and install gst-plugin-subsink-git:
if [ ! -d gst-plugin-dvbmediasink ]; then
	set -e
	set -o pipefail
else
	LIB="libgstreamer-plugins-subsink"
	PKG="gst-plugin-subsink"
	VER="2c4288bb29e0781f27aecc25c941b6e441630f8d"
	echo ""
	echo "**************************** OK. Go to the next step. ******************************"
	echo ""
	echo "                    *** Build and install $PKG ***"
	echo ""
	I=`dpkg -s $LIB | grep "Status"`
	if [ -n "$I" ]; then
		dpkg -P $LIB
	else
		echo "$LIB not installed"
	fi
	if [ -d $PKG ]; then
		rm -rf $PKG
	fi
	wget --no-check-certificate https://github.com/OpenPLi/$PKG/archive/$VER.zip
	unzip $VER.zip
	rm $VER.zip
	mv $PKG-$VER $PKG
	cd $PKG
	echo "AC_CONFIG_MACRO_DIR([m4])" >> configure.ac
	if [[ "$release" = "14.04" ]]; then
		#autoupdate
		autoreconf -i
		./configure --prefix=/usr
		checkinstall -D --install=yes --default --pkgname=$LIB --pkgversion=1.0.0 --maintainer=e2pc@gmail.com --pkggroup=video --gzman=yes
	else
		cd ../..
		cp -v patches/subsink_1.0.patch libs/$PKG
		cd libs/$PKG
		patch -p1 < subsink_1.0.patch
		echo ""
		echo "                  *** Patch for $PKG applied ***"
		echo ""
		#autoupdate
		autoreconf -i
		./configure --prefix=/usr
		checkinstall -D --install=yes --default --pkgname=$LIB --pkgversion=1.0 --maintainer=e2pc@gmail.com --pkggroup=video --gzman=yes
	fi
	rm -f *.tgz
	make distclean
	cd ..
fi

# Message if error at any point of script
if [ ! -d gst-plugin-subsink ]; then
	set -e
	set -o pipefail
	echo ""
	echo "          *** Forced stop script execution. It maybe сompilation error, ***"
	echo "           *** lost Internet connection or the server not responding. ***"
	echo "                    *** Check the log for more information. ***"
	echo ""
else
	cd ..
	if [[ "$release" = "22.04" ]]; then
		cp -rfv pre/python/* /usr # hack!
	else
		cp -rfv pre/python/lib/python2.7/dist-packages/pythonwifi /usr/lib/python2.7/dist-packages
		cp -fv pre/python/lib/python2.7/dist-packages/python_wifi-0.6.1.egg-info /usr/lib/python2.7/dist-packages
		cp -rfv pre/python/lib/python2.7/dist-packages/twistedsnmp /usr/lib/python2.7/dist-packages
		cp -fv pre/python/lib/python2.7/dist-packages/TwistedSNMP-0.3.13.egg-info /usr/lib/python2.7/dist-packages
		cp -rfv pre/python/lib/python2.7/dist-packages/pysnmp /usr/lib/python2.7/dist-packages
		cp -fv pre/python/lib/python2.7/dist-packages/pysnmp_se-3.5.2.egg-info /usr/lib/python2.7/dist-packages
		cp -rfv pre/python/lib/python2.7/dist-packages/js2py /usr/lib/python2.7/dist-packages
		cp -rfv pre/python/lib/python2.7/dist-packages/Js2Py-0.50.egg-info /usr/lib/python2.7/dist-packages
	fi
	echo ""
	echo "************************************ DONE! *****************************************"
fi
