import serial

from paho.mqtt import client as mqtt_client
from ublox_gps import UbloxGps

port = serial.Serial('/dev/serial0', baudrate=9600, timeout=1)
gps = UbloxGps(port)

broker = 'a5f3481784434027b18630476bc1b277.s2.eu.hivemq.cloud'
port = 8883
client_id = f'amantronic-01'
username = 'amantronic'
password = 'amantronic@1234'

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    # Set Connecting Client ID
    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
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
                publish(client,'/visi/amantronic/rs/geo/lon',geo.lon)
                publish(client,'/visi/amantronic/rs/geo/lat',geo.lat)
                publish(client,'/visi/amantronic/rs/geo/headMot',geo.headMot)
                #print("Longitude: ", geo.lon) 
                #print("Latitude: ", geo.lat)
                #print("Heading of Motion: ", geo.headMot)
                
                gps_time = gps.date_time()
                #print("{}/{}/{}".format(gps_time.day, gps_time.month, gps_time.year))
                #print("UTC Time {}:{}:{}".format(gps_time.hour, gps_time.min, gps_time.sec))
                #print("Valid date:{}\nValid Time:{}".format(gps_time.valid.validDate, gps_time.valid.validTime))
                
                veh = gps.veh_attitude()
                publish(client,'/visi/amantronic/rs/veh/roll',veh.roll)
                publish(client,'/visi/amantronic/rs/veh/pitch',veh.pitch)
                publish(client,'/visi/amantronic/rs/veh/heading',veh.heading)
                publish(client,'/visi/amantronic/rs/veh/accRoll',veh.accRoll)
                publish(client,'/visi/amantronic/rs/veh/accPitch',veh.accPitch)
                publish(client,'/visi/amantronic/rs/veh/accHeading',veh.accHeading)
                
                #print("Roll: ", veh.roll)
                #print("Pitch: ", veh.pitch)
                #print("Heading: ", veh.heading)
                #print("Roll Acceleration: ", veh.accRoll)
                #print("Pitch Acceleration: ", veh.accPitch)
                #print("Heading Acceleration: ", veh.accHeading)
                
            except (ValueError, IOError) as err:
                print(err)

    finally:
        port.close()


if __name__ == '__main__':
    client = connect_mqtt()
    client.loop_start()
    getGPS()