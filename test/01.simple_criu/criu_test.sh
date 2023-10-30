#!/bin/bash

trap ReceiveCheckPointSignal SIGUSR2

function ReceiveCheckPointSignal() {
	rm -rf dumped_images-*
	IMG_DIR="dumped_images-$(uuidgen)"
	mkdir ${IMG_DIR}
	/usr/local/sbin/criu dump --unprivileged -v4 -t ${TPID} -D $IMG_DIR -o criu.log #-j #--evasive-devices #--leave-running
    	tar -czvf checkpoint.tar.gz $IMG_DIR
	echo ${TPID} >> ${IMG_DIR}/tpid
	echo "Checkpoint!!" >> state_running.txt
	echo "Exit 85" >> state_running.txt
	exit 85
}


if [ -s checkpoint.tar.gz ]; then
        tar -zxvf checkpoint.tar.gz
	IMG_DIR=$(echo dumped_images-*)
	/usr/local/sbin/criu restore --unprivileged -v4 -d -D $IMG_DIR #-j
	TPID=$(cat $IMG_DIR/tpid)
	if [ $? -ne 0 ]; then
		kill -9 ${TPID}
		exit 85
	fi
else
	echo "Can not find test_sleep.sh. Start script from begining"
	setsid ./test_sleep.sh </dev/null &> /dev/null &
	TPID=$!
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
