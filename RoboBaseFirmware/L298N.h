// Controlador de motores L298N
#include <Arduino.h>

class L298N
{
  private:
    int PIN_E1;
    int PIN_M1;
    int PIN_E2;
    int PIN_M2;
  public:
    const int FORWARD  = LOW;
    const int BACKWARD = HIGH;
  public:
    L298N(int e1, int m1, int e2, int m2);
    void begin();
    void setMotor(int motor, int direccion, int power);
};

