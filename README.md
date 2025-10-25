## Smart Train Seating Project by : Boaz Maron, Zohar Abramovich, Libi Kogan
  
## Details about the project
Modern train systems often face boarding delays caused by uneven passenger distribution along the platform.
Our project uses an ESP32 DevKit V1 and an HC-SR04 ultrasonic sensor to detect whether seats in a train are occupied. The data is displayed on a website and used to calculate boarding statistics, showing that if passengers know where free seats are and spread along the platform accordingly, train boarding delays can be reduced.


## Main features:
  1) Real-time detection of free and occupied seats using ultrasonic sensors.
  2) Automatic data transmission from ESP32 to a cloud-hosted web dashboard.
  3) Statistical analysis of passenger flow to check boarding efficiency.
 
## Folder description :
* Documentation: wiring diagram + basic operating instructions.
* ESP32: Firmware for the ESP32 microcontroller. Handles all the low-level magic.
* Simulation: Source code for the system simulation environment.
* UI: The user interface code.

## ESP32 SDK version used in this project: 
Arduino-ESP32 Core v3.0.0

## Arduino/ESP32 libraries used in this project:
* WiFiMamager - version 2.0.17
* NewPing - version 1.9.7
* ArduinoJson - version 7.4.2
* Preferences - version 2.2.2

## Project Poster:
![Wiring Diagram](Documentation/connection%20diagram/Wiring%20diagram.jpg)

 
This project is part of ICST - The Interdisciplinary Center for Smart Technologies, Taub Faculty of Computer Science, Technion
https://icst.cs.technion.ac.il/ 
