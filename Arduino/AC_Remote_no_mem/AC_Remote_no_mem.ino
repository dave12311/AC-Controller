void setup() {
  Serial.begin(19200);
  pinMode(2, INPUT);
}

#define length 2400

int state = 0;
int count = 0;
int inputState;
bool data[length];

void loop() {
  inputState = digitalRead(2);
  if(state == 0 && inputState == 0){
    Serial.println(micros());
    state = 1;
  }
  if(state==1 && count < length){
    data[count] = inputState;
    count++;
  } else if(count == length){
    for(int i = 0;i<length;i++){
      Serial.println(data[i]);
    }
    Serial.println(micros());
    count = 0;
    state = 2;
  }
  delayMicroseconds(100);
}
