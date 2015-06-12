'''
Created on 03.06.2015

@author: jrenken
'''

import datetime
from nmea import NmeaRecord
from parser import Parser


class IxUsblParser(Parser):
    '''
    Sentence parser for IXBlue USBL Sensors (Posidonia, Gaps)
    '''

    def __init__(self):
        super(IxUsblParser, self).__init__()
        self.headingSource = None        

    def parse(self, data):
        if data.startswith('$PTSAG'):
            return self.decodePtsag(data)
        elif data.startswith('$PTSAH'):
            return self.decodePtsah(data)
        elif data.startswith('$HEHDT'):
            return self.decodeHehdt(data)
#         return {}

    def decodePtsag(self, data):
        nmea = NmeaRecord(data)
        if (nmea.valid):
            result = {'id': int(nmea[6]), 'lat': nmea.fromDDM(7, 8),
                      'lon': nmea.fromDDM(9, 10), 'depth':  float(nmea[12])}
            dt = datetime.datetime(int(nmea[5]), int(nmea[4]), int(nmea[3]), 
                                   int(nmea[2][0:2]), int(nmea[2][2:4]), 
                                   int(nmea[2][4:6]), int(nmea[2][7:]) * 1000)
            td = dt - datetime.datetime(1970, 1, 1)
            result['time'] = td.total_seconds()
            return result

    def decodePtsah(self, data):
        nmea = NmeaRecord(data)
        if nmea.valid:
            return {'id': 0, 'heading': float(nmea[2])}
        
    def decodeHehdt(self, data):
        nmea = NmeaRecord(data)
        if nmea.valid:
            return {'id': 0, 'heading': float(nmea[1])}
