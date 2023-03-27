import serial

from paho.mqtt import client as mqtt_client
from ublox_gps import UbloxGps

port = serial.Serial('/dev/serial0', baudrate=9600, timeout=1)
gps = UbloxGps(port)

broker = 'test.mosquitto.org'
port = 1883
client_id = f'amantronic-01'
#username = 'amantronic'
#password = 'amantronic@1234'

StartLog = False
LogFilename = "/home/amantronic/testFile.txt"
BrokerConnected = False


def on_connect(client, userdata, flags, rc):
    global BrokerConnected
    if rc == 0:
        BrokerConnected = True
        print("Connected to MQTT Broker!")
    else:
        BrokerConnected = False
        print("Failed to connect, return code %d\n", rc)
    
def on_message(client, userdata, message):
    global StartLog
    global LogFilename
    #print("message topic=",message.topic)
    if message.topic == "/visi/amantronic/rs/command/startLog":
        StartLog = str(message.payload.decode("utf-8")) 
    elif message.topic == "/visi/amantronic/rs/command/filename":
        LogFilename = "/home/amantronic/" + str(message.payload.decode("utf-8")) + ".txt"
    
def connect_mqtt():
    
    # Set Connecting Client ID
    client = mqtt_client.Client(client_id)
 #   client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker, port)
    client.loop_start()
    client.subscribe("/visi/amantronic/rs/command/startLog")
    client.subscribe("/visi/amantronic/rs/command/filename")
    return client
        
def publish(client, topic, msg):
    result = client.publish(topic, msg)
    status = result[0]
    if status == 0:
        #pass
        print(f"Send `{msg}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")
    return result

def getGPS():
    global StartLog
    global LogFilename
    try:
        while True:
            try:
                geo = gps.geo_coords()
                gps_time = gps.date_time()
                veh = gps.veh_attitude()
                
                Longitude = "{:.6f}".format(geo.lon)
                Latitude = "{:.6f}".format(geo.lat)
                HeadingOfMotion = "{:.5f}".format(geo.headMot)
                
                GPS_Time = "{}/{}/{}".format(gps_time.day, gps_time.month, gps_time.year)
                UTC_Time = "{}:{}:{}".format(gps_time.hour, gps_time.min, gps_time.sec)
                
                Roll = "{:.1f}".format(veh.roll)
                Pitch = "{:.1f}".format(veh.pitch)
                Heading = "{:.1f}".format(veh.heading)
                AccRoll = "{:.5f}".format(veh.accRoll)
                AccPitch = "{:.5f}".format(veh.accPitch)
                AccHeading = "{:.5f}".format(veh.accHeading)
                
                print("Transmitting data to broker...")
                publish(client,'/visi/amantronic/rs/geo/lon',Longitude)
                publish(client,'/visi/amantronic/rs/geo/lat',Latitude)
                publish(client,'/visi/amantronic/rs/geo/headMot',HeadingOfMotion)
                publish(client,'/visi/amantronic/rs/time/gps',GPS_Time)
                publish(client,'/visi/amantronic/rs/time/utc',UTC_Time)
                publish(client,'/visi/amantronic/rs/veh/roll',Roll)
                publish(client,'/visi/amantronic/rs/veh/pitch',Pitch)
                publish(client,'/visi/amantronic/rs/veh/heading',Heading)
                publish(client,'/visi/amantronic/rs/veh/accRoll',AccRoll)
                publish(client,'/visi/amantronic/rs/veh/accPitch',AccPitch)
                publish(client,'/visi/amantronic/rs/veh/accHeading',AccHeading)
                
                Dataset = [GPS_Time,UTC_Time,Longitude,Latitude,HeadingOfMotion,Roll,Pitch,Heading,AccRoll,AccPitch,AccHeading]
                
                if StartLog == '1':
                    #print("Writing to log file "+LogFilename+".txt")
                    with open(LogFilename, 'a') as f:
                        f.write(','.join(Dataset))
                        f.write('\n')
                
            except (ValueError, IOError) as err:
                print(err)

    finally:
        port.close()

if __name__ == '__main__':
    print("Connecting to MQTT Broker '{broker}'")
    client = connect_mqtt()
    getGPS()
    