#!/bin/bash

trap ReceiveCheckPointSignal SIGUSR2

function ReceiveCheckPointSignal() {
	TPID=$(pgrep test_sleep.sh)
	rm -rf dumped_images-*
	IMG_DIR="dumped_images-$(uuidgen)"
	mkdir ${IMG_DIR}
	criu dump --unprivileged -v4 -t ${TPID} -D $IMG_DIR -o criu.log #-j --evasive-devices #--leave-running
	#criu dump -v4 -t ${TPID} -D $IMG_DIR -o criu.log #-j --evasive-devices #--leave-running
    	tar -czvf checkpoint.tar.gz $IMG_DIR
	echo "Checkpoint!!" >> state_running.txt
	exit 85
}


if [ -s checkpoint.tar.gz ]; then
        tar -zxvf checkpoint.tar.gz
	IMG_DIR=$(echo dumped_images-*)
	criu restore --unprivileged -v4 -d -D $IMG_DIR
	#criu restore -v4 -d -D $IMG_DIR
fi

TPID=$(pgrep test_sleep.sh)
if [ -z $TPID ]; then
	echo "Can not find test_sleep.sh. Start script from begining"
	setsid ./test_sleep.sh </dev/null &> /dev/null &
	TPID=$!
else
	echo "Found test_sleep.sh: $TPID"
fi
while true
do
	echo "Monitoring ${TPID} procces"
	kill -s 0 ${TPID} 
	if [ $? -ne 0 ]; then
	   exit 0   
	fi
	if [[ -e state_running.txt && $(tail -n1 state_running.txt) == "10" ]]; then
		kill -SIGUSR2 $$
	fi
	sleep 1
done
