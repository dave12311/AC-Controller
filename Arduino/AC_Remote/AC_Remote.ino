void setup() {
  Serial.begin(9600);
  pinMode(2, INPUT);
}

#define length 400

int state = 0;
int count = 0;
int inputState;

long int us[length];
bool data[length];

void loop() {
  inputState = digitalRead(2);
  if(state == 0 && inputState == 0){
    state = 1;
  }
  if(state==1 && count < length){
    us[count] = micros();
    data[count] = inputState;
    count++;
  } else if(count == length){
    for(int i=0;i<length;i++){
      Serial.print(us[i]);
      Serial.print(",");
      Serial.print(data[i]);
      Serial.print("\n");
    }
    count = 0;
    state = 2;
  }
  delayMicroseconds(625);
}
