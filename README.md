# Paradox IP150-MQTT
Python-based IP150 interrogator that publishes data and subscribes to control commands to and from an MQTT broker, without using a headless browser.

<b>NB: This is still a very early release and has its bugs</b>

## Steps to use it:
1.  Tested with Python 2.7.10
2.  Download the files in this repository and place it in some directory
3.  Edit the config.ini file to match your setup
3.  Run the script: Python IP150-MQTT.py

## What to expect:
If successfully connected to your IP150 and MQTT broker, the app will start off by publishing all current zone and partition statuses. The following topics are hardcoded:
* Zone Statuses:
  * Topic: <b>Paradox/ZS/Z1</b>
  * (ZS = Zone Statuses; Z = Zone; followed by the number that has changed)
    * Payload (example): <b>S:0,P:1,N:"Front PIR"</b>
    * (S = Status: 0 = Close, 1 = Open; P = Partition number, followed by the zone name)
* Alarm Statuses:
  * Topic: <b>Paradox/AS/P1</b>
  * (AS = Alarm Status (Arm, Disarm, etc.); P = Partition, followed by the partition number)
    * Payload (example):  <b>Disarmed</b>
    * (Possible states = Disarm, Arm, Sleep, Stay, Unsure)
* Siren status:
  * Topic: <b>Paradox/SS</b>
  * (SS = Siren Status)
    * Payload: <b>?</b>
    * This is still being tested as its a bit problematic with having neighbours. If this message is published there's been some activity with your siren. Deliberately set off the siren to determine what the payload is under different situations.
* Controlling the alarm
  * Publish the following topic to control the alarm:
    * <b>Paradox/C/P1/Disarm</b>
    * (C = Control; P = Partition, followed by number; Then the action = Disarm / Arm / Sleep / Stay)
    * The payload is not evaluated
* Controlling this application
  * Publish the following topics to enable/disable polling of the IP module:
    * <b>Paradox/C/Polling/Enable</b>
    * <b>Paradox/C/Polling/Disable</b>
    * The payload is not evaluated


## Running as a service / daemon

### On Mac
( thanks @Rtaxerxes )

If you want to run this as a daemon on Mac, 
 1. Create a file called local.paradox.plist.
 2. Copy and paste the below into the file, editing for the location of your files.
 3. Copy the file to /Library/LaunchDaemons/.
 4. Run it with: sudo launchctl load /Library/LaunchDaemons/local.paradox.plist
 5. Stop it with: sudo launchctl unload /Library/LaunchDaemons/local.paradox.plist

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
    <dict>
        <key>Label</key>
            <string>local.paradox</string>
        <key>WorkingDirectory</key>
            <string>/(folder where files are)</string>
        <key>ProgramArguments</key>
        <array>
            <string>/usr/bin/python</string>
            <string>/(folder where files are)/IP150-MQTT.py</string>
        </array>
        <key>RunAtLoad</key>
            <true/>
    </dict>
</plist>
```

