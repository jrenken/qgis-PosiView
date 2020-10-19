'''
Created on 09.10.2020

@author: jrenken
'''
from __future__ import absolute_import
from .parser import Parser
from .nmea import NmeaRecord
import re


class CompassParser(Parser):
    '''
    Parser for electronic compass data output in standard $C-format or NMEA-183
    $C320.5P0.2R-18.3...
    '''

    def __init__(self):
        '''
        Constructor does nothing
        '''
        super(CompassParser, self).__init__()
        self.pat = re.compile(r'([CPR])([\+\-\d.]+)')

    def parse(self, data):
        if data.startswith('$C'):
            return self.decodeStandardCompassFrame(data)
        else:
            data_id = data[3:6]
            if data_id in ('HDT', 'HDM'):
                return self.decodeHeading(data)

    def decodeStandardCompassFrame(self, data):
        try:
            flds = dict(self.pat.findall(data))
            try:
                result = {'heading': float(flds['C']),
                          'pitch': float(flds['P']),
                          'roll': float(flds['R'])}
                return result
            except (KeyError, ValueError):
                return {}
        except IndexError:
            return {}

    def decodeHeading(self, data):
        nmea = NmeaRecord(data)
        if (nmea.valid):
            h = nmea.value(1)
            if h is not None:
                return {'heading': h, 'id': nmea[0][1:3], 'type': 'true' if nmea[2] == 'T' else 'magnetic'}
        return {}
