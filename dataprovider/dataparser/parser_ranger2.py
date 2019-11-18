'''
Created on 06.07.2015

@author: jrenken
'''
from __future__ import absolute_import

from datetime import datetime, timezone
from .nmea import NmeaRecord
from .parser import Parser


class Ranger2Parser(Parser):
    '''
    Parser for the PSONLLD sentences provided by Sonardyne USBL system Ranger2
    $PSONLLD,153005.253,24,A,50.02495,8.873323,425.3,,,,,,,,*3e<CR><LF>
    Ships heading is only provided by the PSONALL sentence  ----v.
    $PSONALL,Ship 1,CRP,134446.175,650879.00,5688874.16,0.00,180.00,,G,0.00,0.00,,0.109,0.001*51
    '''

    def __init__(self):
        '''
        constructor only calls the parents class constructor
        '''
        super(Ranger2Parser, self).__init__()

    def parse(self, data):
        if data.startswith('$PSONLLD'):
            return self.decodeLld(data)
        elif data.startswith('$PSONALL'):
            return self.decodeAll(data)

    def decodeLld(self, data):
        nmea = NmeaRecord(data)
        if (nmea.valid):
            try:
                if nmea[3] == 'V':
                    return {}
                result = {'id': nmea[2], 'lat': nmea.value(4),
                          'lon': nmea.value(5), 'depth': nmea.value(6)}
                t = datetime.now(tz=timezone.utc)
                try:
                    dt = datetime(t.year, t.month, t.day,
                         int(nmea[1][0:2]), int(nmea[1][2:4]),
                         int(nmea[1][4:6]), int(nmea[1][7:]) * 100, tzinfo=timezone.utc)
                except ValueError:
                    dt = t
                result['time'] = (dt - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds()
                return dict((k, v) for k, v in result.items() if v is not None)
            except ValueError:
                return {}

    def decodeAll(self, data):
        nmea = NmeaRecord(data)
        if (nmea.valid):
            try:
                result = {'id': nmea[1], 'heading': nmea.value(7),
                          'course': nmea.value(8)}
                return dict((k, v) for k, v in result.items() if v is not None)
            except ValueError:
                return {}
