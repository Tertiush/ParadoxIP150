import hashlib
import socket
import time
import lib.client as mqtt
import sys
import array
import random
import ConfigParser


#Do not edit these variables here, use the config.ini file instead.
passw = "abcd"
user = "1234"
IP150_IP = "10.0.0.120"
IP150_Port = 8080
Poll_Speed = 0.5                            #Seconds (float)
MQTT_IP = "10.0.0.130"
MQTT_Port = 1883
MQTT_KeepAlive = 60                         #Seconds
MQTT_Control_Subscribe = "Paradox/C/"       #e.g. To arm partition 1: Paradox/C/P1/Arm
                                            #Options are Arm, Disarm, Stay, Sleep (case sensitive!)

#Global variables
Control_Action = 0
Control_Partition = ""
Control_NewState = ""


def ConfigSectionMap(section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                print ("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1


def rc4(key, text):
#    var i, x, y, t, temp, x2, kl;
    print "spass: " + key
    print "user: " + text
    kl = len(key)

    s = [0] * 256
    for i in range(0, 256):
        s[i] = i
    y = 0
    x = kl
    while x != 0:
        x = x - 1
        y = (ord(key[x]) + s[x] + y) % 256
        #print "y: " + str(y)
        t = s[x]
        s[x] = s[y]
        s[y] = t
    #print "s: "
    #print s
    x = 0
    y = 0
    z = ""
    for x in range(0,len(text)):
        x2 = x & 255
        y = (s[x2] + y) & 255
        t = s[x2]
        s[x2] = s[y]
        s[y] = t
        temp = chr(ord(text[x]) ^ s[(s[x2] + s[y]) % 256])  #temp = String.fromCharCode((text.charCodeAt(x) ^ s[(s[x2] + s[y]) % 256]))
        #print "temp" + str(x) + ": " + str(ord(temp))
        #print "ord(temp[0]: "  + str(ord(temp[0]))
        z += d2h(ord(temp[0]))

    #print "z: " + z
    return z


def d2h(d):
    #print "d: " + str(d)
    hd = "0123456789ABCDEF"
    h = hd[d & 15: (d & 15) + 1]
    #print "h_initial: " + h
    while d > 15:
        d >>= 4
        h = hd[d & 15: (d & 15) + 1] + h

    if len(h) == 1:
        h = "0" + h

    #print "h: " + h
    return h


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # client.subscribe("$SYS/#")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global Control_Partition
    global Control_NewState
    global Control_Action

    valid_states = ['Arm','Disarm','Sleep','Stay']

    print("MQTT Message: " + msg.topic+" "+str(msg.payload))

    topic = msg.topic

    if MQTT_Control_Subscribe in msg.topic:
        try:
            Control_Partition = (topic.split(MQTT_Control_Subscribe + 'P'))[1].split('/')[0]
            print "Control Partition: ", Control_Partition
            Control_NewState = (topic.split('/P'+Control_Partition+'/'))[1]
            print "Control's New State: ", Control_NewState

            if Control_NewState == "Arm":
                Control_NewState = 'r'
            elif Control_NewState == "Disarm":
                Control_NewState = 'd'
            elif Control_NewState == "Sleep":
                Control_NewState = 'p'
            elif Control_NewState == "Stay":
                Control_NewState = 's'
            else:
                raise

            Control_Action = 1
        except:
            print "MQTT message received within incorrect structure"

def connect_ip150socket(address,port):

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        s.connect((address, port))
    except Exception, e:
        print "Error connecting to IP module: " + repr(e)

    return s

def connect_ip150login():

    got_ses = 4

    while got_ses != 0:
        try:
            socketclient = connect_ip150socket(IP150_IP, IP150_Port)
            socketclient.send("GET /login_page.html HTTP/1.1\r\n\r\n")
            data = socketclient.recv(4096)
            data += socketclient.recv(4096)
            data += socketclient.recv(4096)
            ses = (data.split('loginaff("'))[1].split('",')[0]
            if len(ses) == 16:
                print "SES Key Found: ", ses
                got_ses = 0
            else:
                got_ses = got_ses - 1
                print "SES key not found in reply... ({})".format(got_ses)
                socketclient.close()
                time.sleep(4)
        except:
            got_ses = got_ses - 1
            print "No connection to IP Module, are you already logged in? Attempting logout and trying again... ({})".format(
                got_ses)
            socketclient.close()
            if got_ses == 0:
                print "Failure, cannot connect"
                print "Last received data: "
                print data
                sys.exit()
            time.sleep(2)
            socketclient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socketclient.settimeout(2)
            socketclient.connect((IP150_IP, IP150_Port))
            socketclient.send("GET /logout.html HTTP/1.1\r\nHost: " + IP150_IP + ':' + str(IP150_Port) + "\r\nConnection: keep-alive\r\nCache-Control: max-age=0\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\nUpgrade-Insecure-Requests: 1\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36\r\nAccept-Encoding: gzip, deflate, sdch\r\nAccept-Language: en,af;q=0.8,en-GB;q=0.6\r\n\r\n")
            data = socketclient.recv(4096)
            if "200 OK" in data:
                print "Disconnect OK received from IP Module"
            socketclient.close()

            time.sleep(2)


            # print "received data:", data
            #    s.close()

    passw_md5 = hashlib.md5()
    passw_md5.update(passw)
    passw_enc = passw_md5.hexdigest()

    interim_pass = hashlib.md5()
    spass = passw_enc.upper() + ses
    interim_pass.update(spass)
    p = interim_pass.hexdigest()
    p = p.upper()

    u = rc4(spass, user)

    print "P: " + p
    print "U: " + u

    #    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #    s.connect(('10.0.0.120', 8085))

    socketclient.close()
    socketclient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socketclient.settimeout(10)
    socketclient.connect((IP150_IP, IP150_Port))

    # Read/discard the reply messages, allow sufficient time for scripts etc to be received before starting to poll the device

    data, s = connect_ip150readData(socketclient,"GET /default.html?u=" + u + "&p=" + p + " HTTP/1.1\r\nHost: " + IP150_IP + ':' + str(IP150_Port) + "\r\nConnection: keep-alive\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\nUpgrade-Insecure-Requests: 1\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36\r\nReferer: http://" + IP150_IP + ':' + str(IP150_Port) + "/login_page.html\r\nAccept-Encoding: gzip, deflate, sdch\r\nAccept-Language: en,af;q=0.8,en-GB;q=0.6\r\n\r\n")

    if "200 OK" in data:
        print "OK received from requesting: default.html"

    print "Waiting for initial data to be received (scripts, etc.)..."
    for timer in range(1, 8, 1):
        time.sleep(1)
        print "."

    return u, p, socketclient


def connect_ip150readData(socketclient, request):

    tries = 4

    while tries > 0:
        try:

            socketclient.send(request)

            inc_data = socketclient.recv(4096)
            inc_data += socketclient.recv(4096)
            inc_data += socketclient.recv(4096)
            inc_data += socketclient.recv(4096)

            tries = 0

        except Exception, e:
            print "Error reading data from IP module, retrying (" + str(tries) + "): " + repr(e)
            tries = tries - 1
            socketclient.close
            time.sleep(2)
            socketclient = connect_ip150socket(IP150_IP, IP150_Port)
            inc_data = "error"

    return inc_data, socketclient


if __name__ == '__main__':

    Config = ConfigParser.ConfigParser()
    Config.read("config.ini")
    passw = Config.get("IP150","Password")
    user = Config.get("IP150","Pincode")
    IP150_IP = Config.get("IP150","IP")
    IP150_Port = int(Config.get("IP150","HTTP_Port"))

    MQTT_IP = Config.get("MQTT Broker","IP")
    MQTT_Port = int(Config.get("MQTT Broker","Port"))


    #print ConfigSectionMap("IP150")
    #IP150_IP = ConfigSectionMap("IP150")['IP']

    u,p,s = connect_ip150login()



    # --------------MQTT----------------

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_IP, MQTT_Port, MQTT_KeepAlive)

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    # client.loop_forever()

    # client.disconnect()

    client.loop_start()

    client.subscribe(MQTT_Control_Subscribe + "#")
    # --------------MQTT----------------

    s.close()
    # Get zone definitions
    print "Get zone definitions"
    s = connect_ip150socket(IP150_IP, IP150_Port)

    data, s = connect_ip150readData(s, "GET /index.html HTTP/1.1\r\nHost: " + IP150_IP + ':' + str(IP150_Port) + "\r\nConnection: keep-alive\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\nUpgrade-Insecure-Requests: 1\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36\r\nReferer: http://" + IP150_IP + ':' + str(IP150_Port) + "/default.html?u=" + u + "&p=" + p + "\r\nAccept-Encoding: gzip, deflate, sdch\r\nAccept-Language: en,af;q=0.8,en-GB;q=0.6\r\n\r\n")
    #print data
    alarmname = (data.split('top.document.title="'))[1].split('";')[0]
    print "Alarm Name: ", alarmname
    AreaNames = (data.split('tbl_areanam = new Array('))[1].split(');')[0].split(',')
    print "Area Names: ", AreaNames
    ZoneNames = (data.split('tbl_zone = new Array('))[1].split(');')[0].split(',')
    print "Zone Names & Partition assignment: ", ZoneNames
    s.close()

    TotalZones = int(round(len(ZoneNames)/2))

    print "Zone Names (Total: " + str(TotalZones) + "): ", ZoneNames

    ZoneStatuses = array.array('i', (-1 for i in range(1, TotalZones+2)))

    AlarmStatus = [None] * TotalZones

    SirenStatus = "empty"

    start_time = time.time()

    print "Connected and polling data every " + str(Poll_Speed) + "s"

    while True:

        print(".")

        s = connect_ip150socket(IP150_IP, IP150_Port)

        elapsed_time = time.time() - start_time
        #print "Time elapsed: ", elapsed_time

        if elapsed_time > 5:
            start_time = time.time()

            keep_alive_url = "/keep_alive.html?msgid=1" + "&" + str(random.randint(0,99999999999999999))

            #print "Requesting /keep_alive.html"
            data, s = connect_ip150readData(s, "GET " + keep_alive_url + " HTTP/1.1\r\nHost: " + IP150_IP + ':' + str(IP150_Port) + "\r\nConnection: keep-alive\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36\r\nAccept: */*;q=0.8\r\nReferer: http://" + IP150_IP + ':' + str(IP150_Port) + "/menu.html\r\nAccept-Encoding: gzip, deflate, sdch\r\nAccept-Language: en,af;q=0.8,en-GB;q=0.6\r\n\r\n")
            if "200 OK" in data:
                #print "Keep-alive 200 OK received from IP Module"
                print "-"
            #print data
            s.close()
            s = connect_ip150socket(IP150_IP, IP150_Port)

        data, s = connect_ip150readData(s,"GET /statuslive.html?u=" + u + "&p=" + p + " HTTP/1.1\r\nHost: " + IP150_IP + ':' + str(IP150_Port) + "\r\nConnection: keep-alive\r\nCache-Control: max-age=0\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\nUpgrade-Insecure-Requests: 1\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36\r\nAccept-Encoding: gzip, deflate, sdch\r\nAccept-Language: en,af;q=0.8,en-GB;q=0.6\r\n\r\n")

        zones = (data.split('tbl_statuszone = new Array'))[1].split(';var')[0]

        for counter in range (1,TotalZones+1,1):
            if ZoneStatuses[counter] != int(zones[counter*2-1]):
                ZoneStatuses[counter] = int(zones[counter*2-1])
                client.publish("Paradox/ZS/Z" + str(counter), "S:" + str(ZoneStatuses[counter]) + ",P:" + ZoneNames[counter*2-2] + ",N:" + ZoneNames[counter*2-1], qos=0, retain=False)


        AlarmStatusRead = (data.split('tbl_useraccess = new Array('))[1].split(')')[0].split(',')

        for c, val in enumerate(AlarmStatusRead):
            if AlarmStatus[c] != val:
                if val == '1':
                    newstate = "Disarmed"
                elif val == '2':
                    newstate = "Armed"
                elif val == '3':
                    newstate = "Stay"
                elif val == '4':
                    newstate = "Sleep"
                else:
                    newstate = "Unsure"

                client.publish("Paradox/AS/P" + str(c+1), newstate, qos=0, retain=False)
        AlarmStatus = AlarmStatusRead

        SirenStatusRead = (data.split('tbl_alarmes = new Array('))[1].split(')')[0]

        if SirenStatusRead != SirenStatus:
            client.publish("Paradox/SS", str(SirenStatusRead), qos=0, retain=False)
            SirenStatus = SirenStatusRead



        #print "Polling (i=", i, ") - , Zones: " + zones + " - ", AlarmStatus

        s.close()

        if Control_Action == 1:
            Control_Action = 0
            print "Preparing to send a control command"
            s = connect_ip150socket(IP150_IP, IP150_Port)

            data, s = connect_ip150readData(s, "GET /statuslive.html?area=0" + str(int(Control_Partition)-1) + "&value=" + Control_NewState + " HTTP/1.1\r\nHost: " + IP150_IP + ':' + str(IP150_Port) + "\r\nConnection: keep-alive\r\nCache-Control: max-age=0\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\nUpgrade-Insecure-Requests: 1\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36\r\nAccept-Encoding: gzip, deflate, sdch\r\nAccept-Language: en,af;q=0.8,en-GB;q=0.6\r\n\r\n")

            time.sleep(1)  # Short delay to ensure status is updated before reading again
            s.close()

        time.sleep(Poll_Speed)

