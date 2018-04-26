'''
Created on 03.06.2015

@author: jrenken
'''
from __future__ import absolute_import

import datetime
from .nmea import NmeaRecord
from .parser import Parser


class PiseParser(Parser):
    '''
    $PISE,AUV,<Latitude>,<Longitude>,<date>,<time>,<position_source>,
                <false>,<heading>,<depth>,<speed>*<checksum>
    '''
    def __init__(self):
        super(PiseParser, self).__init__()

    def parse(self, data):
        if data.startswith('$PISE'):
            nmea = NmeaRecord(data)
            if nmea.valid:
                try:
                    result = {'id': nmea[1],
                              'lat': nmea.value(2),
                              'lon': nmea.value(3),
                              'heading': nmea.value(8),
                              'depth': nmea.value(9),
                              'speed': nmea.value(10)}
                    try:
                        dt = datetime.datetime(int(nmea[4][0:4]), int(nmea[4][4:6]),
                                           int(nmea[4][6:]),
                                           int(nmea[5][0:2]), int(nmea[5][2:4]),
                                           int(nmea[5][4:6]))
                    except ValueError:
                        dt = datetime.datetime.utcnow()
                    td = dt - datetime.datetime(1970, 1, 1)
                    result['time'] = td.total_seconds()
                    return dict((k, v) for k, v in result.items() if v is not None)
                except ValueError:
                    return {}
