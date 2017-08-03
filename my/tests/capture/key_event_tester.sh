#!/bin/bash
echo "Testing input keyevent"
#keyevents:
# 26 screen off
# 27 capture
 

adb shell am start light.co.lightcamera/light.co.camera.CameraActivity
sleep 1


for i in $(seq 8 50)
do
	echo "This is command number $i"
	adb shell input keyevent $i
	sleep 1
done