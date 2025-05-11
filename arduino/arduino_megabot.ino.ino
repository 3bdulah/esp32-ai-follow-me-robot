char command = 'S';
char lastCommand = 'S';

const int in1 = 8;
const int in2 = 9;
const int in3 = 10;
const int in4 = 11;
const int ena = 5;
const int enb = 6;

// Ultrasonic pins
const int trigPin = A0;
const int echoPin = A1;

// LED pins
const int redLED = 4;
const int greenLED = 3;

void setup() {
  Serial.begin(9600);

  // Motor pins
  pinMode(in1, OUTPUT); pinMode(in2, OUTPUT);
  pinMode(in3, OUTPUT); pinMode(in4, OUTPUT);
  pinMode(ena, OUTPUT); pinMode(enb, OUTPUT);
  analogWrite(ena, 200);  // Half speed
  analogWrite(enb, 200);

  // Ultrasonic pins
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  // LED pins
  pinMode(redLED, OUTPUT);
  pinMode(greenLED, OUTPUT);
  updateLEDs();  // Set initial LED state
}

void loop() {
  float distance = measureDistance();

  // Obstacle detected
  if (distance > 0 && distance < 20) {
    stopMoving();
    delay(200);
    turnRight90();
    delay(500);
    stopMoving();
    delay(300);
  } else {
    // Receive command from ESP32
    if (Serial.available()) {
      char incoming = Serial.read();
      if (incoming == 'F' || incoming == 'B' || incoming == 'L' || incoming == 'R' || incoming == 'S') {
        command = incoming;
        if (command != lastCommand) {
          updateLEDs();
          lastCommand = command;
        }
      }
    }

    // Execute movement
    if (command == 'F') moveForward();
    else if (command == 'B') moveBackward();
    else if (command == 'L') moveLeft();
    else if (command == 'R') moveRight();
    else stopMoving();
  }
}

// === Movement functions ===
void moveForward() {
  digitalWrite(in1, LOW);  digitalWrite(in2, HIGH);  // Left forward
  digitalWrite(in3, HIGH); digitalWrite(in4, LOW);   // Right forward
}

void moveBackward() {
  digitalWrite(in1, HIGH); digitalWrite(in2, LOW);   // Left backward
  digitalWrite(in3, LOW);  digitalWrite(in4, HIGH);  // Right backward
}

void moveLeft() {
  digitalWrite(in1, LOW);  digitalWrite(in2, HIGH);  // Left forward
  digitalWrite(in3, LOW);  digitalWrite(in4, LOW);   // Right stop
}

void moveRight() {
  digitalWrite(in1, LOW);  digitalWrite(in2, LOW);   // Left stop
  digitalWrite(in3, HIGH); digitalWrite(in4, LOW);   // Right forward
}

void stopMoving() {
  digitalWrite(in1, LOW); digitalWrite(in2, LOW);
  digitalWrite(in3, LOW); digitalWrite(in4, LOW);
}

// === Turn 90° right ===
void turnRight90() {
  digitalWrite(in1, HIGH); digitalWrite(in2, LOW);
  digitalWrite(in3, HIGH); digitalWrite(in4, LOW);
}

// === Measure distance ===
float measureDistance() {
  digitalWrite(trigPin, LOW); delayMicroseconds(2);
  digitalWrite(trigPin, HIGH); delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long duration = pulseIn(echoPin, HIGH, 30000);  // Timeout 30ms
  if (duration == 0) return -1;  // No echo
  return duration * 0.034 / 2;
}

// === LED control ===
void updateLEDs() {
  if (command == 'S') {
    digitalWrite(greenLED, LOW);
    digitalWrite(redLED, HIGH);
  } else {
    digitalWrite(greenLED, HIGH);
    digitalWrite(redLED, LOW);
  }
}