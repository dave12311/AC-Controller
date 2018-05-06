#include <IRremote.h>

IRsend irsend;

void setup() {
}

void loop() {
  irsend.sendNEC(0xC1600000,32);
  irsend.sendNEC(0xFFFFFFFF, 32);
  irsend.sendNEC(0xFFFFFFFF, 32);
  delay(3000);
}
