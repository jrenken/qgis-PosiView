'''
Created on 22.06.2015

@author: jrenken
'''
from __future__ import absolute_import

from datetime import datetime, timezone
from .nmea import NmeaRecord
from .parser import Parser


class PmtmParser(Parser):
    '''
    Parser for propritary Sentences by Marum Marine Technology
    Sentences:
    Geographical position:     $PMTMGPO,<sender>,<date>,<time>,<Latitude>,<Longitude>,<position_source>,
                                <depth>,<altitude>,<heading>*<checksum>
                               $PMTMGPO,HROV,020718,092343.92,-53.1234567,-152.1234567,P,0234.5,018.2,270*3B\r\n
    Attitude:                  $PMTMATT,<sender>,<pitch>,<roll>,<heading>*<checksum>
                               $PMTMATT,HROV,1.2,3.5,273.4*6F
    Speed:                     $PMTMSPD,HROV,<forward_speed><port_speed><up_speed>
                               $PMMTSPD,HROV,0.4,0.6,0.3*6F
    '''
    def __init__(self):
        '''
        Constructor
        '''
        super(PmtmParser, self).__init__()

    def parse(self, data):
        data_id = data[5:8]
        if data_id == 'GPO':
            return self.decodeGpo(data)
        elif data_id == 'ATT':
            return self.decodeAtt(data)
        elif data_id == 'SPD':
            return self.decodeSpd(data)

    def decodeGpo(self, data):
        nmea = NmeaRecord(data)
        if nmea.valid:
            try:
                result = {'id': nmea[1],
                          'lat': nmea.value(4),
                          'lon': nmea.value(5),
                          'depth': nmea.value(7),
                          'altitude': nmea.value(8),
                          'heading': nmea.value(9, 0.0),
                          'source': nmea[6]}
                try:
                    year = int(nmea[2][-2:]) + 2000
                    dt = datetime(year, int(nmea[2][-4:-2]),
                                  int(nmea[2][:-4]),
                                  int(nmea[3][0:2]), int(nmea[3][2:4]),
                                  int(nmea[3][4:6]), tzinfo=timezone.utc)
                except ValueError:
                    dt = datetime.now(tz=timezone.utc)
                result['time'] = (dt - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds()
                return dict((k, v) for k, v in result.items() if v is not None)
            except ValueError:
                return {}

    def decodeAtt(self, data):
        nmea = NmeaRecord(data)
        if nmea.valid:
            try:
                result = {'id': nmea[1],
                          'roll': nmea.value(2),
                          'pitch': nmea.value(3),
                          'heading': nmea.value(4)}
                return dict((k, v) for k, v in result.items() if v is not None)
            except ValueError:
                return {}

    def decodeSpd(self, data):
        nmea = NmeaRecord(data)
        if nmea.valid:
            try:
                result = {'id': nmea[1],
                          'velforw': nmea.value(2),
                          'velport': nmea.value(3),
                          'velup': nmea.value(4)}
                return dict((k, v) for k, v in result.items() if v is not None)
            except ValueError:
                return {}
