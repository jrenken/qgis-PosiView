'''
Created on 31.07.2015

@author: jrenken
'''
from parser import Parser
from nmea import NmeaRecord

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
                    result = {'depth':  float(nmea[1]),
                              'altitude': float(nmea[2]), 
                              'heading': float(nmea[3]),
                              'pitch': float(nmea[5]), 
                              'roll': float(nmea[6])}
                    return result
                except ValueError:
                    return {}
