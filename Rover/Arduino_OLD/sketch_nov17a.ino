

//////////////////////////////////////////////////
//  LIBRARIES AND CONFIGURATION //
//////////////////////////////////////////////////
#pragma region LIBRARIES AND CONFIG
// USEFUL TOGGLES
bool useSerial = true; //enables serial output for debugging, set to false to disable serial output

//////////////////////////////////////////////////////////////////////////////////////////////////////////
// LED CONFIG
#pragma region LED config
#include <Adafruit_NeoPixel.h>

#define LED_COUNT 8  // Number of LEDs on the bar
#define LED_PIN 11   // LEDs on pin 11, can be changed to other digital pins
// Declare our NeoPixel strip object:
Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);  // Initializes LED object
unsigned long pattern_interval = 25;                                // Time between steps in the pattern (in milliseconds)
unsigned long lastUpdate = 0;                                       // Tracker for millis() when last update occurred
#pragma endregion LED config

//////////////////////////////////////////////////////////////////////////////////////////////////////////
// HCSR04 DISTANCE SENSOR CONFIG
#pragma region Distance Sensor config
#include <NewPing.h>

#define TRIGGER_PIN 10   // Arduino pin tied to trigger pin on the ultrasonic sensor (HCSR04).
#define ECHO_PIN 9       // Arduino pin tied to echo pin on the ultrasonic sensor.
#define MAX_DISTANCE 30  // Max distance in centimeters that the ultrasonic sensor will look for
// max dist can be increased but further distances can take longer to read which could disrupt balancing

NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE);  // NewPing setup of pins and maximum distance.

bool inRange = false;
int distance = 0;
#pragma endregion Distance Sensor config

//////////////////////////////////////////////////////////////////////////////////////////////////////////
// STATE TRACKING
#pragma region State Machine


enum LedState { RAINBOW,
                BLUSH };
LedState led_state = RAINBOW;

int cmd_count = 0;  // How many loops since last command. Used to track when to interpolate
#pragma endregion State Machine


//////////////////////////////////////////////////////////////////////////////////////////////////////////
//DRV8835 MOTOR DRIVER CONFIG
#pragma region Motor Driver config
#define AENBL 5  //Assigns motor driver pins to the corresponding arduino pins
#define APHASE 7
#define BENBL 6   // "enable" pins are analog (0-255)for speed control
#define BPHASE 8  // "phase" pins are digital (0 or 1) for direction control
#define MODE A3   // "mode" pin can change the function of the DRV8835 and unlocks some cool features. Not used here, but check out the datasheet to learn more!

#pragma endregion Motor Driver config

//////////////////////////////////////////////////////////////////////////////////////////////////////////
// MPU6500 CONFIG
#pragma region IMU config
#include <I2Cdev.h>
#include <MPU6050_6Axis_MotionApps20.h> // although this library is for the MPU6050, that chip is out of production
#include <Wire.h> // instead we're using the MPU6500, which is a newer variant

bool blinkState = false;


#pragma endregion IMU config
#pragma endregion LIBRARIES AND CONFIG

//////////////////////////////////////////////////
//  S E T U P //
//////////////////////////////////////////////////
#pragma region SETUP
int start_time = 0;
void setup() {

  Serial.println("Hi peter Setup");
  init_i2c();
  init_serial();
  init_pins();
  start_time = millis();

}
#pragma endregion SETUP

//////////////////////////////////////////////////
//  L O O P //
//////////////////////////////////////////////////
#pragma region LOOP
void loop() {
  
  int seconds = (millis() - start_time) / 1000;
  int phase = (seconds/2) % 4;
  int left_speed, right_speed;
  if (phase == 0) {
    activateMotors(0, 255);
  } else if (phase == 1) {
    activateMotors(255, 255);
  } else if (phase == 2) {
    activateMotors(255, 0);
  } else {
    activateMotors(0, 0);
  }

  handle_sensors();

  cmd_count++;
  Serial.println("Bye peter");
}
#pragma endregion LOOP

//////////////////////////////////////////////////
//  FUNCTIONS  //
//////////////////////////////////////////////////
#pragma region FUNCTIONS



/********** LOOP HELPERS **********/
#pragma region Loop Helpers

/**
 * @brief Handles updates to IR, Distance, LEDs, and Serial printing, with interpolation
 * 
*/
void handle_sensors() {

  if ((cmd_count % 100) == 0) {
    checkDistance();
  }

  if (millis() - lastUpdate > pattern_interval) {
    if (inRange){
      led_state = BLUSH;
    }else{
      led_state = RAINBOW;
    }
    updateLEDs();
  }

  if (cmd_count > 500) {  // a slower loop (once every 500 loops this runs) to let the MPU run faster without being delayed by other stuff
    if (useSerial) Serial.println("500 loop");
    cmd_count = 0;
  }
}
#pragma endregion Loop helpers

/***** DRIVE FUNCTIONS *****/
#pragma region Driving

/**
 * @brief compensates for motor deadband, factors in turn value to output, and handles output of motor speeds to the motor driver with appropriate pin settings 
*/
void activateMotors(int speed_left, int speed_right) {
  bool dir_right = (speed_right > 0);  //gets set 0 or 1 to tell the motor driver which way to spin
  bool dir_left = (speed_left > 0);

  //constrain pid_output within range
  speed_left = constrain(speed_left, -255, 255);  //ensure that the added turn value doesn't exceed output limits
  speed_right = constrain(speed_right, -255, 255);

  // Speed < 0  => dir=0
  // Speed > 0  => dir=1

  //converts the PID pid_output to 0-255 with a 0 or 1 to determine direction - just for how the DRV8835 motor driver uses pins.

  speed_right = abs(speed_right);
  speed_left = abs(speed_left);

  digitalWrite(APHASE, dir_right);  //the phase pins are digital, meaning they accept 5v or 0v to determine motor direction
  digitalWrite(BPHASE, dir_left);
  analogWrite(AENBL, speed_right);  //the enable pins are analog, meaning they values between 0v and 5v to control motor speed
  analogWrite(BENBL, speed_left);
}
#pragma endregion Driving


/***** LED HELPERS ****/
#pragma region LEDs
/**
 * @brief updates LEDs based on current state setting
*/
void updateLEDs() {
  switch (led_state){
    case RAINBOW:
      rainbowCycle();
      break;

    case BLUSH:
      blush();
      break;
  }
  lastUpdate = millis();  // time for next change to the display
}

/**
 * @brief sets the edge LEDs to pink to make the bot blush
*/
void blush() {
  wipe();
  strip.setPixelColor(0, strip.Color(255, 40, 40));
  strip.setPixelColor(7, strip.Color(255, 40, 40));
  strip.show();
}

/**
 * @brief clears LED bar
*/
void wipe() {  // clear all LEDs
  for (int i = 0; i < strip.numPixels(); i++) {
    strip.setPixelColor(i, strip.Color(0, 0, 0));
  }
}

/**
 * @brief cycles rainbow colors across the LED bar
*/
void rainbowCycle() { 
  static uint16_t j = 0;
  for (int i = 0; i < strip.numPixels(); i++) {
    strip.setPixelColor(i, Wheel(((i * 256 / strip.numPixels()) + j) & 255));
  }
  strip.show();
  j++;
  if (j >= 256 * 5) j = 0;
}

/**
 * @brief cycles colors around the color wheel
 * @return returns with RGB color used to set pixels in rainbowCycle
*/
uint32_t Wheel(byte WheelPos) {  //used to adjust values around the color wheel
  WheelPos = 255 - WheelPos;
  if (WheelPos < 85) {
    return strip.Color(255 - WheelPos * 3, 0, WheelPos * 3);
  }
  if (WheelPos < 170) {
    WheelPos -= 85;
    return strip.Color(0, WheelPos * 3, 255 - WheelPos * 3);
  }
  WheelPos -= 170;
  return strip.Color(WheelPos * 3, 255 - WheelPos * 3, 0);
}
#pragma endregion LEDs

/***** SENSOR HELPERS ****/
#pragma region Sensors
/**
 * @brief checks the distance sensor reading and sets LEDs to blush
*/
void checkDistance() {  //function to check distance with the ultrasonic sensor
  distance = sonar.ping_cm();
  if (distance != 0 && distance < 20) {
    if (!inRange) led_state = BLUSH;
    inRange = true;
  } else {
    inRange = false;
  }
}
#pragma endregion Sensors

/***** SETUP HELPERS ****/
#pragma region Setup Helpers
/**
 * @brief initializes the I2C communications which the IMU will use
*/
void init_i2c() {
  // join I2C bus (I2Cdev library doesn't do this automatically)
#if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
  Wire.begin();
  Wire.setClock(400000);  // 400kHz I2C clock. Comment this line if having compilation difficulties
#elif I2CDEV_IMPLEMENTATION == I2CDEV_BUILTIN_FASTWIRE
  Fastwire::setup(400, true);
#endif
  delay(3);  // ms
}

/**
 * @brief initializes serial communications (and LEDs so we know it's started calibrating)
*/
void init_serial() {

  Serial.begin(38400);
  Serial.println(F(" STARTING UP "));

  strip.begin();            // INITIALIZE NeoPixel strip object (REQUIRED)
  strip.show();             // Turn OFF all pixels ASAP
  strip.setBrightness(60);  // Set BRIGHTNESS to about 1/5 (max = 255)

  updateLEDs();
}

/**
 * @brief initializes pins and PID
*/
void init_pins() {
  digitalWrite(MODE, HIGH); //set the motor driver MODE pin to HIGH, the DRV8835 chip has an alternate mode which require a different pin configuration, check out the datasheet for more info

  pinMode(AENBL, OUTPUT); // configure motor driver pins for output
  pinMode(BENBL, OUTPUT);
  pinMode(APHASE, OUTPUT);
  pinMode(BPHASE, OUTPUT);
}

#pragma endregion Setup Helpers
#pragma endregion FUNCTIONS
//////////////////////////////////////////////////
//  END CODE  //
//////////////////////////////////////////////////
