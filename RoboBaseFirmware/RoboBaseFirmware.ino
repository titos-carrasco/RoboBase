#include "L298N.h"
#include "HCSR04.h"
#include <SoftwareSerial.h>

// inicializa componentes
L298N motors = L298N(3, 2, 5, 4);  // Controlador de Motores
HCSR04 ping  = HCSR04(7, 8);       // Sensor ultrasonico
SoftwareSerial serial(10, 11);     // Modulo Bluetooth

// Comando
const int MOTORS        = 0x01;    // Control de los motores
const int PING          = 0x02;    // Ping
const int BEEP          = 0x03;    // Beep
const int INFO          = 0x04;   // Version

const int PACKET_LENGTH = 8;       // Tamaño comando
byte packet[PACKET_LENGTH];        // Comando recibido

// Varios
const int LED         = 13;        // Led para monitorear procesamiento 
const int BUZZER      = 9;         // Para emitir tonos
const char *INFO_TEXT = "RoboBase Arduino V1.0";

void setup()
{
  motors.begin();
  ping.begin();
  serial.begin(9600);

  pinMode(LED, OUTPUT);
  pinMode(BUZZER, OUTPUT);
}

void loop()
{
  if(!getPacket())
  {
    return;
  }
 
  digitalWrite(LED, HIGH);
  switch(packet[0])
  {
    case MOTORS:
      {
        if(packet[1]==0)
          motors.setMotor(1, motors.BACKWARD, packet[2]);
        else
          motors.setMotor(1, motors.FORWARD, packet[2]);
        if(packet[3]==0)
          motors.setMotor(2, motors.BACKWARD, packet[4]);
        else
          motors.setMotor(2, motors.FORWARD, packet[4]);
      }
      break;
    case PING:
      {
        unsigned int max_distance = packet[1]*256 + packet[2];
        unsigned int d = ping.ping(max_distance);
        serial.write( (d>>8) & 0xFF);
        serial.write(d & 0xFF);
      }
      break;
    case BEEP:
      {
        unsigned long frec = packet[1]*256 + packet[2]; 
        unsigned long duracion = packet[3]*256 + packet[4];
        unsigned long cycles = frec * (duracion/1000.0);
        unsigned long us = (1000000.0/frec)/2.0;
        for(unsigned long i=0; i<cycles; i++)
        {
          digitalWrite(BUZZER, HIGH);
          delayMicroseconds(us);
          digitalWrite(BUZZER, LOW);
          delayMicroseconds(us);
        }
      }
      break;
    case INFO:
      {
        serial.write(INFO_TEXT);
      }
      break;
  }
  digitalWrite(LED, LOW);
}

 boolean getPacket()
 {
  
   for(int i=0; i<PACKET_LENGTH; i++)
   {
     unsigned long t = millis();
     while(!serial.available())
     {
       if(i==0 || (millis() - t)>500L)
       {
         return false;
       }
     }
     int c= serial.read();
     packet[i]=c;
   }
 
   serial.write(packet, PACKET_LENGTH);
   return true;
 }
 
