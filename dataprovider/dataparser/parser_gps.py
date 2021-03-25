'''
Created on 03.07.2015

@author: jrenken
'''
from __future__ import absolute_import

from datetime import datetime, timezone
from .nmea import NmeaRecord
from .parser import Parser


class GpsParser(Parser):
    '''
    $GPRMC,140808,A,5301.4970,N,00852.1740,E,000.0,000.0,030715,0.4,E,N*15
    $GPGLL,3836.1382,N,01712.6234,E,185000.00,A,D*60
    $GPGGA,075222.00,3727.35636,N,01509.01712,E,1,07,1.8,17.35,M,40.17,M,,*5C
    '''

    def __init__(self):
        '''
        Constructor
        '''
        super(GpsParser, self).__init__()

    def parse(self, data):
        data_id = data[3:6]
        if data_id == 'RMC':
            return self.decodeRmc(data)
        elif data_id == 'VTG':
            return self.decodeVtg(data)
        elif data_id == 'GLL':
            return self.decodeGll(data)
        elif data_id == 'GGA':
            return self.decodeGga(data)
        elif data_id == 'HDT':
            return self.decodeHdt(data)

    def decodeRmc(self, data):
        nmea = NmeaRecord(data)
        if nmea.valid:
            try:
                result = {'lat': nmea.fromDDM(3, 4),
                          'lon': nmea.fromDDM(5, 6),
                          'course': nmea.value(8),
                          'id': nmea[0][1:3]}
                try:
                    dt = datetime.now(tz=timezone.utc).replace(hour=int(nmea[1][0:2]),
                                        minute=int(nmea[1][2:4]), second=int(nmea[1][4:6]))
                except ValueError:
                    dt = datetime.now(tz=timezone.utc)
                result['time'] = (dt - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds()
                return dict((k, v) for k, v in result.items() if v is not None)
            except ValueError:
                return {}

    def decodeGll(self, data):
        nmea = NmeaRecord(data)
        if nmea.valid:
            try:
                result = {'lat': nmea.fromDDM(1, 2),
                          'lon': nmea.fromDDM(3, 4),
                          'id': nmea[0][1:3]}
                try:
                    dt = datetime.now(timezone.utc).replace(hour=int(nmea[5][0:2]),
                                        minute=int(nmea[5][2:4]), second=int(nmea[5][4:6]))
                except ValueError:
                    dt = datetime.now(timezone.utc)
                result['time'] = (dt - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds()
                return dict((k, v) for k, v in result.items() if v is not None)
            except ValueError:
                return {}

    def decodeGga(self, data):
        nmea = NmeaRecord(data)
        if nmea.valid:
            try:
                result = {'lat': nmea.fromDDM(2, 3),
                          'lon': nmea.fromDDM(4, 5),
                          'depth': nmea.value(9),
                          'id': nmea[0][1:3]}
                if result['depth']:
                    result['depth'] = -result['depth']
                try:
                    dt = datetime.now(timezone.utc).replace(hour=int(nmea[1][0:2]),
                                        minute=int(nmea[1][2:4]), second=int(nmea[1][4:6]))
                except ValueError:
                    dt = datetime.now(timezone.utc)
                result['time'] = (dt - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds()
                return dict((k, v) for k, v in result.items() if v is not None)
            except ValueError:
                return {}

    def decodeVtg(self, data):
        nmea = NmeaRecord(data)
        if (nmea.valid):
            h = nmea.value(1)
            if h is not None:
                return {'course': h, 'id': nmea[0][1:3]}
        return {}

    def decodeHdt(self, data):
        nmea = NmeaRecord(data)
        if (nmea.valid):
            h = nmea.value(1)
            if h is not None:
                return {'heading': h, 'id': nmea[0][1:3]}
        return {}
