# Johnny Tran - ECE 118
import time
import math
import smbus
import serial
import RPi.GPIO as GPIO
from Adafruit_CharLCDPlate import Adafruit_CharLCDPlate

# Params
default_start = 180
SHUTTER = 23
FOCUS = 24
shutter_stall = .2
rotation = default_start
str1 = "Pano Angle:\n"
OP_SUBMIT = 0x03
OP_RIGHT = 'R'
OP_LEFT = 'L'
OP_JNT = '0'

# sends data on to the I2C bus
def send(val):
	bus.write_byte(uno_addr, val)
	return -1

# receives data off to the I2C bus
def receive():
	num = bus.read_byte(uno_addr)
	return num

# returns number of 36 degree intervals in user designated range
def calc_interval(user_deg):
	if 0<= user_deg < 36:
		return 1
	elif 36 <= user_deg < 324:
		return int(math.ceil(user_deg/36))
OP_SUBMIT = 0x03
OP_RIGHT = 'R'
OP_LEFT = 'L'
OP_JNT = '0'

# sends data on to the I2C bus
def send(val):
	bus.write_byte(uno_addr, val)
	return -1

# receives data off to the I2C bus
def receive():
	num = bus.read_byte(uno_addr)
	return num

# returns number of 36 degree intervals in user designated range
def calc_interval(user_deg):
	if 0<= user_deg < 36:
		return 1
	elif 36 <= user_deg < 324:
		return int(math.ceil(user_deg/36))+1
	elif 324 <= user_deg:
		return 9
	else:
		err()
		return -1

#turns backlight red if there is an error
def err():
	GPIO.cleanup()
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

#
def update_display(message):
	display_str = str1 + str.format('{0:.1f}', message) + " degrees"
	lcd.clear()
	lcd.message(display_str)	

# creates an instruction to send to Arduino
def submit(rotation_var, op_code):
	instruction = 0;
	if op_code == OP_SUBMIT:
		instruction = str(calc_interval(rotation_var))	
	else:
		instruction = op_code
	#print "send instr ", bin(instruction)
	#print str(instruction)i
	print str(instruction)
	uno_serial.write(instruction)
	
# use GPIO to release camera shutter
def release_shutter():
	GPIO.output(SHUTTER, GPIO.HIGH)
	time.sleep(shutter_stall)
	GPIO.output(SHUTTER, GPIO.LOW)

#focus camera
def focus():
	GPIO.output(FOCUS, GPIO.HIGH)
	time.sleep(shutter_stall)
	GPIO.output(FOCUS, GPIO.LOW)

# displays pano text to user, waits on response from Arduino
def pano_display(submitted_rotation):
	uno_message = 0
	while True:
		uno_message = uno_serial.read(1)	# serial read 1 character
		print uno_message					# print serial stream
		if uno_message == "X":				# signal to release shutter
			release_shutter()
		elif uno_message == "Z":			# signal to stop watching line
			break	
	lcd.backlight(lcd.ON)
	for i in range(5,-1,-1):
		lcd.clear()
		lcd.message("Thanks for\nwaiting!       " + str(i))
		time.sleep(1)
		

##############################################################

uno_serial = serial.Serial('/dev/ttyAMA0', 9600, timeout=1)
uno_serial.open()

GPIO.setmode(GPIO.BCM)
GPIO.setup(SHUTTER, GPIO.OUT)
GPIO.setup(FOCUS, GPIO.OUT)
GPIO.output(SHUTTER, GPIO.LOW)
GPIO.output(FOCUS, GPIO.LOW)

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

#bus = smbus.SMBus(1)
uno_addr = 0x04			# I2C address of Arduino Uno R3
time.sleep(2)

update_display(rotation)

prev = -1
try:
	while True:
		time.sleep(0.2) #sleep for 200ms to prevent key bouncing
		for b in btn:
			if lcd.buttonPressed(b[0]):	
				if b[0] == lcd.UP or b[0] == lcd.DOWN:
					rotation = update_rotation(rotation, b[1])
					print "pressed ", rotation
					break
				elif b[0] == lcd.LEFT:
					submit(0, OP_LEFT)
					break
				elif b[0] == lcd.RIGHT:
					#alight and reposition motor shaft
					#rotate	motor over 10 steps left or right
					submit(0, OP_RIGHT)	
					break
				elif b[0] == lcd.SELECT:	
					#submit rotation and execute pano
					focus()
					lcd.clear()
					lcd.backlight(lcd.VIOLET)
					lcd.message("Executing Pano!\n Please wait...")
					submit(rotation, OP_SUBMIT)
					pano_display(rotation)
					rotation = default_start
					update_display(rotation)
				break
except KeyboardInterrupt:
	print "You have exited Pano"
except:
	err()
finally:
	GPIO.cleanup()
