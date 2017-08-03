proc=$(adb shell "ps | grep -i light.co.lightcamera")

#if  [[ $proc != *"camera"* ]]; then

echo "pocess $proc" 

if [ ${#"$proc"} -ge 1 ]; then
echo "not running"
fi
echo "App is runnigng"

#if ! (( $(adb shell "ps | grep -i light.co.lightcamera"))); then
#echo "Process does not exist"

#adb shell am start light.co.lightcamera/light.co.camera.CameraActivity
#fi