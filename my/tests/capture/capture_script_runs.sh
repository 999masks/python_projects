#!/bin/sh
echo "I will run this command:$0, number of captures:$1, initial delay: $2 and pause:$3"

iteration=$1
start_delay=$2
capture_pause=$3
capture_comm="./lcc -m 0 -s 0 -f 1 3E F8 01 11 21 00 -e 40000000 -g 2.0 -R 4160,3120"
focus="./lcc -m 0 -s 0 -f 0 01 00 00 1780 1236 680 680"


echo "program will start in $start_delay sec"
sleep $start_delay

for i in $(seq 1 $iteration)
do


  echo "Doing capture number:" $i
  cd /data/; $capture_comm

  if [ $i -lt $iteration ]; then
        echo "waiting for next capture for $capture_pause seconds"
        sleep $capture_pause
        fi
done