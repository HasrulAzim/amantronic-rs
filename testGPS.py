import serial

from ublox_gps import UbloxGps

port = serial.Serial('/dev/serial0', baudrate=9600, timeout=1)
gps = UbloxGps(port)

def run():

    try:
        print("Listening for UBX Messages")
        while True:
            try:
                geo = gps.geo_coords()
                print("Longitude: ", geo.lon) 
                print("Latitude: ", geo.lat)
                print("Heading of Motion: ", geo.headMot)
                
                gps_time = gps.date_time()
                print("{}/{}/{}".format(gps_time.day, gps_time.month, gps_time.year))
                print("UTC Time {}:{}:{}".format(gps_time.hour, gps_time.min, gps_time.sec))
                print("Valid date:{}\nValid Time:{}".format(gps_time.valid.validDate, gps_time.valid.validTime))
                
                veh = gps.veh_attitude()
                print("Roll: ", veh.roll)
                print("Pitch: ", veh.pitch)
                print("Heading: ", veh.heading)
                print("Roll Acceleration: ", veh.accRoll)
                print("Pitch Acceleration: ", veh.accPitch)
                print("Heading Acceleration: ", veh.accHeading)
                
            except (ValueError, IOError) as err:
                print(err)

    finally:
        port.close()


if __name__ == '__main__':
    run()