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
	cp -fv patches/$PKG.patch plugins/enigma2-plugins/$PKG
	cd plugins/enigma2-plugins/$PKG
	patch -p1 < $PKG.patch
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
	elif [[ "$release" = "22.04" ]]; then
		echo ""
		echo "************************************************************************************"
		echo "                             *** release 22.04 ***"
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
		PKG_="StreamInterface"
		if [ -d $PKG ]; then
			rm -rf $PKG
		fi
		if [ -d $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/$PKG_ ]; then
			rm -rf $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/$PKG_
		fi
		wget https://github.com/E2OpenPlugins/$PKG/archive/refs/heads/master.zip
		unzip master.zip
		rm master.zip
		mv $PKG-master $PKG
		cd $PKG
		if [ "$release" = "20.04" ]; then
			python2 setup.py install
		elif [ "$release" = "22.04" ]; then
			python2 setup.py install
		else
			python setup.py install
		fi
		mv -f /usr/local/lib/python2.7/dist-packages/Extensions/$PKG_ $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions
		mv -f /usr/local/lib/python2.7/dist-packages/enigma2_plugin_extensions_streaminterface* $INSTALL_E2DIR/lib/enigma2/python/Plugins
		cp -rfv plugin/locale $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/$PKG_
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
		PKG_="SystemTools"
		VER="7b12408f5f3542aa87de1efad21aac644b48d430"
		if [ -d $PKG ]; then
			rm -rf $PKG
		fi
		if [ -d $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/$PKG_ ]; then
			rm -rf $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/$PKG_
		fi
		wget https://github.com/E2OpenPlugins/$PKG/archive/$VER.zip
		unzip $VER.zip
		rm $VER.zip
		mv $PKG-$VER $PKG
		cd ../..
		cp -fv patches/$PKG_.patch plugins/e2openplugin/$PKG
		cd plugins/e2openplugin/$PKG
		patch -p1 < $PKG_.patch
		if [ "$release" = "20.04" ]; then
			python2 setup.py install
		elif [ "$release" = "22.04" ]; then
			python2 setup.py install
		else
			python setup.py install
		fi
		mv -f /usr/local/lib/python2.7/dist-packages/Extensions/$PKG_ $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions
		mv -f /usr/local/lib/python2.7/dist-packages/enigma2_plugin_extensions_systemtools* $INSTALL_E2DIR/lib/enigma2/python/Plugins
		cp -rfv plugin/locale $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/$PKG_
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
		PKG_="AddStreamUrl"
		if [ -d $PKG ]; then
			rm -rf $PKG
		fi
		if [ -d $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/$PKG_ ]; then
			rm -rf $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/$PKG_
		fi
		wget https://github.com/E2OpenPlugins/$PKG/archive/refs/heads/master.zip
		unzip master.zip
		rm master.zip
		mv $PKG-master $PKG
		cd $PKG
		if [ "$release" = "20.04" ]; then
			python2 setup.py install
		elif [ "$release" = "22.04" ]; then
			python2 setup.py install
		else
			python setup.py install
		fi
		mv -f /usr/local/lib/python2.7/dist-packages/Extensions/$PKG_ $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions
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
		PKG_="OpenWebif"
		VER="3bbc28e92b8b3b8fccceb1ff5648d1435d890de8"
		VER1="7f53c0efcc7ebf5c79efa34d525721d9d195b597"
		if [ -d $PKG ]; then
			rm -rf $PKG
		fi
		if [ -d $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/$PKG_ ]; then
			rm -rf $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/$PKG_
		fi
		if [ "$release" = "20.04" ]; then
			wget https://github.com/E2OpenPlugins/$PKG/archive/$VER.zip
			unzip $VER.zip
			rm $VER.zip
			mv $PKG-$VER $PKG
			cd ../..
			cp -fv patches/$PKG_-py3.patch plugins/e2openplugin/$PKG
		elif [ "$release" = "22.04" ]; then
			wget https://github.com/E2OpenPlugins/$PKG/archive/$VER.zip
			unzip $VER.zip
			rm $VER.zip
			mv $PKG-$VER $PKG
			cd ../..
			cp -fv patches/$PKG_-py3.patch plugins/e2openplugin/$PKG
		else
			wget https://github.com/E2OpenPlugins/$PKG/archive/$VER1.zip
			unzip $VER1.zip
			rm $VER1.zip
			mv $PKG-$VER1 $PKG
			cd ../..
			cp -fv patches/$PKG_-py2.patch plugins/e2openplugin/$PKG
		fi
		cd plugins/e2openplugin/$PKG
		patch -p1 < $PKG_-*.patch
		mv CI/create_ipk.sh create_ipk.sh
		./create_ipk.sh
		ar -x *.ipk
		tar -xvf data.tar.gz
		mv -f usr/lib/enigma2/python/Plugins/Extensions/$PKG_ $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions
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
		PKG_="SetPicon"
		VER="4703f27cb67cb858e9ecdc14df4e31e42a9e7308"
		if [ -d $PKG ]; then
			rm -rf $PKG
		fi
		if [ -d $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/$PKG_ ]; then
			rm -rf $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/$PKG_
		fi
		wget https://github.com/E2OpenPlugins/$PKG/archive/$VER.zip
		unzip $VER.zip
		rm $VER.zip
		mv $PKG-$VER $PKG
		cd ../..
		cp -fv patches/$PKG_.patch plugins/e2openplugin/$PKG
		cd plugins/e2openplugin/$PKG
		patch -p1 < $PKG_.patch
		if [ "$release" = "20.04" ]; then
			python2 setup.py install
		elif [ "$release" = "22.04" ]; then
			python2 setup.py install
		else
			python setup.py install
		fi
		mv -f /usr/local/lib/python2.7/dist-packages/Extensions/$PKG_ $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions
		mv -f /usr/local/lib/python2.7/dist-packages/enigma2_plugin_extensions_setpicon* $INSTALL_E2DIR/lib/enigma2/python/Plugins
		cp -rfv plugin/locale $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/$PKG_
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
		PKG_="SnmpAgent"
		VER="31dd52b4277f273524622a8bf3678dff8e1ecf8e"
		if [ -d $PKG ]; then
			rm -rf $PKG
		fi
		if [ -d $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/$PKG_ ]; then
			rm -rf $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/$PKG_
		fi
		wget https://github.com/E2OpenPlugins/$PKG/archive/$VER.zip
		unzip $VER.zip
		rm $VER.zip
		mv $PKG-$VER $PKG
		cd ../..
		cp -fv patches/$PKG_.patch plugins/e2openplugin/$PKG
		cd plugins/e2openplugin/$PKG
		patch -p1 < $PKG_.patch
		if [ "$release" = "20.04" ]; then
			python2 setup.py install
		elif [ "$release" = "22.04" ]; then
			python2 setup.py install
		else
			python setup.py install
		fi
		mv -f /usr/local/lib/python2.7/dist-packages/Extensions/$PKG_ $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions
		mv -f /usr/local/lib/python2.7/dist-packages/enigma2_plugin_extensions_snmpagent* $INSTALL_E2DIR/lib/enigma2/python/Plugins
		cp -rfv plugin/locale $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/$PKG_
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
		PKG_="SimpleUmount"
		VER="8c82986a90d77295d3c5bf70983667e2508f17d1"
		if [ -d $PKG ]; then
			rm -rf $PKG
		fi
		if [ -d $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/$PKG_ ]; then
			rm -rf $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/$PKG_
		fi
		wget https://github.com/E2OpenPlugins/$PKG/archive/$VER.zip
		unzip $VER.zip
		rm $VER.zip
		mv $PKG-$VER $PKG
		cd ../..
		cp -fv patches/$PKG_.patch plugins/e2openplugin/$PKG
		cd plugins/e2openplugin/$PKG
		patch -p1 < $PKG_.patch
		if [ "$release" = "20.04" ]; then
			python2 setup.py install
		elif [ "$release" = "22.04" ]; then
			python2 setup.py install
		else
			python setup.py install
		fi
		mv -f /usr/local/lib/python2.7/dist-packages/Extensions/$PKG_ $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions
		mv -f /usr/local/lib/python2.7/dist-packages/enigma2_plugin_extensions_simpleumount* $INSTALL_E2DIR/lib/enigma2/python/Plugins
		cp -rfv plugin/locale $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/$PKG_
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
		PKG_="Foreca"
		if [ -d $PKG ]; then
			rm -rf $PKG
		fi
		if [ -d $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/$PKG_ ]; then
			rm -rf $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/$PKG_
		fi
		wget https://github.com/E2OpenPlugins/$PKG/archive/refs/heads/master.zip
		unzip master.zip
		rm master.zip
		mv $PKG-master $PKG
		cd $PKG
		rpl "Foreca - прогноз погоды" "'Foreca' - Прогноз погоды" plugin/locale/ru/LC_MESSAGES/Foreca.po
		if [ "$release" = "20.04" ]; then
			rpl "\x1b" "KEY_ESC" plugin/keymap.xml
			python2 setup.py install
		elif [ "$release" = "22.04" ]; then
			rpl -F "\x1b" "KEY_ESC" plugin/keymap.xml
			python2 setup.py install
		else
			rpl "\x1b" "KEY_ESC" plugin/keymap.xml
			python setup.py install
		fi
		mv -f /usr/local/lib/python2.7/dist-packages/Extensions/$PKG_ $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions
		mv -f /usr/local/lib/python2.7/dist-packages/enigma2_plugin_extensions_foreca* $INSTALL_E2DIR/lib/enigma2/python/Plugins
		cp -rfv plugin/locale $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/$PKG_
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
		PKG_="YouTube"
		if [ -d $PKG ]; then
			rm -rf $PKG
		fi
		if [ -d $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/$PKG_ ]; then
			rm -rf $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/$PKG_
		fi
		wget https://github.com/Taapat/$PKG/archive/refs/heads/master.zip
		unzip master.zip
		rm master.zip
		mv $PKG-master $PKG
		cd $PKG
		if [ "$release" = "20.04" ]; then
			python2 setup.py install
		elif [ "$release" = "22.04" ]; then
			python2 setup.py install
		else
			python setup.py install
		fi
		mv -f /usr/local/lib/python2.7/dist-packages/Extensions/$PKG_ $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions
		mv -f /usr/local/lib/python2.7/dist-packages/enigma2_plugin_extensions_youtube* $INSTALL_E2DIR/lib/enigma2/python/Plugins
		cp -rfv build/lib/Extensions/YouTube/locale $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/$PKG_
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
		PKG_="OscamStatus"
		if [ -d $PKG ]; then
			rm -rf $PKG
		fi
		if [ -d $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/$PKG_ ]; then
			rm -rf $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/$PKG_
		fi
		wget https://github.com/E2OpenPlugins/$PKG/archive/refs/heads/master.zip
		unzip master.zip
		rm master.zip
		mv $PKG-master $PKG
		cd $PKG
		find plugin/locale -name "*.mo" -exec rm {} \;
		if [ "$release" = "20.04" ]; then
			python2 setup.py install
		elif [ "$release" = "22.04" ]; then
			python2 setup.py install
		else
			python setup.py install
		fi
		mv -f /usr/local/lib/python2.7/dist-packages/Extensions/$PKG_ $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions
		mv -f /usr/local/lib/python2.7/dist-packages/enigma2_plugin_extensions_oscamstatus* $INSTALL_E2DIR/lib/enigma2/python/Plugins
		cp -rfv plugin/locale $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/$PKG_
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
		PKG_="EPGImport"
		VER="a82a48233dad402a7e5ed69edfa2720a793f3dcd"
		if [ -d $PKG ]; then
			rm -rf $PKG
		fi
		if [ -d $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/$PKG_ ]; then
			rm -rf $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/$PKG_
		fi
		wget https://github.com/OpenPLi/$PKG/archive/$VER.zip
		unzip $VER.zip
		rm $VER.zip
		mv $PKG-$VER $PKG
		cd ../..
		cp -fv patches/$PKG_.patch plugins/e2openplugin/$PKG
		cd plugins/e2openplugin/$PKG
		patch -p1 < $PKG_.patch
		cd src
		if [ "$release" = "20.04" ]; then
			python2 setup.py install
		elif [ "$release" = "22.04" ]; then
			python2 setup.py install
		else
			python setup.py install
		fi
		mv -f /usr/local/lib/python2.7/dist-packages/Extensions/$PKG_ $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions
		mv -f /usr/local/lib/python2.7/dist-packages/enigma2_plugin_extensions_xmltvimport* $INSTALL_E2DIR/lib/enigma2/python/Plugins
		cp -rfv $PKG_/locale $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/$PKG_
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
		PKG_="IPTVPlayer"
		PKG__="E2IPlayer"
		VER="3a026b0a1974f751a08da94a0d7e6c35090366d2"
		if [ -d $PKG ]; then
			rm -rf $PKG
		fi
		if [ -d $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/$PKG_ ]; then
			rm -rf $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/$PKG_
		fi
		rm -f /usr/lib/librtmp.so.1
		wget https://gitlab.com/zadmario/e2iplayer/-/archive/$VER/e2iplayer-$VER.zip
		unzip $PKG-$VER.zip
		rm $PKG-$VER.zip
		mv $PKG-$VER $PKG
		cd ../..
		cp -rv pre/icons plugins/e2openplugin/$PKG/$PKG_
		cp -fv patches/$PKG__.patch plugins/e2openplugin/$PKG
		cd plugins/e2openplugin/$PKG
		patch -p1 < $PKG__.patch
		rm -f IPTVPlayer/locale/ru/LC_MESSAGES/.gitkeep
		if [ "$release" = "20.04" ]; then
			python2 setup_translate.py
			python2 setup.py install
		elif [ "$release" = "22.04" ]; then
			python2 setup_translate.py
			python2 setup.py install
		else
			python setup_translate.py
			python setup.py install
		fi
		mv -f /usr/local/lib/python2.7/dist-packages/Extensions/$PKG_ $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions
		mv -f /usr/local/lib/python2.7/dist-packages/enigma2_plugin_extensions_iptvplayer* $INSTALL_E2DIR/lib/enigma2/python/Plugins
		cp -rfv IPTVPlayer/locale $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/$PKG_
		wget http://iptvplayer.vline.pl/resources/bin/i686/_subparser.so
		chmod 755 _subparser.so
		mv -f _subparser.so $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/$PKG_/libs/iptvsubparser
		wget http://iptvplayer.vline.pl/resources/bin/i686/duk
		chmod 755 duk
		mv -f duk $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/$PKG_/bin
		rm -f /usr/bin/duk
		wget http://iptvplayer.vline.pl/resources/bin/i686/hlsdl_static_curl_openssl.1.0.2
		chmod 755 hlsdl_static_curl_openssl.1.0.2
		mv -f hlsdl_static_curl_openssl.1.0.2 $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/$PKG_/bin/hlsdl
		rm -f /usr/bin/hlsdl
		wget http://iptvplayer.vline.pl/resources/bin/i686/f4mdump_openssl.1.0.2
		chmod 755 f4mdump_openssl.1.0.2
		mv -f f4mdump_openssl.1.0.2 $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/$PKG_/bin/f4mdump
		rm -f /usr/bin/f4mdump
		wget http://iptvplayer.vline.pl/resources/bin/i686/uchardet
		chmod 755 uchardet
		mv -f uchardet $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/$PKG_/bin
		wget http://iptvplayer.vline.pl/resources/bin/i686/wget_openssl.1.0.2
		chmod 755 wget_openssl.1.0.2
		mv -f wget_openssl.1.0.2 $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/$PKG_/bin/fullwget
		cd ..
		if [ -d e2iplayer ]; then
			if [[ "$release" = "14.04" ]]; then
				echo "         *** release 14.04 ***"
				wget http://iptvplayer.vline.pl/resources/bin/i686/gstplayer_gstreamer0.10
				mv -f gstplayer_gstreamer0.10 gstplayer
				chmod 755 gstplayer
				mv -f gstplayer $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/$PKG_/bin
				rm -f /usr/bin/gstplayer
			fi
		else
			wget http://iptvplayer.vline.pl/resources/bin/i686/gstplayer_gstreamer1.0
			mv -f gstplayer_gstreamer1.0 gstplayer
			chmod 755 gstplayer
			mv -f gstplayer $INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/$PKG_/bin
			rm -f /usr/bin/gstplayer
		fi
		if grep "config.plugins.iptvplayer.wgetpath=/usr/bin/wget" $INSTALL_E2DIR/etc/enigma2/settings; then
			echo ""
			echo ""
			echo "*************************** Detected $PKG_ settings.***************************"
		else
			echo ""
			echo "******************* There are no iptvplayer settings. Adding...*********************"
			echo "config.plugins.iptvplayer.autoCheckForUpdate=false" >> $INSTALL_E2DIR/etc/enigma2/settings
			echo "config.plugins.iptvplayer.deleteIcons=0" >> $INSTALL_E2DIR/etc/enigma2/settings
			echo "config.plugins.iptvplayer.downgradePossible=true" >> $INSTALL_E2DIR/etc/enigma2/settings
			echo "config.plugins.iptvplayer.dukpath=$INSTALL_E2DIR/lib/enigma2/python/Plugins/Extensions/$PKG_/bin/duk" >> $INSTALL_E2DIR/etc/enigma2/settings
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
	elif [ "$release" = "22.04" ]; then
		python2 -m compileall $INSTALL_E2DIR/lib/enigma2/python
	else
		python -m compileall $INSTALL_E2DIR/lib/enigma2/python
	fi

	# Force recompile new pyc files
	#if [ "$release" = "20.04" ]; then
	#	python2 -m compileall -f $INSTALL_E2DIR/lib/enigma2/python
	#elif [ "$release" = "22.04" ]; then
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
