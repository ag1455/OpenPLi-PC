#!/bin/bash

# Build and install plugins for enigma2pc

release=$(lsb_release -a 2>/dev/null | grep -i release | awk ' { print $2 } ')
INSTALL_E2DIR="/usr/local/e2"
MAKE_J="9"

# This is the lock from the unpredictable script actions in the root directory in the absence of the plugins folder.
if [ -d plugins ]; then
	cd plugins/enigma2-plugins

	# Build enigma2 cpp plugins:
	echo ""
	echo "************************** OK. Let's build the plugins. ****************************"
	echo ""
	PKG="servicemp3"
	VER="aa60f9a1d0113eaccf6926c559b8202368fde857"
	if [ -d $PKG ]; then
		rm -rf $PKG
	fi
	wget https://github.com/OpenPLi/servicemp3/archive/$VER.zip
	unzip $VER.zip
	rm $VER.zip
	mv $PKG-$VER $PKG
	cd ../..
	cp -fv patches/servicemp3.patch plugins/enigma2-plugins/$PKG
	cd plugins/enigma2-plugins/$PKG
	patch -p1 < servicemp3.patch
	cd ..

	if [[ "$release" = "14.04" ]]; then
		echo ""
		echo "************************************************************************************"
		echo "                              *** release 14.04 ***"
		echo "                               *** used g++-8 ***"
		echo "************************************************************************************"
		echo ""
		export CXX=/usr/bin/g++-8
	elif [[ "$release" = "16.04" ]]; then
		echo ""
		echo "************************************************************************************"
		echo "                             *** release 16.04 ***"
		echo "                              *** used g++-8 ***"
		echo "************************************************************************************"
		echo ""
		export CXX=/usr/bin/g++-8
	elif [[ "$release" = "18.04" ]]; then
		echo ""
		echo "************************************************************************************"
		echo "                             *** release 18.04 ***"
		echo "                              *** used g++-8 ***"
		echo "************************************************************************************"
    		echo ""
		export CXX=/usr/bin/g++-8
	elif [[ "$release" = "20.04" ]]; then
		echo ""
		echo "************************************************************************************"
		echo "                             *** release 20.04 ***"
		echo "                              *** used g++-9 ***"
		echo "************************************************************************************"
		echo ""
		export CXX=/usr/bin/g++-9
	elif [[ "$release" = "21.10" ]]; then
		echo ""
		echo "************************************************************************************"
		echo "                             *** release 21.10 ***"
		echo "                              *** used g++-11 ***"
		echo "************************************************************************************"
		echo ""
		cd ../..
		cp -fv pre/include/rpc/* /usr/include/rpc
		cd plugins/enigma2-plugins
		export CXX=/usr/bin/g++-11
	fi

	#autoupdate
	autoreconf -i
	PKG_CONFIG_PATH=$INSTALL_E2DIR/lib/pkgconfig ./configure --prefix=$INSTALL_E2DIR
	make -j"$MAKE_J"
	make install
	cd ..

	if [ ! -d e2openplugin ]; then
		mkdir e2openplugin
	fi

	# Build e2openplugin-StreamInterface:
	if [ ! -d enigma2-plugins/servicemp3 ]; then
		set -e
		set -o pipefail
	else
		echo ""
		echo "**************************** OK. Go to the next step. ******************************"
		echo ""
		cd e2openplugin
		PKG="e2openplugin-StreamInterface"
		if [ -d $PKG ]; then
			rm -rf $PKG
		fi
		if [ -d $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/StreamInterface ]; then
			rm -rf $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/StreamInterface
		fi
		wget https://github.com/E2OpenPlugins/e2openplugin-StreamInterface/archive/refs/heads/master.zip
		unzip master.zip
		rm master.zip
		mv $PKG-master $PKG
		cd $PKG
		if [ "$release" = "20.04" ]; then
			python2 setup.py install
		elif [ "$release" = "21.10" ]; then
			python2 setup.py install
		else
			python setup.py install
		fi
		mv -f /usr/local/lib/python2.7/dist-packages/Extensions/StreamInterface $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions
		mv -f /usr/local/lib/python2.7/dist-packages/enigma2_plugin_extensions_streaminterface* $INSTALL_E2DIR/lib/enigma2/python/Plugins
		cp -rfv plugin/locale $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/StreamInterface
		cd ..
	fi

	# Build e2openplugin-SystemTools
	if [ ! -d e2openplugin-StreamInterface ]; then
		set -e
		set -o pipefail
	else
		echo ""
		echo "**************************** OK. Go to the next step. ******************************"
		echo ""
		PKG="e2openplugin-SystemTools"
		VER="7b12408f5f3542aa87de1efad21aac644b48d430"
		if [ -d $PKG ]; then
			rm -rf $PKG
		fi
		if [ -d $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/SystemTools ]; then
			rm -rf $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/SystemTools
		fi
		wget https://github.com/E2OpenPlugins/e2openplugin-SystemTools/archive/$VER.zip
		unzip $VER.zip
		rm $VER.zip
		mv $PKG-$VER $PKG
		cd ../..
		cp -fv patches/SystemTools.patch plugins/e2openplugin/$PKG
		cd plugins/e2openplugin/$PKG
		patch -p1 < SystemTools.patch
		if [ "$release" = "20.04" ]; then
			python2 setup.py install
		elif [ "$release" = "21.10" ]; then
			python2 setup.py install
		else
			python setup.py install
		fi
		mv -f /usr/local/lib/python2.7/dist-packages/Extensions/SystemTools $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions
		mv -f /usr/local/lib/python2.7/dist-packages/enigma2_plugin_extensions_systemtools* $INSTALL_E2DIR/lib/enigma2/python/Plugins
		cp -rfv plugin/locale $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/SystemTools
		cd ..
	fi

	# Build e2openplugin-AddStreamUrl
	if [ ! -d e2openplugin-SystemTools ]; then
		set -e
		set -o pipefail
	else
		echo ""
		echo "**************************** OK. Go to the next step. ******************************"
		echo ""
		PKG="e2openplugin-AddStreamUrl"
		if [ -d $PKG ]; then
			rm -rf $PKG
		fi
		if [ -d $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/AddStreamUrl ]; then
			rm -rf $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/AddStreamUrl
		fi
		wget https://github.com/E2OpenPlugins/e2openplugin-AddStreamUrl/archive/refs/heads/master.zip
		unzip master.zip
		rm master.zip
		mv $PKG-master $PKG
		cd $PKG
		if [ "$release" = "20.04" ]; then
			python2 setup.py install
		elif [ "$release" = "21.10" ]; then
			python2 setup.py install
		else
			python setup.py install
		fi
		mv -f /usr/local/lib/python2.7/dist-packages/Extensions/AddStreamUrl $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions
		mv -f /usr/local/lib/python2.7/dist-packages/enigma2_plugin_extensions_addstreamurl* $INSTALL_E2DIR/lib/enigma2/python/Plugins
		cd ..
	fi

	# Build e2openplugin-OpenWebif
	if [ ! -d e2openplugin-AddStreamUrl ]; then
		set -e
		set -o pipefail
	else
		echo ""
		echo "**************************** OK. Go to the next step. ******************************"
		echo ""
		PKG="e2openplugin-OpenWebif"
		VER="b238b3770b90f49ba076987f66a4f042eb4b318e"
		VER1="7f53c0efcc7ebf5c79efa34d525721d9d195b597"
		if [ -d $PKG ]; then
			rm -rf $PKG
		fi
		if [ -d $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/OpenWebif ]; then
			rm -rf $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/OpenWebif
		fi
		if [ "$release" = "20.04" ]; then
			wget https://github.com/E2OpenPlugins/e2openplugin-OpenWebif/archive/$VER.zip
			unzip $VER.zip
			rm $VER.zip
			mv $PKG-$VER $PKG
			cd ../..
			cp -fv patches/OpenWebif-py3.patch plugins/e2openplugin/$PKG
		elif [ "$release" = "21.10" ]; then
			wget https://github.com/E2OpenPlugins/e2openplugin-OpenWebif/archive/$VER.zip
			unzip $VER.zip
			rm $VER.zip
			mv $PKG-$VER $PKG
			cd ../..
			cp -fv patches/OpenWebif-py3.patch plugins/e2openplugin/$PKG
		else
			wget https://github.com/E2OpenPlugins/e2openplugin-OpenWebif/archive/$VER1.zip
			unzip $VER1.zip
			rm $VER1.zip
			mv $PKG-$VER1 $PKG
			cd ../..
			cp -fv patches/OpenWebif-py2.patch plugins/e2openplugin/$PKG
		fi
		cd plugins/e2openplugin/$PKG
		patch -p1 < OpenWebif-*.patch
		mv CI/create_ipk.sh create_ipk.sh
		./create_ipk.sh
		ar -x *.ipk
		tar -xvf data.tar.gz
		mv -f usr/lib/enigma2/python/Plugins/Extensions/OpenWebif $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions
		rm -rf debian-binary usr *.gz *.ipk
		cd ..
	fi

	# Build e2openplugin-SetPicon
	if [ ! -d e2openplugin-OpenWebif ]; then
		set -e
		set -o pipefail
	else
		echo ""
		echo "**************************** OK. Go to the next step. ******************************"
		echo ""
		PKG="e2openplugin-SetPicon"
		VER="ef33e2657203fcb8039afbc2a49b9b059db0c5ee"
		if [ -d $PKG ]; then
			rm -rf $PKG
		fi
		if [ -d $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/SetPicon ]; then
			rm -rf $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/SetPicon
		fi
		wget https://github.com/E2OpenPlugins/e2openplugin-SetPicon/archive/$VER.zip
		unzip $VER.zip
		rm $VER.zip
		mv $PKG-$VER $PKG
		cd ../..
		cp -fv patches/SetPicon.patch plugins/e2openplugin/$PKG
		cd plugins/e2openplugin/$PKG
		patch -p1 < SetPicon.patch
		if [ "$release" = "20.04" ]; then
			python2 setup.py install
		elif [ "$release" = "21.10" ]; then
			python2 setup.py install
		else
			python setup.py install
		fi
		mv -f /usr/local/lib/python2.7/dist-packages/Extensions/SetPicon $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions
		mv -f /usr/local/lib/python2.7/dist-packages/enigma2_plugin_extensions_setpicon* $INSTALL_E2DIR/lib/enigma2/python/Plugins
		cp -rfv plugin/locale $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/SetPicon
		cd ..
	fi

	# Build e2openplugin-SnmpAgent
	if [ ! -d e2openplugin-SetPicon ]; then
		set -e
		set -o pipefail
	else
		echo ""
		echo "**************************** OK. Go to the next step. ******************************"
		echo ""
		PKG="e2openplugin-SnmpAgent"
		VER="31dd52b4277f273524622a8bf3678dff8e1ecf8e"
		if [ -d $PKG ]; then
			rm -rf $PKG
		fi
		if [ -d $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/SnmpAgent ]; then
			rm -rf $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/SnmpAgent
		fi
		wget https://github.com/E2OpenPlugins/e2openplugin-SnmpAgent/archive/$VER.zip
		unzip $VER.zip
		rm $VER.zip
		mv $PKG-$VER $PKG
		cd ../..
		cp -fv patches/SnmpAgent.patch plugins/e2openplugin/$PKG
		cd plugins/e2openplugin/$PKG
		patch -p1 < SnmpAgent.patch
		if [ "$release" = "20.04" ]; then
			python2 setup.py install
		elif [ "$release" = "21.10" ]; then
			python2 setup.py install
		else
			python setup.py install
		fi
		mv -f /usr/local/lib/python2.7/dist-packages/Extensions/SnmpAgent $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions
		mv -f /usr/local/lib/python2.7/dist-packages/enigma2_plugin_extensions_snmpagent* $INSTALL_E2DIR/lib/enigma2/python/Plugins
		cp -rfv plugin/locale $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/SnmpAgent
		cd ..
	fi

	# Build e2openplugin-SimpleUmount
	if [ ! -d e2openplugin-SnmpAgent ]; then
		set -e
		set -o pipefail
	else
		echo ""
		echo "**************************** OK. Go to the next step. ******************************"
		echo ""
		PKG="e2openplugin-SimpleUmount"
		VER="8c82986a90d77295d3c5bf70983667e2508f17d1"
		if [ -d $PKG ]; then
			rm -rf $PKG
		fi
		if [ -d $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/SimpleUmount ]; then
			rm -rf $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/SimpleUmount
		fi
		wget https://github.com/E2OpenPlugins/e2openplugin-SimpleUmount/archive/$VER.zip
		unzip $VER.zip
		rm $VER.zip
		mv $PKG-$VER $PKG
		cd ../..
		cp -fv patches/SimpleUmount.patch plugins/e2openplugin/$PKG
		cd plugins/e2openplugin/$PKG
		patch -p1 < SimpleUmount.patch
		if [ "$release" = "20.04" ]; then
			python2 setup.py install
		elif [ "$release" = "21.10" ]; then
			python2 setup.py install
		else
			python setup.py install
		fi
		mv -f /usr/local/lib/python2.7/dist-packages/Extensions/SimpleUmount $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions
		mv -f /usr/local/lib/python2.7/dist-packages/enigma2_plugin_extensions_simpleumount* $INSTALL_E2DIR/lib/enigma2/python/Plugins
		cp -rfv plugin/locale $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/SimpleUmount
		cd ..
	fi

	# Build e2openplugin-Foreca
	if [ ! -d e2openplugin-SimpleUmount ]; then
		set -e
		set -o pipefail
	else
		echo ""
		echo "**************************** OK. Go to the next step. ******************************"
		echo ""
		PKG="e2openplugin-Foreca"
		if [ -d $PKG ]; then
			rm -rf $PKG
		fi
		if [ -d $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/Foreca ]; then
			rm -rf $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/Foreca
		fi
		wget https://github.com/E2OpenPlugins/e2openplugin-Foreca/archive/refs/heads/master.zip
		unzip master.zip
		rm master.zip
		mv $PKG-master $PKG
		rpl "Foreca - прогноз погоды" "'Foreca' - Прогноз погоды" e2openplugin-Foreca/plugin/locale/ru/LC_MESSAGES/Foreca.po
		rpl '\x1b' 'KEY_ESC' e2openplugin-Foreca/plugin/keymap.xml
		cd $PKG
		if [ "$release" = "20.04" ]; then
			python2 setup.py install
		elif [ "$release" = "21.10" ]; then
			python2 setup.py install
		else
			python setup.py install
		fi
		mv -f /usr/local/lib/python2.7/dist-packages/Extensions/Foreca $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions
		mv -f /usr/local/lib/python2.7/dist-packages/enigma2_plugin_extensions_foreca* $INSTALL_E2DIR/lib/enigma2/python/Plugins
		cp -rfv plugin/locale $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/Foreca
		cd ..
	fi

	# Build enigma2-plugin-youtube
	if [ ! -d e2openplugin-SimpleUmount ]; then
		set -e
		set -o pipefail
	else
		echo ""
		echo "**************************** OK. Go to the next step. ******************************"
		echo ""
		PKG="enigma2-plugin-youtube"
		if [ -d $PKG ]; then
			rm -rf $PKG
		fi
		if [ -d $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/YouTube ]; then
			rm -rf $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/YouTube
		fi
		wget https://github.com/Taapat/enigma2-plugin-youtube/archive/refs/heads/master.zip
		unzip master.zip
		rm master.zip
		mv $PKG-master $PKG
		cd $PKG
		if [ "$release" = "20.04" ]; then
			python2 setup.py install
		elif [ "$release" = "21.10" ]; then
			python2 setup.py install
		else
			python setup.py install
		fi
		mv -f /usr/local/lib/python2.7/dist-packages/Extensions/YouTube $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions
		mv -f /usr/local/lib/python2.7/dist-packages/enigma2_plugin_extensions_youtube* $INSTALL_E2DIR/lib/enigma2/python/Plugins
		cp -rfv build/lib/Extensions/YouTube/locale $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/YouTube
		cd ..
	fi

	# Build e2openplugin-OscamStatus
	if [ ! -d enigma2-plugin-youtube ]; then
		set -e
		set -o pipefail
	else
		echo ""
		echo "**************************** OK. Go to the next step. ******************************"
		echo ""
		PKG="e2openplugin-OscamStatus"
		if [ -d $PKG ]; then
			rm -rf $PKG
		fi
		if [ -d $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/OscamStatus ]; then
			rm -rf $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/OscamStatus
		fi
		wget https://github.com/E2OpenPlugins/e2openplugin-OscamStatus/archive/refs/heads/master.zip
		unzip master.zip
		rm master.zip
		mv $PKG-master $PKG
		cd $PKG
		find plugin/locale -name "*.mo" -exec rm {} \;
		if [ "$release" = "20.04" ]; then
			python2 setup.py install
		elif [ "$release" = "21.10" ]; then
			python2 setup.py install
		else
			python setup.py install
		fi
		mv -f /usr/local/lib/python2.7/dist-packages/Extensions/OscamStatus $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions
		mv -f /usr/local/lib/python2.7/dist-packages/enigma2_plugin_extensions_oscamstatus* $INSTALL_E2DIR/lib/enigma2/python/Plugins
		cp -rfv plugin/locale $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/OscamStatus
		cd ..
	fi

	# Build enigma2-plugin-extensions-epgimport
	if [ ! -d e2openplugin-OscamStatus ]; then
		set -e
		set -o pipefail
	else
		echo ""
		echo "**************************** OK. Go to the next step. ******************************"
		echo ""
		PKG="enigma2-plugin-extensions-epgimport"
		VER="0f638f2b8d6a0c59895a4f5f772aebd81a8376f3"
		if [ -d $PKG ]; then
			rm -rf $PKG
		fi
		if [ -d $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/EPGImport ]; then
			rm -rf $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/EPGImport
		fi
		wget https://github.com/OpenPLi/$PKG/archive/$VER.zip
		unzip $VER.zip
		rm $VER.zip
		mv $PKG-$VER $PKG
		cd ../..
		cp -fv patches/EPGImport.patch plugins/e2openplugin/$PKG
		cd plugins/e2openplugin/$PKG
		patch -p1 < EPGImport.patch
		cd src
		if [ "$release" = "20.04" ]; then
			python2 setup.py install
		elif [ "$release" = "21.10" ]; then
			python2 setup.py install
		else
			python setup.py install
		fi
		mv -f /usr/local/lib/python2.7/dist-packages/Extensions/EPGImport $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions
		mv -f /usr/local/lib/python2.7/dist-packages/enigma2_plugin_extensions_xmltvimport* $INSTALL_E2DIR/lib/enigma2/python/Plugins
		cp -rfv EPGImport/locale $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/EPGImport
		cd ../..
	fi

	# Build e2iplayer
	if [ ! -d enigma2-plugin-extensions-epgimport ]; then
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
		PKG="e2iplayer"
		VER="8de52879b072b946f699d820bd2061268a90bc3f"
		if [ -d $PKG ]; then
			rm -rf $PKG
		fi
		if [ -d $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/IPTVPlayer ]; then
			rm -rf $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/IPTVPlayer
		fi
		rm -f /usr/lib/librtmp.so.1
		wget https://gitlab.com/zadmario/e2iplayer/-/archive/$VER/e2iplayer-$VER.zip
		unzip $PKG-$VER.zip
		rm $PKG-$VER.zip
		mv $PKG-$VER $PKG
		cd ../..
		cp -rv pre/icons plugins/e2openplugin/$PKG/IPTVPlayer
		cp -fv patches/E2IPlayer.patch plugins/e2openplugin/$PKG
		cd plugins/e2openplugin/$PKG
		patch -p1 < E2IPlayer.patch
		rm -f IPTVPlayer/locale/ru/LC_MESSAGES/.gitkeep
		if [ "$release" = "20.04" ]; then
			python2 setup_translate.py
			python2 setup.py install
		elif [ "$release" = "21.10" ]; then
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
				echo "         *** release 14.04 ***"
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
			echo "config.plugins.iptvplayer.dukpath=$INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/IPTVPlayer/bin/duk" >> $INSTALL_E2DIR/etc/enigma2/settings
			echo "config.plugins.iptvplayer.possibleUpdateType=sourcecode" >> $INSTALL_E2DIR/etc/enigma2/settings
			echo "config.plugins.iptvplayer.showinMainMenu=true" >> $INSTALL_E2DIR/etc/enigma2/settings
			echo "config.plugins.iptvplayer.uchardetpath=/usr/bin/uchardet" >> $INSTALL_E2DIR/etc/enigma2/settings
			echo "config.plugins.iptvplayer.wgetpath=/usr/bin/wget" >> $INSTALL_E2DIR/etc/enigma2/settings
		fi
	fi

	cd ../..

	# Temporarily
	if [ -d $INSTALL_E2DIR/lib/enigma2/python/Plugins/PLi ]; then
		rm -rf $INSTALL_E2DIR/lib/enigma2/python/Plugins/PLi
	fi

	# For use *.m3u8 in the /tmp folder
	chown $(who | awk '{print $1}'):$(who | awk '{print $1}') /tmp

	# Copy files to $INSTALL_E2DIR
	echo ""
	echo "******************************** Copy  plugins E2PC ********************************"
	cp -rfv plugins/third-party-plugins/Plugins $INSTALL_E2DIR/lib/enigma2/python
	cp -fv pre/python/urllib.py /usr/lib/python2.7
	cp -rfv pre/epgimport $INSTALL_E2DIR/etc
	cp -rfv pre/xmltvimport $INSTALL_E2DIR/etc
	cp -rfv skins/* $INSTALL_E2DIR

	if [ ! -f /usr/local/bin/bitrate ]; then
		ln -sf $INSTALL_E2DIR/bin/bitrate /usr/local/bin
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
	elif [ "$release" = "21.10" ]; then
		python2 -m compileall $INSTALL_E2DIR/lib/enigma2/python
	else
		python -m compileall $INSTALL_E2DIR/lib/enigma2/python
	fi

	# Force recompile new pyc files
	#if [ "$release" = "20.04" ]; then
	#	python2 -m compileall -f $INSTALL_E2DIR/lib/enigma2/python
	#elif [ "$release" = "21.10" ]; then
	#	python2 -m compileall -f $INSTALL_E2DIR/lib/enigma2/python
	#else
	#	python -m compileall -f $INSTALL_E2DIR/lib/enigma2/python
	#fi
	echo ""
	echo "************* Plugins, skins, E2PC python files installed successfully.*************"
else
	echo ""
	echo "************ Plugins folder is missing! Please run scripts step by step! ************"
# End lock
fi
