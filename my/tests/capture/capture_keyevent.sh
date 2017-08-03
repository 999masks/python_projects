#!/bin/bash
echo "capture keyevent"

# below code to run camera daemon if it is not runing

proc=$(adb shell "ps | grep -i light.co.lightcamera")

adb shell input tap 1000 600
sleep 1	
adb shell input keyevent 27
