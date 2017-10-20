import time, sys
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.FT232H as FT232H
import usb # to conform, the USB device that is will be used

def check_door():
	try:
		busses = usb.busses()
		for bus in busses:
			devices = bus.devices
			for dev in devices:
				vendorid = dev.idVendor
				productid = dev.idProduct
		
		if vendorid == 1027 and productid == 24596:			
			fth232=FT232H.FT232H()
			fth232.setup(7, GPIO.IN)
			fth232.setup(8, GPIO.OUT)
			level = fth232.input(7)
			
			if level ==GPIO.LOW:
				fth232.output(8, GPIO.HIGH)
				status = "Door is closed"

			elif level == GPIO.HIGH:
				fth232.output(8, GPIO.LOW)
				status = "Door is open"

			else:
				while True:
					fth232.output(8, GPIO.HIGH)
					time.sleep(1)
					fth232.output(8, GPIO.LOW)
					time.sleep(1)
					status = "unknown"
			return status
		
	except:
		#raise
		sys.exit("Not proper device was found. Exiting...")	

if __name__ == "__main__":
	print check_door()


