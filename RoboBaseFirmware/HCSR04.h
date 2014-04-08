// Sensor ultrasonico HC-SR04
#include <Arduino.h>

class HCSR04
{
  private:
    int PIN_TRIGGER;
    int PIN_ECHO;
    unsigned long distance;
  private:
    void fill(unsigned long);
  public:
    HCSR04(int trigger, int echo);
    void begin();
    unsigned int ping(unsigned int max_distance);
};

