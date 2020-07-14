#!/bin/bash

# Build and install plugins for enigma2pc

release=$(lsb_release -a 2>/dev/null | grep -i release | awk ' { print $2 } ')
INSTALL_E2DIR="/usr/local/e2"
MAKE_J="9"

### This is the lock from the unpredictable script actions in the root directory in the absence of the plugins folder.
if [ -d plugins ]; then

	# Remove old folders from e2 dir
	if [ -d $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/StreamInterface ]; then
		rm -rf $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/StreamInterface
	fi
	if [ -d $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/SystemTools ]; then
		rm -rf $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/SystemTools
	fi
	if [ -d $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/AddStreamUrl ]; then
		rm -rf $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/AddStreamUrl
	fi
	if [ -d $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/OpenWebif ]; then
		rm -rf $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/OpenWebif
	fi
	if [ -d $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/SetPicon ]; then
		rm -rf $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/SetPicon
	fi
	if [ -d $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/SnmpAgent ]; then
		rm -rf $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/SnmpAgent
	fi
	if [ -d $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/SimpleUmount ]; then
		rm -rf $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/SimpleUmount
	fi
	if [ -d $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/Foreca ]; then
		rm -rf $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/Foreca
	fi
	if [ -d $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/YouTube ]; then
		rm -rf $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/YouTube
	fi
	if [ -d $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/IPTVPlayer ]; then
		rm -rf $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/IPTVPlayer
	fi
	if [ -d $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/OscamStatus ]; then
		rm -rf $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/OscamStatus
	fi
	# Temporarily
	if [ -d $INSTALL_E2DIR/lib/enigma2/python/Plugins/PLi ]; then
		rm -rf $INSTALL_E2DIR/lib/enigma2/python/Plugins/PLi
	fi

	cd plugins/enigma2-plugins

	# Build enigma2 cpp plugins:
	if [ -d servicemp3 ]; then
		rm -rf servicemp3
	fi
	git clone https://github.com/OpenPLi/servicemp3.git
	cd ../..

	if [[ "$release" = "14.04" ]]; then
		echo "-----------------------------------------"
		echo "         *** release 14.04 ***           "
		echo "-----------------------------------------"
		export CXX=/usr/bin/g++-6
		echo ""
		echo "                  *** used g++-6 ***"
		echo ""
		cp patches/servicemp3-0.patch plugins/enigma2-plugins/servicemp3
		cd plugins/enigma2-plugins/servicemp3
		git checkout --detach c7750c5a
		patch -p1 < servicemp3-0.patch
	elif [[ "$release" = "16.04" ]]; then
		echo "-----------------------------------------"
		echo "         *** release 16.04 ***           "
		echo "-----------------------------------------"
		echo ""
		export CXX=/usr/bin/g++-7
		echo "                  *** used g++-7 ***"
		echo ""
		cp patches/servicemp3-0.patch plugins/enigma2-plugins/servicemp3
		cd plugins/enigma2-plugins/servicemp3
		git checkout --detach c7750c5a
		patch -p1 < servicemp3-0.patch
	elif [[ "$release" = "18.04" ]]; then
		echo "-----------------------------------------"
		echo "         *** release 18.04 ***           "
		echo "-----------------------------------------"
		echo ""
		export CXX=/usr/bin/g++-7
		echo "                  *** used g++-7 ***"
		echo ""
		cp patches/servicemp3.patch plugins/enigma2-plugins/servicemp3
		cd plugins/enigma2-plugins/servicemp3
		git checkout --detach c7750c5a
		patch -p1 < servicemp3.patch
	elif [[ "$release" = "19.04" ]]; then
		echo "-----------------------------------------"
		echo "         *** release 19.04 ***           "
		echo "-----------------------------------------"
		echo ""
		export CXX=/usr/bin/g++-8
		echo "                  *** used g++-8 ***"
		echo ""
		cp patches/servicemp3.patch plugins/enigma2-plugins/servicemp3
		cd plugins/enigma2-plugins/servicemp3
		git checkout --detach c7750c5a
		patch -p1 < servicemp3.patch
	elif [[ "$release" = "19.10" ]]; then
		echo "-----------------------------------------"
		echo "         *** release 19.10 ***           "
		echo "-----------------------------------------"
		echo ""
		export CXX=/usr/bin/g++-9
		echo "                  *** used g++-9 ***"
		echo ""
		cp patches/servicemp3.patch plugins/enigma2-plugins/servicemp3
		cd plugins/enigma2-plugins/servicemp3
		git checkout --detach c7750c5a
		patch -p1 < servicemp3.patch
	elif [[ "$release" = "20.04" ]]; then
		echo "-----------------------------------------"
		echo "         *** release 20.04 ***           "
		echo "-----------------------------------------"
		echo ""
		export CXX=/usr/bin/g++-9
		echo "                  *** used g++-9 ***"
		echo ""
		cp patches/servicemp3.patch plugins/enigma2-plugins/servicemp3
		cd plugins/enigma2-plugins/servicemp3
		git checkout --detach c7750c5a
		patch -p1 < servicemp3.patch
	fi

	cd ..

	#autoupdate
	autoreconf -i
	PKG_CONFIG_PATH=$INSTALL_E2DIR/lib/pkgconfig ./configure --prefix=$INSTALL_E2DIR
	make -j"$MAKE_J"
	make install
	cd ..

	tar -cvzf $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/VirtualZap.tar.gz $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/VirtualZap
	rm -rf $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/VirtualZap
	if [ -d e2openplugin ]; then
		rm -rf e2openplugin
	fi
	mkdir e2openplugin

	# Build python e2openplugin StreamInterface:
	if [ ! -d enigma2-plugins/servicemp3 ]; then
		set -e
		set -o pipefail
	else
		echo ""
		echo "**************************** OK. Go to the next step. ******************************"
		echo ""
		cd e2openplugin
		git clone https://github.com/E2OpenPlugins/e2openplugin-StreamInterface.git
		cd e2openplugin-StreamInterface
		if [ "$release" = "20.04" ]; then
			python2 setup.py install
		else
			python setup.py install
		fi
		mv -f /usr/local/lib/python2.7/dist-packages/Extensions/StreamInterface $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions
		mv -f /usr/local/lib/python2.7/dist-packages/enigma2_plugin_extensions_streaminterface* $INSTALL_E2DIR/lib/enigma2/python/Plugins
		cp -rfv plugin/locale $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/StreamInterface
		cd ..
	fi

	# Build python e2openplugin SystemTools
	if [ ! -d e2openplugin-StreamInterface ]; then
		set -e
		set -o pipefail
	else
		echo ""
		echo "**************************** OK. Go to the next step. ******************************"
		echo ""
		git clone https://github.com/E2OpenPlugins/e2openplugin-SystemTools.git
		cd ../..
		cp patches/SystemTools.patch plugins/e2openplugin/e2openplugin-SystemTools
		cd plugins/e2openplugin/e2openplugin-SystemTools
		patch -p1 < SystemTools.patch
		if [ "$release" = "20.04" ]; then
			python2 setup.py install
		else
			python setup.py install
		fi
		mv -f /usr/local/lib/python2.7/dist-packages/Extensions/SystemTools $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions
		mv -f /usr/local/lib/python2.7/dist-packages/enigma2_plugin_extensions_systemtools* $INSTALL_E2DIR/lib/enigma2/python/Plugins
		cp -rfv plugin/locale $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/SystemTools
		cd ..
	fi

	# Build python e2openplugin AddStreamUrl
	if [ ! -d e2openplugin-SystemTools ]; then
		set -e
		set -o pipefail
	else
		echo ""
		echo "**************************** OK. Go to the next step. ******************************"
		echo ""
		git clone https://github.com/E2OpenPlugins/e2openplugin-AddStreamUrl.git
		cd e2openplugin-AddStreamUrl
		if [ "$release" = "20.04" ]; then
			python2 setup.py install
		else
			python setup.py install
		fi
		mv -f /usr/local/lib/python2.7/dist-packages/Extensions/AddStreamUrl $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions
		mv -f /usr/local/lib/python2.7/dist-packages/enigma2_plugin_extensions_addstreamurl* $INSTALL_E2DIR/lib/enigma2/python/Plugins
		cd ..
	fi

	# Build python e2openplugin OpenWebif
	if [ ! -d e2openplugin-AddStreamUrl ]; then
		set -e
		set -o pipefail
	else
		echo ""
		echo "**************************** OK. Go to the next step. ******************************"
		echo ""
		git clone https://github.com/E2OpenPlugins/e2openplugin-OpenWebif.git
		cd ../..
		cp patches/OpenWebif.patch  plugins/e2openplugin/e2openplugin-OpenWebif
		cd plugins/e2openplugin/e2openplugin-OpenWebif
		git checkout --detach b79cfb76
		patch -p1 < OpenWebif.patch
		sh create_ipk.sh
		ar -x *.ipk
		tar -xvf data.tar.gz
		mv -f usr/lib/enigma2/python/Plugins/Extensions/OpenWebif /usr/local/e2/lib/enigma2/python/Plugins/Extensions
		rm -rf debian-binary usr *.gz *.ipk
		cd ..
	fi

	# Build python e2openplugin SetPicon
	if [ ! -d e2openplugin-OpenWebif ]; then
		set -e
		set -o pipefail
	else
		echo ""
		echo "**************************** OK. Go to the next step. ******************************"
		echo ""
		git clone https://github.com/E2OpenPlugins/e2openplugin-SetPicon.git
		cd ../..
		cp patches/SetPicon.patch plugins/e2openplugin/e2openplugin-SetPicon
		cd plugins/e2openplugin/e2openplugin-SetPicon
		git checkout --detach 1ec3cace
		patch -p1 < SetPicon.patch
		if [ "$release" = "20.04" ]; then
			python2 setup.py install
		else
			python setup.py install
		fi
		mv -f /usr/local/lib/python2.7/dist-packages/Extensions/SetPicon $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions
		mv -f /usr/local/lib/python2.7/dist-packages/enigma2_plugin_extensions_setpicon* $INSTALL_E2DIR/lib/enigma2/python/Plugins
		cp -rfv plugin/locale $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/SetPicon
		cd ..
	fi

	# Build python e2openplugin SnmpAgent
	if [ ! -d e2openplugin-SetPicon ]; then
		set -e
		set -o pipefail
	else
		echo ""
		echo "**************************** OK. Go to the next step. ******************************"
		echo ""
		git clone https://github.com/E2OpenPlugins/e2openplugin-SnmpAgent.git
		cd ../..
		cp patches/SnmpAgent.patch plugins/e2openplugin/e2openplugin-SnmpAgent
		cd plugins/e2openplugin/e2openplugin-SnmpAgent
		patch -p1 < SnmpAgent.patch
		if [ "$release" = "20.04" ]; then
			python2 setup.py install
		else
			python setup.py install
		fi
		mv -f /usr/local/lib/python2.7/dist-packages/Extensions/SnmpAgent $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions
		mv -f /usr/local/lib/python2.7/dist-packages/enigma2_plugin_extensions_snmpagent* $INSTALL_E2DIR/lib/enigma2/python/Plugins
		cp -rfv plugin/locale $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/SnmpAgent
		cd ..
	fi

	# Build python e2openplugin SimpleUmount
	if [ ! -d e2openplugin-SnmpAgent ]; then
		set -e
		set -o pipefail
	else
		echo ""
		echo "**************************** OK. Go to the next step. ******************************"
		echo ""
		git clone https://github.com/E2OpenPlugins/e2openplugin-SimpleUmount.git
		cd ../..
		cp patches/SimpleUmount.patch plugins/e2openplugin/e2openplugin-SimpleUmount
		cd plugins/e2openplugin/e2openplugin-SimpleUmount
		patch -p1 < SimpleUmount.patch
		if [ "$release" = "20.04" ]; then
			python2 setup.py install
		else
			python setup.py install
		fi
		mv -f /usr/local/lib/python2.7/dist-packages/Extensions/SimpleUmount $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions
		mv -f /usr/local/lib/python2.7/dist-packages/enigma2_plugin_extensions_simpleumount* $INSTALL_E2DIR/lib/enigma2/python/Plugins
		cp -rfv plugin/locale $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/SimpleUmount
		cd ..
	fi

	# Build python e2openplugin Foreca
	if [ ! -d e2openplugin-SimpleUmount ]; then
		set -e
		set -o pipefail
	else
		echo ""
		echo "**************************** OK. Go to the next step. ******************************"
		echo ""
		git clone https://github.com/E2OpenPlugins/e2openplugin-Foreca.git
		rpl "Foreca - прогноз погоды" "'Foreca' - Прогноз погоды" e2openplugin-Foreca/plugin/locale/ru/LC_MESSAGES/Foreca.po
		rpl '\x1b' 'KEY_ESC' e2openplugin-Foreca/plugin/keymap.xml
		cd e2openplugin-Foreca
		if [ "$release" = "20.04" ]; then
			python2 setup.py install
		else
			python setup.py install
		fi
		mv -f /usr/local/lib/python2.7/dist-packages/Extensions/Foreca $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions
		mv -f /usr/local/lib/python2.7/dist-packages/enigma2_plugin_extensions_foreca* $INSTALL_E2DIR/lib/enigma2/python/Plugins
		cp -rfv plugin/locale $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/Foreca
		cd ..
	fi

	# Build python plugin YouTube
	if [ ! -d e2openplugin-SimpleUmount ]; then
		set -e
		set -o pipefail
	else
		echo ""
		echo "**************************** OK. Go to the next step. ******************************"
		echo ""
		git clone https://github.com/Taapat/enigma2-plugin-youtube.git
		cd enigma2-plugin-youtube
		if [ "$release" = "20.04" ]; then
			python2 setup.py install
		else
			python setup.py install
		fi
		mv -f /usr/local/lib/python2.7/dist-packages/Extensions/YouTube $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions
		mv -f /usr/local/lib/python2.7/dist-packages/enigma2_plugin_extensions_youtube* $INSTALL_E2DIR/lib/enigma2/python/Plugins
		cp -rfv build/lib/Extensions/YouTube/locale $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/YouTube
		cd ..
	fi

	# Build python plugin OscamStatus
	if [ ! -d enigma2-plugin-youtube ]; then
		set -e
		set -o pipefail
	else
		echo ""
		echo "**************************** OK. Go to the next step. ******************************"
		echo ""
		git clone https://github.com/E2OpenPlugins/e2openplugin-OscamStatus.git
		cd ../..
		cp patches/OscamStatus.patch plugins/e2openplugin/e2openplugin-OscamStatus
		cd plugins/e2openplugin/e2openplugin-OscamStatus
		patch -p1 < OscamStatus.patch
		find plugin/locale -name "*.mo" -exec rm {} \;
		if [ "$release" = "20.04" ]; then
			python2 setup.py install
		else
			python setup.py install
		fi
		mv -f /usr/local/lib/python2.7/dist-packages/Extensions/OscamStatus $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions
		mv -f /usr/local/lib/python2.7/dist-packages/enigma2_plugin_extensions_oscamstatus* $INSTALL_E2DIR/lib/enigma2/python/Plugins
		cp -rfv plugin/locale $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/OscamStatus
		cd ..
	fi

	# Build python plugin IPTVPlayer
	if [ ! -d e2openplugin-OscamStatus ]; then
		set -e
		set -o pipefail
		# Message if error at any point of script
		echo ""
		echo "************ Forced stop script execution. It maybe сompilation error, *************"
		echo "************** lost Internet connection or the server not responding. **************"
		echo "*********************** Check the log for more information. ************************"
		echo ""
	else
		echo ""
		echo "**************************** OK. Go to the next step. ******************************"
		echo ""
		rm -f /usr/lib/librtmp.so.1
		git clone https://gitlab.com/maxbambi/e2iplayer.git
		#git clone https://gitlab.com/zadmario/e2iplayer.git
		#git clone https://github.com/persianpros/e2iplayer.git
		cd ../..
		cp -r pre/icons plugins/e2openplugin/e2iplayer/IPTVPlayer
		cp patches/E2IPlayer.patch plugins/e2openplugin/e2iplayer
		cd plugins/e2openplugin/e2iplayer
		git checkout --detach 62d1cd9c
		patch -p1 < E2IPlayer.patch
		rm -rf IPTVPlayer/locale/uk
		rm -f IPTVPlayer/locale/ru/LC_MESSAGES/.gitkeep
		if [ "$release" = "20.04" ]; then
			python2 setup_translate.py
			python2 setup.py install
		else
			python setup_translate.py
			python setup.py install
		fi
		mv -f /usr/local/lib/python2.7/dist-packages/Extensions/IPTVPlayer $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions
		mv -f /usr/local/lib/python2.7/dist-packages/enigma2_plugin_extensions_iptvplayer* $INSTALL_E2DIR/lib/enigma2/python/Plugins
		cp -rfv IPTVPlayer/locale $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/IPTVPlayer
		wget http://iptvplayer.vline.pl/resources/bin/i686/_subparser.so
		chmod 755 _subparser.so
		mv -f _subparser.so $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/IPTVPlayer/libs/iptvsubparser
		wget http://iptvplayer.vline.pl/resources/bin/i686/duk
		chmod 755 duk
		mv -f duk $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/IPTVPlayer/bin
		rm -f /usr/bin/duk
		wget http://iptvplayer.vline.pl/resources/bin/i686/hlsdl_static_curl_openssl.1.0.2
		chmod 755 hlsdl_static_curl_openssl.1.0.2
		mv -f hlsdl_static_curl_openssl.1.0.2 $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/IPTVPlayer/bin/hlsdl
		rm -f /usr/bin/hlsdl
		wget http://iptvplayer.vline.pl/resources/bin/i686/f4mdump_openssl.1.0.2
		chmod 755 f4mdump_openssl.1.0.2
		mv -f f4mdump_openssl.1.0.2 $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/IPTVPlayer/bin/f4mdump
		rm -f /usr/bin/f4mdump
		wget http://iptvplayer.vline.pl/resources/bin/i686/uchardet
		chmod 755 uchardet
		mv -f uchardet $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/IPTVPlayer/bin
		wget http://iptvplayer.vline.pl/resources/bin/i686/wget_openssl.1.0.2
		chmod 755 wget_openssl.1.0.2
		mv -f wget_openssl.1.0.2 $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/IPTVPlayer/bin/fullwget
		cd ..

		if [ -d e2iplayer ]; then
			if [[ "$release" = "14.04" ]]; then
				echo "         *** release 14.04 ***           "
				wget http://iptvplayer.vline.pl/resources/bin/i686/gstplayer_gstreamer0.10
				mv -f gstplayer_gstreamer0.10 gstplayer
				chmod 755 gstplayer
				mv -f gstplayer $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/IPTVPlayer/bin
				rm -f /usr/bin/gstplayer
			fi
		else
				wget http://iptvplayer.vline.pl/resources/bin/i686/gstplayer_gstreamer1.0
				mv -f gstplayer_gstreamer1.0 gstplayer
				chmod 755 gstplayer
				mv -f gstplayer $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/IPTVPlayer/bin
			rm -f /usr/bin/gstplayer
		fi

		if grep "config.plugins.iptvplayer.wgetpath=/usr/bin/wget" $INSTALL_E2DIR/etc/enigma2/settings; then
			echo ""
			echo ""
			echo "*************************** Detected IPTVPlayer settings.***************************"
		else
			echo ""
			echo "******************* There are no iptvplayer settings. Adding...*********************"
			echo "config.plugins.iptvplayer.autoCheckForUpdate=false" >> $INSTALL_E2DIR/etc/enigma2/settings
			echo "config.plugins.iptvplayer.deleteIcons=0" >> $INSTALL_E2DIR/etc/enigma2/settings
			echo "config.plugins.iptvplayer.downgradePossible=true" >> $INSTALL_E2DIR/etc/enigma2/settings
			echo "config.plugins.iptvplayer.dukpath=/usr/local/e2/lib/enigma2/python/Plugins/Extensions/IPTVPlayer/bin/duk" >> $INSTALL_E2DIR/etc/enigma2/settings
			echo "config.plugins.iptvplayer.possibleUpdateType=sourcecode" >> $INSTALL_E2DIR/etc/enigma2/settings
			echo "config.plugins.iptvplayer.showinMainMenu=true" >> $INSTALL_E2DIR/etc/enigma2/settings
			echo "config.plugins.iptvplayer.uchardetpath=/usr/bin/uchardet" >> $INSTALL_E2DIR/etc/enigma2/settings
			echo "config.plugins.iptvplayer.wgetpath=/usr/bin/wget" >> $INSTALL_E2DIR/etc/enigma2/settings
		fi

		cd ../..

		# Copy files to $INSTALL_E2DIR
		echo ""
		echo "******************************** Copy  plugins E2PC ********************************"
		cp -rfv plugins/third-party-plugins/Plugins $INSTALL_E2DIR/lib/enigma2/python
		cp -fv pre/urllib.py /usr/lib/python2.7
		cp -rfv skins/* $INSTALL_E2DIR

		if [ ! -f /usr/local/bin/bitrate ]; then
			ln -sf /usr/local/e2/bin/bitrate /usr/local/bin
		fi

		# Create folder for softam keys and symlink for plugin 'navibar'
		if [ ! -d /var/keys ]; then
			mkdir -p /var/keys
		fi
		if [ ! -d /home/hdd/icons ]; then
			ln -s $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/navibar/icons /home/hdd
		fi

		# Removing old compiled pyc files
		find $INSTALL_E2DIR/lib/enigma2/python/ -name "*.py[o]" -exec rm {} \;

		# Compile other pyc files
		if [ "$release" = "20.04" ]; then
			python2 -m compileall $INSTALL_E2DIR/lib/enigma2/python
		else
			python -m compileall $INSTALL_E2DIR/lib/enigma2/python
		fi

		# Force recompile new pyc files
		#if [ "$release" = "20.04" ]; then
		#	python2 -m compileall -f $INSTALL_E2DIR/lib/enigma2/python
		#else
		#	python -m compileall -f $INSTALL_E2DIR/lib/enigma2/python
		#fi
		echo ""
		echo "************* Plugins, skins, E2PC python files installed successfully.*************"
	fi
else
	# End lock
	echo ""
	echo "************ Plugins folder is missing! Please run scripts step by step! ************"
fi
