int mestime = 10; // ms
long maxValue = 10800; // Hz
int noise = 800; // Hz

#include <Adafruit_MCP23X17.h>
#define BCMR D5
#define BCQ1 0
#define BCQ2 1
#define BCQ3 2
#define BCQ4 3
#define BCQ5 4
#define BCQ6 5
#define BCQ7 6
#define BCQ8 7
#define BCQ9 8
#define BCQ10 9
#define BCQ11 10
#define BCQ12 11

#define BCQ13 12
#define BCQ14 13
#define BCQ15 14
#define BCQ16 15
float outValue = 0;

Adafruit_MCP23X17 mcp;
#include <Wire.h>
#include <Adafruit_MCP4725.h>
Adafruit_MCP4725 dac;

// Set this value to 9, 8, 7, 6 or 5 to adjust the resolution
#define DAC_RESOLUTION    (12)

#include <string.h>
char unitID_in[10];
char command_in[10];
char data_in[100];

void setup() {
  Serial.begin(115200);
    Serial.flush();
  //while (!Serial);
  //  Serial.println("MCP23017  Button Test!");

  // uncomment appropriate mcp.begin
  if (!mcp.begin_I2C()) {
    Serial.println("Error.");
    while (1);
  }
  //  mcp.begin(0x20);

  // configure pin for port extender
  mcp.pinMode(BCQ1, INPUT);
  mcp.pinMode(BCQ2, INPUT);
  mcp.pinMode(BCQ3, INPUT);
  mcp.pinMode(BCQ4, INPUT);
  mcp.pinMode(BCQ5, INPUT);
  mcp.pinMode(BCQ6, INPUT);
  mcp.pinMode(BCQ7, INPUT);
  mcp.pinMode(BCQ8, INPUT);
  mcp.pinMode(BCQ9, INPUT);
  mcp.pinMode(BCQ10, INPUT);
  mcp.pinMode(BCQ11, INPUT);
  mcp.pinMode(BCQ12, INPUT);

  mcp.pinMode(BCQ13, INPUT);
  mcp.pinMode(BCQ14, INPUT);
  mcp.pinMode(BCQ15, INPUT);
  mcp.pinMode(BCQ16, INPUT);
  pinMode(BCMR, OUTPUT);
  dac.begin(0x60);
  digitalWrite(BCMR, LOW);
  digitalWrite(BCMR, HIGH);
  digitalWrite(BCMR, LOW);
  
}

void loop() {
  
static uint32_t tmr2;
if (millis() - tmr2 > mestime) {
  tmr2 = millis();

  //    uint8_t PA = mcp.readGPIO(0);
  uint16_t PAB = mcp.readGPIO();
  unsigned int value = PAB & 0b00001111111111111;
  //    unsigned int value = 0b00001111111111111;
  Serial.println(PAB, DEC);
  digitalWrite(BCMR, HIGH);
  digitalWrite(BCMR, LOW);


  //    int qState[] = {
  //      mcp.digitalRead(BCQ12), mcp.digitalRead(BCQ11), mcp.digitalRead(BCQ10), mcp.digitalRead(BCQ9), mcp.digitalRead(BCQ8), mcp.digitalRead(BCQ7), mcp.digitalRead(BCQ6), mcp.digitalRead(BCQ5), mcp.digitalRead(BCQ4), mcp.digitalRead(BCQ3), mcp.digitalRead(BCQ2), mcp.digitalRead(BCQ1)
  //    };
  //    unsigned int value = 0;
  //    for (byte i = 0; i < 12; i++)
  //    {
  //      value *= 2;
  //      value += qState[i] ;
  //    }
  //    value = value / 2;
  unsigned long freq = value * 1e3 / mestime;
  //Serial.println(value, DEC); // OUTPUT TRUE

  //Serial.println(freq, DEC);
  if (freq < noise) {
    freq = noise;
    outValue = 0;
  }
  else {
    outValue = (freq - noise);
    outValue = (outValue / maxValue) * (4095);
    outValue = int(outValue);
    if (outValue > 4095) {
      outValue = 4095;
    }
  }
  outValue = (freq - noise);
  outValue = (outValue / maxValue) * (4095);
  outValue = int(outValue);
  if (outValue > 4095) {
    outValue = 4095;
  }


  dac.setVoltage(outValue, false);
  //    outValue = 0;
  //    value = 0;

}

}
