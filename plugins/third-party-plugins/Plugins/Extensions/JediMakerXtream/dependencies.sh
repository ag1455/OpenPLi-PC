#!/bin/sh
pyv="$(python -V 2>&1)"
echo "$pyv"
echo "Checking Dependencies"
echo
if [ -d /etc/opkg ]; then
    echo "updating feeds"
    opkg update
    echo
    if [[ $pyv =~ "Python 3" ]]; then
        echo "checking python3-lzma"
        opkg install liblzma5
        echo
    else
        echo "checking python2-lzma"
        opkg install python-lzma
        echo
    fi
else
    echo "updating feeds"
    apt-get update
    echo
    if [[ $pyv =~ "Python 3" ]]; then
        echo "checking python3-lzma"
        apt-get -y install liblzma5
        echo
    else
        echo "checking python2-lzma"
        apt-get -y install python-lzma
        echo
    fi
fi
exit 0
