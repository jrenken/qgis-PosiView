'''
Created on 12.06.2015

@author: jrenken
'''
from __future__ import absolute_import

from datetime import datetime, timezone
from .parser import Parser
from .nmea import NmeaRecord


class MiniPosParser(Parser):
    '''
    Parser for the Saab MiniPos3 data output
    $PSAAS,101301.06,5832.74,N,01458.52,E,176.3,4.3,4.8,1.20,-1.00,-0.30*54
    '''

    def __init__(self):
        '''
        Constructor
        '''
        super(MiniPosParser, self).__init__()

    def parse(self, data):
        if data.startswith('$PSAAS'):
            nmea = NmeaRecord(data)
            if nmea.valid:
                try:
                    result = {'lat': nmea.fromDDM(2, 3),
                              'lon': nmea.fromDDM(4, 5),
                              'depth': nmea.value(6),
                              'altitude': nmea.value(7),
                              'heading': nmea.value(8),
                              'velforw': nmea.value(9),
                              'velport': nmea.value(10),
                              'velup': nmea.value(11)}

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
