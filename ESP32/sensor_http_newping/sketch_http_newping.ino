#include <WiFiManager.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <NewPing.h>

//variables for Firebase
const char* API_KEY = "AIzaSyCGbpMrhaH8YEkw_W9sejNX3DAPbGailI8";
const char* DATABASE_URL = "https://iot2025-56325-default-rtdb.europe-west1.firebasedatabase.app";  
const char* USER_EMAIL = "arduin2505@gmail.com";  
const char* USER_PASSWORD = "123456"; 
String idToken; 
String refreshToken;
int expiresIn;

//pins for ultrasonic sensor
#define ECHO_PIN 2              
#define TRIGGER_PIN 4  
#define MAX_DISTANCE 200    
#define SONAR_NUM 1   

//modes for token function
#define RECEIVE 1
#define REFRESH 2

WiFiManager wm;
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

void setup(){
  Serial.begin (9600);
  wm.setDebugOutput(false);
  wm.setConnectTimeout(30);        
  wm.setConfigPortalTimeout(60);  
  wm.setAPCallback([](WiFiManager *myWM){
    Serial.println("Failed to connect to saved Wi-Fi, opening config portal...");
  });
  if (!connectToWiFi()) {
    ESP.restart();
    delay(1000);
  }
  if (!receiveToken(RECEIVE)) {
    ESP.restart();
    delay(1000);
  }
}

void updateRTDB(long distance){
  //Serial.printf("Distance: %d cm\n", distance);
  HTTPClient http;
  String url = String(DATABASE_URL) + "/sensor1/dist.json?auth=" + idToken;
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  String json = String(distance);
  int httpCode = http.PUT(json);
  if (httpCode <= 0) {
    Serial.printf("Error: %s\n", http.errorToString(httpCode).c_str());
    receiveToken(REFRESH);
  }
  http.end();
  delay(1000);
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
  //if sensor isn't connected return 0
    else {
      for (uint8_t i = 0; i < SONAR_NUM; i++) {
        delay(50);
        updateRTDB(sonar.ping_cm());
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

