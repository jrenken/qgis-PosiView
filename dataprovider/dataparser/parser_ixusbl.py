'''
Created on 03.06.2015

@author: jrenken
'''
from __future__ import absolute_import

from datetime import datetime, timezone
from .nmea import NmeaRecord
from .parser import Parser


class IxUsblParser(Parser):
    '''
    Sentence parser for IXBlue USBL Sensors (Posidonia, Gaps)
    '''

    def __init__(self):
        super(IxUsblParser, self).__init__()

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
            try:
                result = {'id': nmea.value(6), 'lat': nmea.fromDDM(7, 8),
                          'lon': nmea.fromDDM(9, 10), 'depth': nmea.value(12)}
                try:
                    dt = datetime(int(nmea[5]), int(nmea[4]), int(nmea[3]),
                                   int(nmea[2][0:2]), int(nmea[2][2:4]),
                                   int(nmea[2][4:6]), int(nmea[2][7:]) * 1000, tzinfo=timezone.utc)
                except ValueError:
                    dt = datetime.now(tz=timezone.utc)
                result['time'] = (dt - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds()
                return dict((k, v) for k, v in result.items() if v is not None)
            except ValueError:
                return {}

    def decodePtsah(self, data):
        nmea = NmeaRecord(data)
        if nmea.valid:
            h = nmea.value(2)
            if h is not None:
                return {'id': 0, 'heading': h}
            return {}

    def decodeHehdt(self, data):
        nmea = NmeaRecord(data)
        if nmea.valid:
            h = nmea.value(1)
            if h is not None:
                return {'id': 0, 'heading': h}
            return {}
