# Johnny Tran - ECE 118 - SP14
import time
import math
import smbus
import serial
import RPi.GPIO as GPIO
from Adafruit_CharLCDPlate import Adafruit_CharLCDPlate

# Params
default_start = 180			# default start position for angle
default_interval = 36 		# default interval angle
SHUTTER = 23				# shutter GPIO pin		
FOCUS = 24					# focus GPIO pin
shutter_stall = .2 			# time in seconds to keep GPIO pin on high
rotation = default_start	# default rotation set to default start position
shutter_sentinel = "X"		# sentinel value for shutter release
halt_sentinel = "Z"			# sentinel value to halt watching serial comm
str1 = "Pano Angle:\n"		
OP_SUBMIT = 'S'			# serial code to send for panoroma execution
OP_RIGHT = 'R'				# serial code to send for right rotation
OP_LEFT = 'L'				# serial code to send for left rotation
OP_JNT = '0'

# returns number of 36 degree intervals in user designated range
def calc_interval(user_deg):
	if 0<= user_deg < default_interval:
		return 1
	elif default_interval <= user_deg < 360-default_interval:
		return int(math.ceil(user_deg/default_interval))+1
	elif 360-default_interval <= user_deg:
		return 9
	else:
		err()
		return -1

#turns backlight red if there is an error
def err():
	GPIO.cleanup()			# reset GPIO pins
	lcd.backlight(lcd.RED)

# updates display with current rotation selection
def update_rotation(curr_rotation, diff):
	# keeps value of rotation in range
	new_rotation = curr_rotation + diff
	if curr_rotation == 360 and diff == 1.8:
		new_rotation = 0
	elif curr_rotation == 0 and diff == -1.8:
		new_rotation = 360

	if new_rotation < 0:
		new_rotation = 360

	if new_rotation != 360:
		new_rotation %= 360

	update_display(new_rotation)
	return new_rotation

# updates angle display
def update_display(message):
	display_str = str1 + str.format('{0:.1f}', message) + " degrees"
	lcd.clear()
	lcd.message(display_str)	

# calculates information to send to Arduino for panorama execution
def submit(rotation_var, op_code):
	instruction = 0;
	if op_code == OP_SUBMIT:
		instruction = str(calc_interval(rotation_var))	
	else:
		instruction = op_code
	print "Pan " + rotation_var " degrees, in " + str(instruction) + "intervals"
	uno_serial.write(instruction)
	
# use GPIO to release DSLR shutter
def release_shutter():
	GPIO.output(SHUTTER, GPIO.HIGH)	# set logic to high 
	time.sleep(shutter_stall)		# give DSLR time to register shutter
	GPIO.output(SHUTTER, GPIO.LOW)	# set logic to low

# focus/wake DSLR
def focus():
	GPIO.output(FOCUS, GPIO.HIGH)	# set logic to high
	time.sleep(shutter_stall)		# give DSLR time to register
	GPIO.output(FOCUS, GPIO.LOW)	# set logic to low

# poll serial communication for shutter release
def pano_shutter(submitted_rotation):
	uno_message = 0
	while True:
		uno_message = uno_serial.read(1)	# read 1 character from serial comm
		print uno_message					# print serial stream
		if uno_message == shutter_sentinel:	# signal to release shutter
			release_shutter()
		elif uno_message == halt_sentinel:	# signal to stop
			break	
	lcd.backlight(lcd.ON)
	for i in range(5,-1,-1):
		lcd.clear()
		lcd.message("Thanks for\nwaiting!       " + str(i))
		time.sleep(1)
		

##############################################################
# open serial communication through UART
uno_serial = serial.Serial('/dev/ttyAMA0', 9600, timeout=1)
uno_serial.open()

# initialize GPIO and setup output pins for DSLR communication
GPIO.setmode(GPIO.BCM)
GPIO.setup(SHUTTER, GPIO.OUT)
GPIO.setup(FOCUS, GPIO.OUT)
GPIO.output(SHUTTER, GPIO.LOW)
GPIO.output(FOCUS, GPIO.LOW)

# initialize LCD object and display splash screen
lcd = Adafruit_CharLCDPlate()
lcd.clear()
lcd.backlight(lcd.ON)
lcd.message("Welcome to Pano!\nECE 118 - Johnny")
focus()
btn = ((lcd.LEFT  , 1),
       (lcd.UP    , 1.8),
       (lcd.DOWN  , -1.8),
       (lcd.RIGHT , 2),
       (lcd.SELECT, 3))

time.sleep(2)

update_display(rotation)

try:
	while True:
		time.sleep(0.2) #sleep for 200ms to prevent key bouncing
		for b in btn:
			if lcd.buttonPressed(b[0]):	
				if b[0] == lcd.UP or b[0] == lcd.DOWN:
					rotation = update_rotation(rotation, b[1])
					print "pressed ", rotation
					break
				# user specified alignment and repositioning of motor shaft
				#rotate	motor over 10 steps left or right
				elif b[0] == lcd.LEFT:
					submit(0, OP_LEFT)
					break
				elif b[0] == lcd.RIGHT:
					submit(0, OP_RIGHT)	
					break
				# user submission to execute panorama
				elif b[0] == lcd.SELECT:	
					focus()						# wake camera and focus
					lcd.clear()
					lcd.backlight(lcd.VIOLET)
					lcd.message("Executing Pano!\n Please wait...")
					submit(rotation, OP_SUBMIT)	# submit pano intent
					pano_shutter(rotation)		# poll comm for shutter release
					rotation = default_start	# set to default
					update_display(rotation)
				break
except KeyboardInterrupt:				# exit on user interrupt
	print "\nYou have exited Pano"
except:									# err gracefully
	err()
finally:								# clean up and reset GPIO on exit
	GPIO.cleanup()
