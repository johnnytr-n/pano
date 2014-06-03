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
byte command = 0x00;
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
}

void loop(){
  if(Serial.available()){
    command = Serial.read(); 
    //Serial.print("character recieved: ");
    //Serial.println(command, HEX);   
    if((char)command == 0x4C){                 // CLOCK RIGHT
      Serial.println("command:\trotate right");
      pano->step(10, FORWARD, DOUBLE);
    }
    else if((char)command == 0x52){            // ANTICLOCK LEFT
      Serial.println("command:\trotate left");
      pano->step(10, BACKWARD, DOUBLE);
    }
    else{
      int interval = (int) command - 48; // ASCII values
      Serial.print("command:\t");
      Serial.print(interval);
      Serial.println(" intervals");
      for(int i = 0; i < interval; i++){
        Serial.print(i);
        pano->step(20, FORWARD, DOUBLE);
        delay(1000);    // delay 3 seconds
        Serial.print("X");
        delay(2000);
      }
      Serial.println("Z");                // signal end of serial stream
      Serial.println("Done with panorama");
    }
    command = -1;
  }
}
