# Script to run at backend, interpreting the GPS coordinates sent over LoRaWAN
import math

class Read_GPS_coordinates:
    def reset_coordinate(self):
        global data, latitude, longitude, ns, we, hdop
        latitude = 91.0
        ns = 'N'
        longitude = 181.0
        we = 'E'
        hdop = 0
        data = [latitude, ns, longitude, we, hdop]

    def read_coordinate(self, s):               # Read HEX string sent over LoRa and convert coordinate data
        global data, latitude, longitude, ns, we, hdop
        [latitude, ns, longitude, we, hdop] = s.decode('hex').split(',')
        latitude = float(latitude)
        longitude = float(longitude)
        hdop = float(hdop)

        deg = math.floor(latitude/100)          # Convert latitude and longitude to correct format
        min = latitude - (deg*100)              # 51.1234567 04.1234567
        latitude = deg + (min/60)
        print latitude
        deg = math.floor(longitude / 100)
        min = longitude - (deg * 100)
        longitude = deg + (min / 60)
        print longitude

        if ns == 'S':
            latitude *= -1
        if we == 'W':
            longitude *= -1

    def print_coordinate(self):
        print('Coordinate: {}{} {}{} (HDOP = {})'.format(ns, latitude, we, longitude, hdop))


# Init coordinates with unrealistic values
latitude = 91.0
ns = 'N'
longitude = 181.0
we = 'E'
hdop = 0
data = [latitude, ns, longitude, we, hdop]

GPSread = Read_GPS_coordinates()
#while True:
s = "353131302e363538302c4e2c30303432342e3934312c452c312e31"
GPSread.reset_coordinate()
GPSread.read_coordinate(s)
GPSread.print_coordinate()


