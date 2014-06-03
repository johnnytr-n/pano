/* Johnny Tran - ECE 118
 * pano_arduino
 */
 
// Libraries for Motor Shield
#include <Wire.h>
#include <SoftwareSerial.h>
#include <Adafruit_MotorShield.h>
#include "utility/Adafruit_PWMServoDriver.h"

#define UNO_ADDR 0x04
// Creates motor object wi th default I2C addr, 0x60?
Adafruit_MotorShield uno_shield = Adafruit_MotorShield(); 

// Initialize Stepper obj with 200 step resolution (1.8 deg)
Adafruit_StepperMotor *pano = uno_shield.getStepper(200, 2);

//SoftwareSerial rpi_serial(2,3);
byte number = 0x00;
int rotate = 0;
//int data[2]; // d[0] is interval, d[1] is rotation

void setup(){
  //initialize shield. default param  1.6KHz PWM
  Serial.begin(9600); //9600
  
  Serial.println("waiting to establish serial connection");
  while(!Serial){
  }
  Serial.println("Connected");
  Serial.println("Setting up MotorShield");
  // Initialize MotorShield and StepperMotor objects
  uno_shield.begin();      // default freq 1.6KHz
  pano->setSpeed(6);       // 6 RPM, 1 rev per 10 seconds
  /*
  Wire.begin(UNO_ADDR);  // initialize device as slave on addr 0x60
  Wire.onReceive(receive);
  Wire.onRequest(send);
  */
  /*
  rpi_serial.begin(9600);
  Serial.println("setup complete");
  */
}

void loop(){
  if(Serial.available()){
    number = Serial.read(); 
    Serial.print("character recieved: ");
    Serial.println(number, HEX);   
    if((char)number == 0x4C){                 // CLOCK RIGHT
      Serial.println("rotate right");
      pano->step(10, FORWARD, DOUBLE);
    }
    else if((char)number == 0x52){            // ANTICLOCK LEFT
      Serial.println("rotate left");
      pano->step(10, BACKWARD, DOUBLE);
    }
    else{
      int interval = number - 48; // ASCII values
      Serial.print("submitting intervals: ");
      Serial.println(interval);
      for(int i = 0; i < interval; i++){
        pano->step(20, FORWARD, DOUBLE);
        delay(3000);    // delay 3 seconds
      }
      
    }
    number = -1;
  }
}
  /*
  if(rpi_serial.available()){
      Serial.write(rpi_serial.read());
   }
   if(Serial.available()){
      rpi_serial.write(Serial.read()); 
   }
     
   */  
  /*
  rotate += 20;
  rotate = rotate%200;
  Serial.print("rotating: ");
  Serial.println(rotate);
  pano->step(rotate, FORWARD, DOUBLE);
  pano->step(20, BACKWARD, SINGLE);
  */

/*
void readPacket(int packet, int *data){
  int mask = 0x3F;
  data[0] = packet>>6;  //interval
  data[1] = packet & mask;  //rotation
}
*/
/*
void receive(int var){
  while(Wire.available()){
    number = Wire.read();
    //int rotate = number;
    Serial.print("data received: ");
    Serial.println(number);    
    //pano->step(rotate, FORWARD, DOUBLE);
  }
}

void send(){
 Wire.write(number); 
}
*/




