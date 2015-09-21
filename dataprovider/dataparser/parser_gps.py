'''
Created on 03.07.2015

@author: jrenken
'''

import datetime
from nmea import NmeaRecord
from parser import Parser


class GpsParser(Parser):
    '''
    classdocs
    $GPRMC,140808,A,5301.4970,N,00852.1740,E,000.0,000.0,030715,0.4,E,N*15
    '''

    def __init__(self):
        '''
        Constructor
        '''
        super(GpsParser, self).__init__()

    def parse(self, data):
        if data.startswith('$GPRMC'):
            return self.decodeRmc(data)
        elif data.startswith('$GPVTG'):
            return self.decodeVtg(data)

    def decodeRmc(self, data):
        nmea = NmeaRecord(data)
        if (nmea.valid):
            try:
                result = {'lat': nmea.fromDDM(3, 4),
                          'lon': nmea.fromDDM(5, 6)}
                dt = datetime.datetime(int(nmea[9][4:]) + 2000, int(nmea[9][2:4]), int(nmea[9][0:2]),
                                   int(nmea[1][0:2]), int(nmea[1][2:4]),
                                   int(nmea[1][4:6]))
                td = dt - datetime.datetime(1970, 1, 1)
                result['time'] = td.total_seconds()
                return result
            except ValueError:
                return {}

    def decodeVtg(self, data):
        nmea = NmeaRecord(data)
        if (nmea.valid):
            try:
                return {'heading': float(nmea[1])}
            except ValueError:
                return {}
