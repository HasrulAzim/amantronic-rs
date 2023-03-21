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

StartLog = '0'
LogFilename = ''

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print("Failed to connect, return code %d\n", rc)
        
def on_message(client, userdata, message):
    print("message topic=",message.topic)
    if message.topic == "/visi/amantronic/rs/command/startLog":
        StartLog = str(message.payload.decode("utf-8"))
        print(StartLog)
    elif message.topic == "/visi/amantronic/rs/command/filename":
        LogFilename = "home/amantronic/" + str(message.payload.decode("utf-8")) + ".txt"
        print(LogFilename)
        
def connect_mqtt():
    
    # Set Connecting Client ID
    client = mqtt_client.Client(client_id)
 #   client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker, port)
    client.subscribe("/visi/amantronic/rs/command/startLog")
    client.subscribe("/visi/amantronic/rs/command/filename")
    return client
        
def publish(client, topic, msg):
    result = client.publish(topic, msg)
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")
    return result

def getGPS():
    try:
        print("Listening for UBX Messages")
        while True:
            try:
                geo = gps.geo_coords()
                gps_time = gps.date_time()
                veh = gps.veh_attitude()
                Longitude = geo.lon
                Latitude = geo.lat
                HeadingOfMotion = geo.headMot
                publish(client,'/visi/amantronic/rs/geo/lon',geo.lon)
                publish(client,'/visi/amantronic/rs/geo/lat',geo.lat)
                publish(client,'/visi/amantronic/rs/geo/headMot',geo.headMot)
                
                GPS_Time = "{}/{}/{}".format(gps_time.day, gps_time.month, gps_time.year)
                UTC_Time = "{}:{}:{}".format(gps_time.hour, gps_time.min, gps_time.sec)
                publish(client,'/visi/amantronic/rs/time/gps',GPS_Time)
                publish(client,'/visi/amantronic/rs/time/utc',UTC_Time)
                
                Roll = veh.roll
                Pitch = veh.pitch
                Heading = veh.heading
                AccRoll = veh.accRoll
                AccPitch = veh.accPitch
                AccHeading = veh.accHeading
                publish(client,'/visi/amantronic/rs/veh/roll',veh.roll)
                publish(client,'/visi/amantronic/rs/veh/pitch',veh.pitch)
                publish(client,'/visi/amantronic/rs/veh/heading',veh.heading)
                publish(client,'/visi/amantronic/rs/veh/accRoll',veh.accRoll)
                publish(client,'/visi/amantronic/rs/veh/accPitch',veh.accPitch)
                publish(client,'/visi/amantronic/rs/veh/accHeading',veh.accHeading)
                
                Dataset = [Longitude,Latitude,HeadingOfMotion,GPS_Time,UTC_Time,Roll,Pitch,Heading,AccRoll,AccPitch,AccHeading]
                
                if StartLog == '1':
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
    client.loop_forever
    getGPS()