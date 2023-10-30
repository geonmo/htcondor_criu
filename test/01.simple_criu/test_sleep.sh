#!/bin/bash
count=0
ls -l $PWD
while :; 
do
	echo $count  | tee -a state_running.txt
	count=$((count+1))
	sleep 2
	if [ $count -ge 20 ];then
		echo "job is finished" > finish.txt
		exit 0
	fi
done

