# ParadoxIP150
Python-based IP150 interrogator that publishes data and subscribes to control commands to and from an MQTT broker, without using a headless browser.

## Steps to use it:
1.  Tested Python 2.7.10
2.  Download the files in this repository and place it in some directory
3.  Edit the config.ini file to match your setup
3.  Run the script: Python IP150-MQTT.py

## What to expect:
If successfully connected to your IP150 and MQTT broker, the app will start off with publishing all current zone and partition statuses. The following topics are hardcoded:
* Zone Statuses:
  * Topic: <b>Paradox/ZS/Z1</b>
  * (Z = Zone; followed by the number that has changed)
    * Payload (example): <b>S:0,P:1,N:"Front PIR"</b>
    * (S = Status: 0 = Close, 1 = Open; P = Partition number; Followed by the zone name)
* Alarm Statuses:
  * Topic: <b>Paradox/AS/P1</b>
  * (AS = Alarm Status (Arm, Disarm, etc.); Followed by the partition number)
    * Payload (example):  <b>Disarmed</b>
    * (Possible states = Disarm, Arm, Sleep, Stay, Unsure)
* Siren status:
  * Topic: <b>Paradox/SS</b>
  * (SS = Siren Status)
    * Payload: <b>0</b>
    * (This is still being tested as its a bit problematic due to having neighbours. If this message is published the siren is ON.)
