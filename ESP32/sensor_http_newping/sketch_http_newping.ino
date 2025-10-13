#include <WiFiManager.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <NewPing.h>
#include <Preferences.h>
#include "../parameters.h"

int dummyChange = 3;

String idToken; 
String refreshToken;
int expiresIn;
int carNumber = -1; // Default car number value

// Pins for ultrasonic sensor
#define ECHO_PIN 2              
#define TRIGGER_PIN 4  
#define MAX_DISTANCE 200    
#define SONAR_NUM 1   

// Modes for token function
#define RECEIVE 1
#define REFRESH 2

// Values for sensor processing
#define NUM_OF_SAMPLES 2
#define NON_ACCUPIED_SAMPLE 110
#define SENSOR_THRESHOLD 60

WiFiManager wm;
Preferences preferences;
NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE); 

//function to connect to Wi-Fi
int connectToWiFi(){
  Serial.println("Trying to connect to saved Wi-Fi...");
  bool res;
  res = wm.autoConnect("AutoConnectAP","password");
  if(!res) {
    Serial.println("Config portal closed, restarting...");
    return 0;
  } 
  else { 
    Serial.println("Connected");
    return 1;
  }
}

//function to receive or refresh token
int receiveToken(int mode){
  HTTPClient http;
  String payload;
  switch (mode)
  {
  case RECEIVE:
    http.begin("https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=" + String(API_KEY));
    http.addHeader("Content-Type", "application/json");
    payload = "{\"email\":\"" + String(USER_EMAIL) + "\",\"password\":\"" + String(USER_PASSWORD) + "\",\"returnSecureToken\":true}";
    break;
  case REFRESH:
    http.begin("https://securetoken.googleapis.com/v1/token?key=" + String(API_KEY));
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");
    payload = "grant_type=refresh_token&refresh_token=" + refreshToken;
    break;
  default:
    break;
  }
  int httpCode = http.POST(payload);
  if (httpCode == 200) {
    String response = http.getString();
    //Serial.println("Raw response:");
    //Serial.println(response);
    StaticJsonDocument<2048> doc;  
    DeserializationError error = deserializeJson(doc, response);
    if (error) {
      Serial.print("JSON parse error: ");
      Serial.println(error.f_str());
    } else {
      idToken = doc["idToken"].as<String>();
      refreshToken = doc["refreshToken"].as<String>();
      expiresIn = doc["expiresIn"].as<int>();
      //Serial.println("Got idToken: " + idToken);
      //Serial.println("Got refreshToken: " + refreshToken);
      Serial.printf("Token expires in %d seconds\n", expiresIn);
    }   
  } else {
    switch (mode)
    {
    case RECEIVE:
    Serial.printf("Auth failed, code: %d\n", httpCode);
    Serial.println(http.getString());
      break;
    case REFRESH:
    Serial.printf("Token refresh failed, code: %d\n", httpCode);
    Serial.println(http.getString());
      break;
    default:
      break;
    }
    return 0;
  }
  http.end();
  return 1;
}

// An array of the 'NUM_OF_SAMPLES' last sampled values.
unsigned long last_samples_arr[NUM_OF_SAMPLES];
int last_samples_arr_index = 0;

// Returns car number
int getCarNumber() {
  preferences.begin("config", true); // read-only
  int idx = preferences.getInt("carNumber", -1); // default -1 if not found
  preferences.end();
  return idx;
}

// Set a new car number
void setCarNumber(int newNum) {
  preferences.begin("config", false); // read-write
  preferences.putInt("carNumber", newNum); // commits automatically
  preferences.end();
  carNumber = newNum;
  Serial.printf("Save new index: %d\n", carNumber);
}

void setup(){
  Serial.begin (9600);
  wm.resetSettings();
  wm.setDebugOutput(false); // Disable debug logs.
  wm.setConnectTimeout(30); // WM will try to connect to saved WiFi for 30 seconds, and then move on.
  wm.setConfigPortalTimeout(60); // Creating a "hotspot" for 60 seconds.

  wm.setAPCallback([](WiFiManager *myWM){ // Print an error message if failed to connect to WiFi.
    Serial.println("Failed to connect to saved Wi-Fi, opening config portal...");
  });

  // Load saved car number from saved memory.
  carNumber = getCarNumber();
  Serial.printf("Loaded car number: %d\n", carNumber);

  // Create a custom WiFiManager parameter
  char carNumberArr[8];
  sprintf(carNumberArr, "%d", carNumber);
  WiFiManagerParameter wmCarNumber("carNumber", "car number", carNumberArr, 8);
  wm.addParameter(&wmCarNumber);

  if (!connectToWiFi()) {
    ESP.restart();
    delay(1000);
  }

  // Save updated car number if changed in WiFiManager portal
  String newCarNumber = wmCarNumber.getValue();
  int newNum = atoi(newCarNumber.c_str());
  if (newNum != carNumber) {
    setCarNumber(newNum);
  }

  if (!receiveToken(RECEIVE)) {
    ESP.restart();
    delay(1000);
  }
  for (int i = 0; i < NUM_OF_SAMPLES; i++) { // Initialize with non-occupied sampled values.
      last_samples_arr[i] = NON_ACCUPIED_SAMPLE;
  }
}

void updateRTDB(long distance, int seatNumber){
  //Serial.printf("Distance: %d cm\n", distance);
  HTTPClient http;
  String url = String(DATABASE_URL) + "/cars/" + carNumber + "/seats/" + seatNumber + "/sensorDistance.json?auth=" + idToken;
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  String json = String(distance);
  int httpCode = http.PUT(json);
  if (httpCode <= 0 || httpCode == 401) {
    Serial.printf("Error: %s\n", http.errorToString(httpCode).c_str());
    receiveToken(REFRESH);
  }
  http.end();
  delay(500);
}

void updateRTDB_bool(bool occupied, int seatNumber){
  HTTPClient http;
  String url = String(DATABASE_URL) + "/cars/" + carNumber + "/seats/" + seatNumber + "/Occupied.json?auth=" + idToken;  
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  String json = occupied ? "true" : "false";
  int httpCode = http.PUT(json);
  if (httpCode <= 0 || httpCode == 401) {
    Serial.printf("Error: %s\n", http.errorToString(httpCode).c_str());
    receiveToken(REFRESH);
  }
  http.end();
  delay(500);
}

// Updates the car number saved in the microcontroller, through changes made in FireBase.
void carNumberUpdateRTDB(){
  //Serial.printf("Distance: %d cm\n", distance);
  HTTPClient http;
  String url = String(DATABASE_URL) + "/Settings/controller_index.json?auth=" + idToken;
  http.begin(url);
  int httpCode = http.GET();
  if(httpCode == 200){
    String payload = http.getString();
    int newNum = payload.toInt();
    if(newNum != carNumber){
      setCarNumber(newNum);
      Serial.printf("car number updated to %d from Firebase\n", newNum);
    }
  }
  if (httpCode <= 0 || httpCode == 401) {
    Serial.printf("Error: %s\n", http.errorToString(httpCode).c_str());
    receiveToken(REFRESH);
  }
  http.end();
  delay(500);
}

void loop(){
  if (WiFi.status() == WL_CONNECTED) {
    if (idToken.length() == 0) {
      Serial.println("No token");
      if (!receiveToken(REFRESH)) {
        ESP.restart();
        delay(1000);
      }
    }
    else { // If there is a token, update each sensor return values.
      for (uint8_t i = 1; i <= SONAR_NUM; i++) {
        delay(500); // Wait one second between samples.
        unsigned long ping_val = sonar.ping_cm();
        last_samples_arr[last_samples_arr_index] = ping_val; // Update the samples array
        last_samples_arr_index = (last_samples_arr_index + 1) % NUM_OF_SAMPLES; // Update the array index cyclically
        bool occupied = is_occupied(last_samples_arr);
        updateRTDB(ping_val, i);
        updateRTDB_bool(occupied, i);
        Serial.println(occupied);    
        Serial.println(ping_val);    
      }
    }
  }
  else {
    Serial.println("Connection lost");
      if (!connectToWiFi()) {
        ESP.restart();
        delay(1000);
      }
    delay(1000);
  }
}

bool is_occupied(unsigned long last_samples_arr[NUM_OF_SAMPLES]){
  int number_of_samples_smaller_then_thresh = 0;
  for(int i = 0; i < NUM_OF_SAMPLES; i++){
    if(last_samples_arr[i] < SENSOR_THRESHOLD){
      number_of_samples_smaller_then_thresh++;
    }
  }
  // Return 'occupied' if there are 2 occupied samples.
  float error_threshold = 1;
  return number_of_samples_smaller_then_thresh >= error_threshold ? true : false;
}

