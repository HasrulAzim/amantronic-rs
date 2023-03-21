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
BrokerConnected = False