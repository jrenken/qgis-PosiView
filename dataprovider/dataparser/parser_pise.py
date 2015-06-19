'''
Created on 03.06.2015

@author: jrenken
'''

import datetime
from nmea import NmeaRecord
from parser import Parser


class PiseParser(Parser):
    '''
    $PISE,AUV,<Latitude>,<Longitude>,<date>,<time>,<position_source>,<false>,<heading>,<depth>,<speed>*<checksum>
    '''
    
    def __init__(self):
        super(PiseParser, self).__init__()
        
    def parse(self, data):
        if data.startswith('$PISE'):
            nmea = NmeaRecord(data)
            if nmea.valid:
                result = {'id': nmea[1], 
                          'lat': float( nmea[2]), 
                          'lon': float( nmea[3]),
                          'heading': float( nmea[8]),
                          'depth': float( nmea[9]),
                          'speed': float( nmea[10])}
                dt = datetime.datetime(int(nmea[4][0:4]), int(nmea[4][4:6]), int(nmea[4][6:]), 
                                   int(nmea[5][0:2]), int(nmea[5][2:4]), 
                                   int(nmea[5][4:6]))
                td = dt - datetime.datetime(1970, 1, 1)
                result['time'] = td.total_seconds()
                return result
