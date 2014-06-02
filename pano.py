# Johnny Tran - ECE 118
import time
import smbus
import serial
from Adafruit_CharLCDPlate import Adafruit_CharLCDPlate

# Params
rotation = 180
str1 = "Pano Angle:\n"
OP_SUBMIT = 0x03
OP_RIGHT = 0x02
OP_LEFT = 0x01
OP_JNT = 0x00

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
		return (user_deg/36)+1
	elif 324 <= user_deg <= 360:
		return 9
	else:
		err()
		return -1

#turns backlight red if there is an error
def err():
	lcd.backlight(lcd.RED)

# updates display with current rotation selection
def update_rotation_display(curr_rotation, diff):
	# keeps value of rotation in range
	new_rotation = curr_rotation + diff
	if curr_rotation == 360 and diff == 10:
		new_rotation = 0
	elif curr_rotation == 0 and diff == -10:
		new_rotation = 360

	if new_rotation != 360:
		new_rotation %= 360

	display_str = str1 + str(new_rotation)
	lcd.clear()
	lcd.message(display_str)
	return new_rotation	

# creates a packet for part of the instruction
def create_packet(param):
	interval = calc_interval(param)
	rotate_var = param/10			#rotation is between 0-36, 37 values
	
	packet = interval<<6			#4 bits for interval
	packet = packet|rotate_var		#6 bits for rotation
	print bin(packet)
	return packet;

# creates an instruction to send to Arduino
def submit(rotation_var, op_code):
	instruction = 0;
	if op_code == OP_SUBMIT:
		packet = create_packet(rotation_var)
		instruction = op_code<<10
		instruction = instruction|packet
	else:
		instruction = op_code<<10
	print "send instr ", bin(instruction)
	uno_serial.write(str(instruction))
	
# displays pano text to user, waits on response from Arduino
def pano_display():
	lcd.clear()
	lcd.backlight(lcd.VIOLET)
	lcd.message("Executing Pano!\n Please wait...")
	time.sleep(5)
	uno_output = 0
	#while uno_output != 1:
	#	uno_output = receive()
	lcd.clear()
	lcd.backlight(lcd.ON)
	lcd.message("Done! Press any key\n to continue.")
	wait_for_user = 0
	while wait_for_user == 0:
		for b in btn:
			time.sleep(0.2)
			if lcd.buttonPressed(b[0]):	
				lcd.clear()	
				lcd.message(welcome_str)
				wait_for_user = 1

##############################################################

uno_serial = serial.Serial('/dev/ttyAMA0', 9600, timeout=1)
uno_serial.open()

lcd = Adafruit_CharLCDPlate()
lcd.clear()
lcd.backlight(lcd.ON)
lcd.message("Welcome to Pano!\nECE 118 - Johnny")
btn = ((lcd.LEFT  , 1),
       (lcd.UP    , 10),
       (lcd.DOWN  , -10),
       (lcd.RIGHT , 2),
       (lcd.SELECT, 3))

bus = smbus.SMBus(1)
uno_addr = 0x04			# I2C address of Arduino Uno R3
time.sleep(2)

welcome_str = str1 + str(rotation)

lcd.clear()
lcd.message(welcome_str)	
prev = -1
while True:
	time.sleep(0.2) #sleep for 200ms to prevent key bouncing
	for b in btn:
		if lcd.buttonPressed(b[0]):	
			if b[0] == lcd.UP or b[0] == lcd.DOWN:
				rotation = update_rotation_display(rotation, b[1])
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
				submit(rotation, OP_SUBMIT)
				pano_display()
				rotation = 180
				break
						

	#user_in = input("Enter 1- 9: ")
	#if not user_in:
	#	continue

	#send(user_in)
	#lcd.message(user_in)
	#print "RPI: sent ", user_in
	#time.sleep(1)


	#uno_out = receive()
	#print "Arduino: received ", user_in


