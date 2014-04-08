// Controlador de motores L298N
#include "L298N.h"

L298N::L298N(int e1, int m1, int e2, int m2)
{
  PIN_E1 = e1;
  PIN_M1 = m1;
  PIN_E2 = e2;
  PIN_M2 = m2;
}

void L298N::begin()
{
  pinMode(PIN_E1, OUTPUT);
  pinMode(PIN_M1, OUTPUT);
  pinMode(PIN_E2, OUTPUT);
  pinMode(PIN_M2, OUTPUT);
  analogWrite(PIN_E1, 0);
  digitalWrite(PIN_M1, FORWARD);
  analogWrite(PIN_E2, 0);
  digitalWrite(PIN_M2, FORWARD);
}

void L298N::setMotor(int motor, int direccion, int power)
{
  switch(motor)
  {
    case 1:
      digitalWrite(PIN_M1, direccion);
      analogWrite(PIN_E1, power);
      break;
    case 2:
      digitalWrite(PIN_M2, direccion);
      analogWrite(PIN_E2, power);
      break;
  }
}
