#include <Servo2.h>

Servo servo1;
Servo servo2;
Servo servo3;

int pos = 170;
int pos3 = 20;
int E1 = 8;
int M1 = 12;
int E2 =11;
int M2 = 13;
int value;

void setup() {
  Serial.begin(9600);
  pinMode(M1, OUTPUT);
  pinMode(M2, OUTPUT);
  
  servo1.attach(5);
  servo2.attach(6);
  servo3.attach(7);
  servo1.write(pos);servo2.write(180 - pos);servo3.write(pos3);

}


void loop() {
  if (Serial.available() > 0) {
    int data = Serial.read()- '0';
    switch (data){
      
      case 1:
      digitalWrite(M1,HIGH);
      digitalWrite(M2, HIGH);
      analogWrite(E1, 130);
      analogWrite(E2, 130);
      delay(200);
      analogWrite(E1, 0);
      analogWrite(E2, 0);
      delay(200);
      break;
      
      case 2:
      digitalWrite(M1,LOW);
      digitalWrite(M2, LOW);
      analogWrite(E1, 130);
      analogWrite(E2, 130);
      delay(200);
      analogWrite(E1, 0);
      analogWrite(E2, 0);
      delay(200);
      break;
      
      case 3:
      digitalWrite(M1,HIGH);
      analogWrite(E1, 130);
      delay(200);
      analogWrite(E1, 0);
      delay(400);
      break;
      
      case 4:
      digitalWrite(M2,HIGH);
      analogWrite(E2, 140);
      delay(200);
      analogWrite(E2, 0);
      delay(400);
      break;
      
      case 5:
      digitalWrite(M1,HIGH);
      digitalWrite(M2, LOW);
      analogWrite(E1, 130);
      analogWrite(E2, 130);
      delay(100);
      analogWrite(E1, 0);
      analogWrite(E2, 0);
      delay(400);
      break;
      
      case 6:
      servo1.write(pos);servo2.write(180 - pos);servo3.write(pos3);
      for (pos = 170; pos > 70; pos -= 1) { // goes from 0 degrees to 180 degrees
        // in steps of 1 degree
        servo2.write(180 - pos);
        servo1.write(pos); 
      // tell servo to go to position in variable 'pos'
        delay(35);                       // waits 15 ms for the servo to reach the position
      }
      for (pos3 = 20; pos3 < 45; pos3 += 1) { // goes from 180 degrees to 0 degrees
        servo3.write(pos3);              // tell servo to go to position in variable 'pos'
        delay(35);                       // waits 15 ms for the servo to reach the position
      }
      break;

      case 7:
      for (pos3 = 45; pos3 > 20; pos3 -= 1) { // goes from 180 degrees to 0 degrees
        servo3.write(pos3);              // tell servo to go to position in variable 'pos'
        delay(35);                       // waits 15 ms for the servo to reach the position
      }
      
      for (pos = 70; pos < 170; pos += 1) { // goes from 0 degrees to 180 degrees
        // in steps of 1 degree
        servo1.write(pos);
        servo2.write(180 - pos); // tell servo to go to position in variable 'pos'
        delay(15);                       // waits 15 ms for the servo to reach the position
      }
      break;
      
      default:
      break;
    }
    Serial.print("OK");
  }
}
