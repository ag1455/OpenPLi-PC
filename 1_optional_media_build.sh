#!/bin/bash

git clone https://github.com/crazycat69/media_build.git
cd media_build
# git checkout 8e48f8a1
./build
make install
cd ..
reboot # You need to restart PC.