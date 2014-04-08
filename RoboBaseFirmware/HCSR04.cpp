// Sensor ultrasonico HC-SR04
#include "HCSR04.h"

HCSR04::HCSR04(int trigger, int echo)
{
  PIN_TRIGGER = trigger;
  PIN_ECHO = echo;
}

void HCSR04::begin()
{
  pinMode(PIN_TRIGGER,OUTPUT);
  pinMode(PIN_ECHO, INPUT);
  digitalWrite(PIN_TRIGGER,LOW);
  delay(20);
}

unsigned int HCSR04::ping(unsigned int max_distance)
{
  unsigned long t0 = 0;
  unsigned long t  = 0;
  unsigned long timeout = 58L * max_distance;

  t0 = micros();

  digitalWrite(PIN_TRIGGER, HIGH);
  delayMicroseconds(10);
  digitalWrite(PIN_TRIGGER, LOW);
  delayMicroseconds(10);

  t = micros();
  while(digitalRead(PIN_ECHO)==LOW)
  {
    if((micros() - t)>500L)
    {
      fill(t0);
      return 0;
    }
  }

  t = micros();
  while(digitalRead(PIN_ECHO)==HIGH)
  {
    if((micros() - t)>timeout)
    {
      fill(t0);
      return 0;
    }
  }

  // dos decimales. dividir por 100.0 al recibir
  unsigned int distance = ((micros() - t)*100L)/58;
  fill(t0);
  return distance;
}

void HCSR04::fill(unsigned long t0)
{
  // se sugiere delay de 60ms entre invocacion: t0 es el inicio de la operacion
  // delay((60 -(micros()-t0)/1000));
}

