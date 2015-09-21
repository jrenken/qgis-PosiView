'''
Created on 06.07.2015

@author: jrenken
'''

import datetime
from nmea import NmeaRecord
from parser import Parser


class PsonlldParser(Parser):
    '''
    Parser for the PSONLLD sentences provided by Sonardyne USBL system Ranger2
    $PSONLLD,153005.253,24,A,50.02495,8.873323,425.3,,,,,,,,*3e<CR><LF>
    '''

    def __init__(self):
        '''
        constructor only calls the parents class constructor
        '''
        super(PsonlldParser, self).__init__()

    def parse(self, data):
        if data.startswith('$PSONLLD'):
            nmea = NmeaRecord(data)
            if (nmea.valid):
                try:
                    if nmea[3] == 'V':
                        return {}
                    result = {'id': int(nmea[2]), 'lat': float(nmea[4]),
                              'lon': float(nmea[5]), 'depth': float(nmea[6])}
                    t = datetime.date.today()
                    dt = datetime.datetime(t.year, t.month, t.day,
                                        int(nmea[1][0:2]), int(nmea[1][2:4]),
                                        int(nmea[1][4:6]), int(nmea[1][7:]) * 100)
                    td = dt - datetime.datetime(1970, 1, 1)
                    result['time'] = td.total_seconds()
                    return result
                except ValueError:
                    return {}
