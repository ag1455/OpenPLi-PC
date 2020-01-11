#!/bin/sh

date +"%d. %B %Y - %H:%M:%S"
name=$1
dest=$2
descr=`cat $name |sed -n "/DESCRIPTION/{s/DESCRIPTION=//;p}"`
url=`cat $name |sed -n "/URL/{s/URL=//;p}"`
ausgabe='tee -a /etc/enigma2/piconload'


echo "Loading picons $descr"
echo "Found url, downloading $url"
echo "wait..."
rm -f /tmp/picondata.tar.gz
wget -q $url -O /tmp/picondata.tar.gz
if [ $? = 1 ]; then
	echo " "
	echo "Sorry, the Picon file is not available!"
	echo " "
	echo "Please try later!"
	echo " "
	echo "=============================================="
	echo " "
	exit 1
fi
echo "ok"
echo "Picon file was loaded successfully!!!"
if test -d $d; then
	echo "extracting..."
	cd $dest
	tar -xzf /tmp/picondata.tar.gz
	echo "Picons extracted to $dest"
	rm -f /tmp/picondata.tar.gz
	chmod 755 /usr/local/e2/share/enigma2/picon
	chmod 755 /usr/local/e2/share/enigma2/piconSat
	chmod 755 /usr/local/e2/share/enigma2/piconProv
	chmod 644 /usr/local/e2/share/enigma2/picon/*
	chmod 644 /usr/local/e2/share/enigma2/piconSat/*
	chmod 644 /usr/local/e2/share/enigma2/piconProv/*
	rm -f /usr/local/e2/share/enigma2/picon/Thumbs.db
	rm -f /usr/local/e2/share/enigma2/piconSat/Thumbs.db
	rm -f /usr/local/e2/share/enigma2/piconProv/Thumbs.db
	echo " "
  if [ -f $name ]; then
        echo -e 'Picon' `cat $name |sed -n "/DESCRIPTION/{s/DESCRIPTION=//;p}"` $Linie  | $ausgabe
        echo -e 'Download ' `date +"%d. %B %Y - %H:%M:%S"` '\n'$Linie  | $ausgabe
	echo "Enigma2 needs a restart to load the Picon data!"
	echo " "
	echo "=============================================="
	echo " "
	echo "Enjoy -:) "
	exit 0
  fi
fi
