'''
Created on 31.07.2015

@author: jrenken
'''
from __future__ import absolute_import
from .parser import Parser
from .nmea import NmeaRecord


class CP16Parser(Parser):
    '''
    Parser for CP-16 compass NMEA sentences
    $PCI,<depth meter>,<depth feet>,<heading>,<CP data>,<pitch>,<roll><CR><LF>
    '''

    def __init__(self):
        '''
        Constructor does nothing
        '''
        super(CP16Parser, self).__init__()

    def parse(self, data):
        if data.startswith('$PCI'):
            nmea = NmeaRecord(data)
            if nmea.valid:
                try:
                    result = {'depth': nmea.value(1),
                              'heading': nmea.value(3),
                              'pitch': nmea.value(5),
                              'roll': nmea.value(6)}
                    return dict((k, v) for k, v in result.items() if v is not None)
                except ValueError:
                    return {}
