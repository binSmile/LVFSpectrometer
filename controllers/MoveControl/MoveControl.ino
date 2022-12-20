const uint8_t pin_ENA = 4;                // Вывод Arduino подключённый к входу драйвера ENA+.
const uint8_t pin_DIR = 3;                // Вывод Arduino подключённый к входу драйвера DIR+.
const uint8_t pin_PUL = 2;                // Вывод Arduino подключённый к входу драйвера PUL+.
// Вывод GND Arduino соединён с входами драйвера ENA-, DIR-, PUL-.
#include <GyverStepper2.h>
//https://alexgyver.ru/gyverstepper/
//GStepper<STEPPER2WIRE> stepper(1, pin_PUL, pin_DIR, pin_ENA);
GStepper2<STEPPER2WIRE> stepper(1, 2, 3, 4);

#include <string.h>
char unitID_in[10];
char command_in[10];
char data_in[100];


void setup() {                            //
  //  pinMode( pin_ENA, OUTPUT );          // Конфигурируем вывод Arduino как выход.
  //  pinMode( pin_DIR, OUTPUT );          // Конфигурируем вывод Arduino как выход.
  //  pinMode( pin_PUL, OUTPUT );          // Конфигурируем вывод Arduino как выход.
  Serial.begin(2000000);
  pinMode(13, OUTPUT); // Sets pin 13 as OUTPUT.
  Serial.flush();

  // установка макс. скорости в шагах/сек
  stepper.setMaxSpeed(400);
  // установка ускорения в шагах/сек/сек
  stepper.setAcceleration(500);

  // отключать мотор при достижении цели
  stepper.autoPower(true);
  // положительные смещения - от мотора
  stepper.reverse(false);


}                                         //
//



void loop() {
  stepper.tick();

    // график положения
    static uint32_t tmr2;
    if (millis() - tmr2 > 20) {
      tmr2 = millis();
      Serial.println(stepper.getCurrent());
    }



  int i = 0;
  char buffer[100];

  //если есть данные - читаем
  if (Serial.available()) {
    delay(100);

    //загоняем прочитанное в буфер
    while ( Serial.available() && i < 99) {
      buffer[i++] = Serial.read();
    }
    //закрываем массив
    buffer[i++] = '\0';
  }

  //если буфер наполнен
  if (i > 0) {

    //разбераем его на части отделенные запятой
    sscanf(buffer, "%[^','],%[^','],%s", &unitID_in, &command_in, &data_in);

  }

  //Исполнительная часть
  //Проверяем какому устройству пришли данные

  //тестовое устройство 001
  if ((String)unitID_in == "001") { //test serial read
    Serial.print("001,arduino recive: unit ");
    Serial.print(unitID_in);
    Serial.print("\n");
    Serial.print("command: ");
    Serial.print(command_in);
    Serial.print("\n");
    Serial.print("data: ");
    Serial.print(data_in);
    Serial.print("\n");
    unitID_in[0] = '\0';
    command_in[0] = '\0';
  }

  //пример выполнения команды устройством 002
  if ((String)unitID_in == "002") {
    if ((String)command_in == "brake") {
      stepper.brake();
    } else {
      if ((String)command_in == "move") {
        long  insteps = atol(data_in);
        stepper.setTarget(insteps, RELATIVE);
      }
      if ((String)command_in == "setspeed") {
        float news = atof(data_in);
        stepper.setSpeed(news);
      }
      if ((String)command_in == "setaccel") {
        float accel = atof(data_in);
        stepper.setAcceleration(accel);
      }
      if ((String)command_in == "reset") {
        stepper.reset();
      }
      if ((String)command_in == "ready") {
        if (stepper.tick()) {
          Serial.println("m");
        } else {
          Serial.println("r");
        }
      }
      if ((String)command_in == "getStatus") {
        Serial.println(stepper.getStatus());
      }
      if ((String)command_in == "Current") {
        Serial.println(stepper.getCurrent());
      }
    }


    // Serial.print("002,stepper recive: unit ");
    // Serial.print(unitID_in);
    // Serial.print(" command ");
    // Serial.print(command_in);
    // Serial.print("\n");
    unitID_in[0] = '\0';
    command_in[0] = '\0';
  }

  //пример выполнения команды устройством 013
  if ((String)unitID_in == "013") {

    if ((String)command_in == "on") {
      digitalWrite(13, HIGH);
    }
    if ((String)command_in == "off") {
      digitalWrite(13, LOW);
    }

    Serial.print("001,arduino recive: unit ");
    Serial.print(unitID_in);
    Serial.print(" command ");
    Serial.print(command_in);
    Serial.print("\n");
    unitID_in[0] = '\0';
    command_in[0] = '\0';
  }

}
