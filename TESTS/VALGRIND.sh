#!/bin/sh

if [ ! -f /usr/bin/valgrind ]; then
	apt install valgrind
fi

cd ..
valgrind --leak-check=full --track-origins=yes --error-limit=no --log-file="./logfile.out" -v ./e2bin
#valgrind --tool=callgrind --log-file="./logfile.out" -v ./e2bin
#valgrind --tool=callgrind --log-file="./logfile.out" ./e2bin
#valgrind --tool=cachegrind --log-file="./logfile.out" -v ./e2bin
#valgrind --tool=helgrind --log-file="./logfile.out" -v ./e2bin
#valgrind --tool=massif --log-file="./logfile.out" -v ./e2bin

