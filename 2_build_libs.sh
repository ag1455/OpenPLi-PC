#!/bin/bash

# To build enigma2 on Ubuntu 14.04 LTS (32/64-bit), 16.04 LTS (32/64-bit), 18.04 LTS (64-bit), 20.04 LTS (64-bit) and test 20.10 (64-bit).
# Install these packages:

echo "********************************************************"
echo "            *** INSTALL REQUIRED PACKAGES ***"
echo "********************************************************"

release=$(lsb_release -a 2>/dev/null | grep -i release | awk ' { print $2 } ')

REQPKG_ALL="ant aptitude autoconf automake autopoint avahi-daemon bash build-essential checkinstall chrpath cmake coreutils cvs debhelper desktop-file-utils docbook-utils \
	diffstat dvb-apps dvdbackup ethtool fakeroot flex ffmpeg gawk gettext git help2man linux-headers-`uname -r` libdvdnav-dev libfreetype6-dev libfribidi-dev \
	libpcsclite-dev libjpeg8-dev libgif-dev libjpeg-turbo8-dev libgiftiio0 libaio-dev libxinerama-dev libxt-dev libasound2-dev libcaca-dev libpulse-dev libvorbis-dev \
	libgtk2.0-dev libtool libtool-bin libxml2-dev libxml2-utils libxslt1-dev libssl-dev libvdpau-dev libcdio-dev libcrypto++-dev libudf-dev libvcdinfo-dev libusb-1.0-0-dev \
	libavcodec-dev libavformat-dev libpostproc-dev libavutil-dev libnl-3-dev libbluray-dev libmpcdec-dev libvpx-dev libnl-genl-3-dev libavahi-client3 libavahi-client-dev \
	libflac-dev libogg-dev libdts-dev libxcb-xv0-dev libxcb-shape0-dev libxv-dev libxvmc-dev libaa1-dev libmodplug-dev libjack-jackd2-dev libdirectfb-dev libmagickwand-dev \
	libwavpack-dev libspeex-dev libmng-dev libmad0-dev librsvg2-bin libtheora-dev libsmbclient-dev liblircclient-dev librtmp1 libmng2 libx11-6 libxext6 libglib2.0-dev \
	libelf-dev libmysqlclient-dev libupnp-dev libgiftiio-dev libgstreamer-plugins-base1.0-dev libgstreamer1.0-dev gstreamer1.0-libav mawk mercurial mingetty mjpegtools \
	net-tools ntpdate openssh-sftp-server pmccabe python-setuptools python-ipaddress python-pysqlite2 python-cryptography-vectors python-netifaces python-pyasn1-modules \
	python-pycryptopp python-simplejson python-pycurl python-pil python-openssl python-cheetah patch pyflakes pkg-config rpl rsyslog rtmpdump sdparm setserial smartmontools \
	software-properties-common sphinx-common streamripper subversion texi2html texinfo unclutter unzip uchardet youtube-dl w3m vsftpd xmlto xterm ubuntu-restricted-extras \
	wavpack \
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
	REQPKG="flake gcc-8 g++-8 libgnomevfs2-dev libssl1.0.0 libsdl1.2-dev libpng12-dev libsigc++-1.2-dev libesd0-dev libqtgstreamer-dev libupnp6-dev libva-glx1 libva-dev \
	mock python-flickrapi python-lzma python-mechanize python-sendfile python-bzrlib python-blessings python-httpretty python-ntplib python-daap python-transmissionrpc \
	python-yenc python-gdata python-demjson python-mutagen python-twisted python-twisted-web python-twisted-mail python-ipaddr python-urllib3 python-dev swig2.0 \
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
	REQPKG="flake8 gcc-8 g++-8 libgnomevfs2-dev libssl1.0.0 libsdl1.2-dev libesd0-dev libpng12-dev libsigc++-1.2-dev libva-glx1 libva-dev python-subprocess32 libqt5gstreamer-dev \
	mock python-flickrapi python-lzma python-mechanize python-sendfile python-bzrlib python-blessings python-httpretty python-cryptodome python-pickleshare \
	python-service-identity python-certifi python-restructuredtext-lint python-ntplib pylint python-daap python-transmissionrpc python-yenc python-gdata python-demjson \
	python-mutagen python-twisted python-twisted-web python-twisted-mail python-ipaddr python-urllib3 python-dev sphinx-rtd-theme-common libupnp6-dev swig2.0 yamllint \
	"
elif [[ "$release" = "18.04" ]]; then
	echo ""
	echo "********************************************************"
	echo "                 *** release 18.04 ***                  "
	echo "********************************************************"
	echo ""
	REQPKG="flake8 gcc-8 g++-8 libgnomevfs2-dev libssl1.1 libsdl2-dev libpng-dev libsigc++-2.0-dev libqt5gstreamer-dev libva-glx2 libva-dev mock python-flickrapi python-lzma \
	python-mechanize python-sendfile python-bzrlib python-blessings python-httpretty python-subprocess32 python-langdetect python-pycryptodome python-pickleshare \
	pycodestyle python-service-identity python-certifi python-restructuredtext-lint python-daap python-ntplib python-transmissionrpc python-yenc python-gdata python-demjson \
	python-mutagen python-twisted python-twisted-web python-twisted-mail python-ipaddr python-urllib3 python-dev pylint libvdpau1 libvdpau-va-gl1 sphinx-rtd-theme-common \
	libupnp6-dev swig yamllint \
	"
elif [[ "$release" = "20.04" ]]; then
	echo ""
	echo "********************************************************"
	echo "                 *** release 20.04 ***                  "
	echo "********************************************************"
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
		echo "********************************************************"
		echo "            *** Packages already updated. ***"
		echo "********************************************************"
	fi

	REQPKG="flake8 gcc-9 g++-9 libssl1.1 libsdl2-dev libpng-dev libsigc++-2.0-dev libqt5gstreamer-dev libva-glx2 libva-dev python2-dev python-subprocess32 python-pycryptodome \
	python-pycryptodome pycodestyle python-service-identity python-certifi python2-dev python-dev-is-python2 python-automat python-constantly python-hyperlink python-zope.interface \
	python-chardet python-docutils python-pygments python-roman python3-langdetect python3-restructuredtext-lint python3-ntplib python3-transmissionrpc python3-sabyenc \
	python3-flickrapi python3-demjson python3-mechanize python3-sendfile python3-blessings python3-httpretty python3-mutagen python3-urllib3 pylint python-ipaddress \
	sphinx-rtd-theme-common libupnp-dev libvdpau1 libvdpau-va-gl1 swig swig3.0 yamllint \
	"
	apt-get purge -y python-twisted-bin python-incremental python-twisted-core python-twisted-web python-twisted-names python-twisted-mail python-ipaddr python-urllib3 python-configobj \
	python-bzrlib python-lzma python-blessings python-mechanize python-flickrapi python-langdetect python-pickleshare python-sabyenc python-restructuredtext-lint python-requests \
	python-requests-toolbelt python-jwt python-oauthlib python-requests-oauthlib python-blinker python-flickrapi python-sendfile
	wget http://archive.ubuntu.com/ubuntu/pool/main/i/incremental/python-incremental_16.10.1-3_all.deb \
	http://ftp.br.debian.org/debian/pool/main/t/twisted/python-twisted-web_18.9.0-3_all.deb \
	http://ftp.br.debian.org/debian/pool/main/t/twisted/python-twisted-names_18.9.0-3_all.deb \
	http://ftp.br.debian.org/debian/pool/main/t/twisted/python-twisted-mail_18.9.0-3_all.deb \
	http://ftp.br.debian.org/debian/pool/main/t/twisted/python-twisted-bin_18.9.0-3_amd64.deb \
	http://ftp.br.debian.org/debian/pool/main/t/twisted/python-twisted-core_18.9.0-3_all.deb \
	http://ftp.br.debian.org/debian/pool/main/p/python-ipaddr/python-ipaddr_2.2.0-2_all.deb \
	http://ftp.br.debian.org/debian/pool/main/p/python-urllib3/python-urllib3_1.24.1-1_all.deb \
	http://ftp.br.debian.org/debian/pool/main/b/bzr/python-bzrlib_2.7.0+bzr6622-15_amd64.deb \
	http://ftp.br.debian.org/debian/pool/main/p/pysendfile/python-sendfile_2.0.1-2_amd64.deb \
	http://ftp.br.debian.org/debian/pool/main/p/python-lzma/python-lzma_0.5.3-4_amd64.deb \
	http://ftp.br.debian.org/debian/pool/main/b/blessings/python-blessings_1.6-2_all.deb \
	http://ftp.br.debian.org/debian/pool/main/p/python-mechanize/python-mechanize_0.2.5-3_all.deb \
	http://ftp.br.debian.org/debian/pool/main/p/python-langdetect/python-langdetect_1.0.7-3_all.deb \
	http://ftp.br.debian.org/debian/pool/main/p/pickleshare/python-pickleshare_0.7.5-1_all.deb \
	http://ftp.br.debian.org/debian/pool/main/p/python-sabyenc/python-sabyenc_3.3.5-1_amd64.deb \
	http://ftp.br.debian.org/debian/pool/main/p/python-restructuredtext-lint/python-restructuredtext-lint_0.12.2-2_all.deb \
	http://ftp.br.debian.org/debian/pool/main/r/requests/python-requests_2.21.0-1_all.deb \
	http://ftp.br.debian.org/debian/pool/main/p/python-requests-toolbelt/python-requests-toolbelt_0.8.0-1_all.deb \
	http://ftp.br.debian.org/debian/pool/main/p/pyjwt/python-jwt_1.7.0-2_all.deb \
	http://archive.ubuntu.com/ubuntu/pool/universe/b/blinker/python-blinker_1.4+dfsg1-0.3ubuntu1_all.deb\
	http://ftp.br.debian.org/debian/pool/main/p/python-oauthlib/python-oauthlib_2.1.0-1_all.deb \
	http://ftp.br.debian.org/debian/pool/main/p/python-requests-oauthlib/python-requests-oauthlib_1.0.0-0.1_all.deb \
	http://ftp.br.debian.org/debian/pool/main/p/python-flickrapi/python-flickrapi_2.1.2-5_all.deb \
	http://archive.ubuntu.com/ubuntu/pool/main/c/configobj/python-configobj_5.0.6-2_all.deb
	dpkg -i *.deb
	apt-get -f install -y
	rm -f *.deb
elif [[ "$release" = "20.10" ]]; then
	echo ""
	echo "********************************************************"
	echo "                 *** release 20.10 ***                  "
	echo "********************************************************"
	echo ""

	# Add new repositories
#	if [ ! -f /etc/apt/sources.list.d/oibaf-ubuntu-graphics-drivers-groovy.list ]; then
#		add-apt-repository -y ppa:oibaf/graphics-drivers
#	fi
	if [ ! -f /etc/apt/sources.list.d/mamarley-ubuntu-updates-groovy.list ]; then
		add-apt-repository -y ppa:mamarley/updates
		apt-get update
		apt-get -y upgrade
	else
		echo "********************************************************"
		echo "            *** Packages already updated. ***"
		echo "********************************************************"
	fi

	REQPKG="flake8 gcc-10 g++-10 libssl1.1 libsdl2-dev libpng-dev libsigc++-2.0-dev libqt5gstreamer-dev libva-glx2 libva-dev liba52-0.7.4-dev python2-dev \
	pycodestyle python-service-identity python2-dev python-dev-is-python2 python-automat python-constantly python-hyperlink python-zope.interface \
	python-pygments python-roman python3-langdetect python3-restructuredtext-lint python3-ntplib python3-transmissionrpc python3-sabyenc \
	python3-flickrapi python3-demjson python3-mechanize python3-sendfile python3-blessings python3-httpretty python3-mutagen python3-urllib3 pylint python-ipaddress python-is-python2 \
	sphinx-rtd-theme-common libupnp-dev libvdpau1 libvdpau-va-gl1 swig swig3.0 yamllint \
	"
	wget http://archive.ubuntu.com/ubuntu/pool/main/i/incremental/python-incremental_16.10.1-3_all.deb \
	http://ftp.br.debian.org/debian/pool/main/t/twisted/python-twisted-web_18.9.0-3_all.deb \
	http://ftp.br.debian.org/debian/pool/main/t/twisted/python-twisted-names_18.9.0-3_all.deb \
	http://ftp.br.debian.org/debian/pool/main/t/twisted/python-twisted-mail_18.9.0-3_all.deb \
	http://ftp.br.debian.org/debian/pool/main/t/twisted/python-twisted-bin_18.9.0-3_amd64.deb \
	http://ftp.br.debian.org/debian/pool/main/t/twisted/python-twisted-core_18.9.0-3_all.deb \
	http://ftp.br.debian.org/debian/pool/main/p/python-ipaddr/python-ipaddr_2.2.0-2_all.deb \
	http://ftp.br.debian.org/debian/pool/main/p/python-urllib3/python-urllib3_1.24.1-1_all.deb \
	http://ftp.br.debian.org/debian/pool/main/b/bzr/python-bzrlib_2.7.0+bzr6622-15_amd64.deb \
	http://ftp.br.debian.org/debian/pool/main/p/pysendfile/python-sendfile_2.0.1-2_amd64.deb \
	http://ftp.br.debian.org/debian/pool/main/p/python-lzma/python-lzma_0.5.3-4_amd64.deb \
	http://ftp.br.debian.org/debian/pool/main/b/blessings/python-blessings_1.6-2_all.deb \
	http://ftp.br.debian.org/debian/pool/main/p/python-mechanize/python-mechanize_0.2.5-3_all.deb \
	http://ftp.br.debian.org/debian/pool/main/p/python-langdetect/python-langdetect_1.0.7-3_all.deb \
	http://ftp.br.debian.org/debian/pool/main/p/pickleshare/python-pickleshare_0.7.5-1_all.deb \
	http://ftp.br.debian.org/debian/pool/main/p/python-sabyenc/python-sabyenc_3.3.5-1_amd64.deb \
	http://ftp.br.debian.org/debian/pool/main/p/pyjwt/python-jwt_1.7.0-2_all.deb \
	http://ftp.br.debian.org/debian/pool/main/p/python-oauthlib/python-oauthlib_2.1.0-1_all.deb \
	http://archive.ubuntu.com/ubuntu/pool/universe/b/blinker/python-blinker_1.4+dfsg1-0.3ubuntu1_all.deb\
	http://archive.ubuntu.com/ubuntu/pool/main/c/configobj/python-configobj_5.0.6-2_all.deb \
	http://archive.ubuntu.com/ubuntu/pool/main/p/pycurl/python-pycurl_7.43.0.1-0.2_amd64.deb \
	http://archive.ubuntu.com/ubuntu/pool/universe/c/cheetah/python-cheetah_3.2.4-1ubuntu1_amd64.deb \
	http://archive.ubuntu.com/ubuntu/pool/universe/p/pyflakes/pyflakes_1.6.0-1_all.deb \
	http://archive.ubuntu.com/ubuntu/pool/universe/p/pyflakes/python-pyflakes_1.6.0-1_all.deb \
	http://archive.ubuntu.com/ubuntu/pool/universe/p/python-pysqlite2/python-pysqlite2_2.7.0-1_amd64.deb \
	http://archive.ubuntu.com/ubuntu/pool/universe/p/python-cryptography-vectors/python-cryptography-vectors_2.1.4-1_all.deb \
	http://archive.ubuntu.com/ubuntu/pool/universe/p/pycryptopp/python-pycryptopp_0.7.1-3_amd64.deb \
	http://archive.ubuntu.com/ubuntu/pool/main/s/simplejson/python-simplejson_3.13.2-1_amd64.deb \
	http://archive.ubuntu.com/ubuntu/pool/main/p/pycryptodome/python-pycryptodome_3.4.7-1ubuntu1_amd64.deb \
	http://archive.ubuntu.com/ubuntu/pool/main/p/python-certifi/python-certifi_2018.1.18-2_all.deb \
	http://archive.ubuntu.com/ubuntu/pool/universe/p/python-subprocess32/python-subprocess32_3.2.7-3_amd64.deb
#	http://ftp.br.debian.org/debian/pool/main/p/python-restructuredtext-lint/python-restructuredtext-lint_0.12.2-2_all.deb \
#	http://ftp.br.debian.org/debian/pool/main/p/python-requests-toolbelt/python-requests-toolbelt_0.8.0-1_all.deb \
#	http://ftp.br.debian.org/debian/pool/main/r/requests/python-requests_2.21.0-1_all.deb \
#	http://ftp.br.debian.org/debian/pool/main/p/python-requests-oauthlib/python-requests-oauthlib_1.0.0-0.1_all.deb \
#	http://archive.ubuntu.com/ubuntu/pool/main/p/python-docutils/python-docutils_0.14+dfsg-3_all.deb \
#	http://archive.ubuntu.com/ubuntu/pool/main/p/python-roman/python-roman_2.0.0-3_all.deb \
#	http://archive.ubuntu.com/ubuntu/pool/main/c/chardet/python-chardet_3.0.4-1_all.deb \
#	http://archive.ubuntu.com/ubuntu/pool/universe/p/python-flickrapi/python-flickrapi_2.1.2-5_all.deb
	dpkg -i *.deb
	apt-get -f install -y
	rm -f *.deb
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

cp -fv pre/dvb/* $INCLUDE
cp -fv pre/dvb/* $HEADERS
cp -fv pre/sitecustomize.py /usr/local/lib/python2.7/site-packages

# Download dvb-firmwares
wget https://github.com/crazycat69/media_build/releases/download/latest/dvb-firmwares.tar.bz2
tar -xvjf dvb-firmwares.tar.bz2 -C /lib/firmware
rm -f dvb-firmwares.tar.bz2

BUILD_DIR="libs"
if [ -d $BUILD_DIR ]; then
	rm -rfv $BUILD_DIR
fi
mkdir -v $BUILD_DIR
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
cp -v patches/fix_section_len_check.patch libs/$PKG
cp -v patches/ac3_descriptor-check-if-header-is-larger-than-descri.patch libs/$PKG
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
	cp -v patches/tuxtxt.patch libs/$SOURCE
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
	find $INSTALL_E2DIR/lib/enigma2/python2/Plugins/Extensions/Tuxtxt -name "*.py[o]" -exec rm {} \;
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
	cp -v patches/aio-grab.patch libs/$PKG
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
		cp -v patches/dvbmediasink-0.10.patch libs/$PKG
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
		cp -v patches/dvbmediasink-1.0.patch libs/$PKG
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
		cp -v patches/subsink_1.0.patch libs/$PKG
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

# Build and install pythonwifi-git:
if [ ! -f gst-plugin-subsink/*.deb ]; then
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
	if [ "$release" = "20.04" ]; then
		python2 setup.py install
	elif [ "$release" = "20.10" ]; then
		python2 setup.py install
	else
		python setup.py install
	fi
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
	if [ "$release" = "20.04" ]; then
		python2 setup.py install
	elif [ "$release" = "20.10" ]; then
		python2 setup.py install
	else
		python setup.py install
	fi
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
	if [ "$release" = "20.04" ]; then
		python2 setup.py install
	elif [ "$release" = "20.10" ]; then
		python2 setup.py install
	else
		python setup.py install
	fi
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
	if [ "$release" = "20.04" ]; then
		python2 setup.py install
	elif [ "$release" = "20.10" ]; then
		python2 setup.py install
	else
		python setup.py install
	fi
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
	if [ "$release" = "20.04" ]; then
		python2 setup.py install
	elif [ "$release" = "20.10" ]; then
		python2 setup.py install
	else
		python setup.py install
	fi
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
	if [ "$release" = "20.04" ]; then
		python2 setup.py install
	elif [ "$release" = "20.10" ]; then
		python2 setup.py install
	else
		python setup.py install
	fi
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
	if [ "$release" = "20.04" ]; then
		python2 setup.py install
	elif [ "$release" = "20.10" ]; then
		python2 setup.py install
	else
		python setup.py install
	fi
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
	if [ "$release" = "20.04" ]; then
		python2 setup.py install
	elif [ "$release" = "20.10" ]; then
		python2 setup.py install
	else
		python setup.py install
	fi
	cd ../..
	echo ""
	echo "************************************ DONE! *****************************************"
fi
