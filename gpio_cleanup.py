import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
	
GPIO.setup(23, GPIO.OUT)
try:
	print "outputting to 23"
	while True:
		print "HIGH"
		GPIO.output(23, GPIO.HIGH)
		time.sleep(5)
		print "LOW"
		GPIO.output(23, GPIO.HIGH)
		time.sleep(5)
finally:
	GPIO.cleanup()
