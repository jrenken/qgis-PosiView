'''
Created on 25.04.2016

@author: jrenken
'''

import datetime
from parser import Parser
from nmea import NmeaRecord


class AisParser(Parser):
    '''
    Parser for AIS Position Report Class A
    Type 1, 2 and 3 messages share a common reporting structure

    !AIVDM,1,1,,A,139Qfu`P000WtshNI2u@0Ow20HD4,0*55
    '''

    def __init__(self):
        '''
        Constructor
        '''
        super(AisParser, self).__init__()
        self.binaryPayload = ''
        self.fragment = 0
        self.fragmentcount = 0

    def parse(self, data):
        if not data.startswith('!AIVDM'):
            return {}
        nmea = NmeaRecord(data)
        if nmea.valid:
            fcnt = nmea.value(1)
            frag = nmea.value(2)

            if frag == 1:
                self.binaryPayload = nmea[5]
            else:
                self.binaryPayload += nmea[5]

            if frag == fcnt:
                return self.decodePayload(self.binaryPayload)
            return {}

    def decodePayload(self, payload):
        binPayload = BitVector()
        for c in payload:
            val = self.get6Bit(c)
            binPayload.extend(val, 6)
        try:
            mmsi = binPayload.getInt(8, 30)
            type = binPayload.getInt(0,6)
            sec = 0
            head = 0
            result = {'id': mmsi,
                      'depth': 0.0}
            if type in (1, 2, 3):
                result['lat'] = float(binPayload.getInt(89, 27)) / 600000.0
                result['lon'] = float(binPayload.getInt(61, 28)) / 600000.0
                sec = binPayload.getInt(137, 6)
                head = binPayload.getInt(128, 9)
                if head == 511:
                    head = 0.1 * float(binPayload.getInt(116, 12))
            elif type == 18:
                result['lat'] = float(binPayload.getInt(85, 27)) / 600000.0
                result['lon'] = float(binPayload.getInt(57, 28)) / 600000.0
                sec = binPayload.getInt(133, 6)
                head = binPayload.getInt(124, 9)
                if head == 511:
                    head = 0.1 * float(binPayload.getInt(112, 12))
            dt = datetime.datetime.utcnow()
            if sec < 60:
                dt.replace(second=sec)
            result['time'] = (dt - datetime.datetime(1970, 1, 1)).total_seconds()
            result['heading'] = head
            return dict((k, v) for k, v in result.iteritems() if v is not None)
        except (ValueError, KeyError):
            print 'AIS exception'
            return {}

    def get6Bit(self, ch):
        res = ord(ch) - 48
        if res > 40:
            res -= 8
        return res


class BitVector:
    '''
    Helper class for handling AIS binary payload data
    '''

    def __init__(self, val=0, size=0):
        '''
        constructor
        '''
        self.vector = []
        if size:
            self.extend(val, size)

    def extend(self, val, size):
        if size:
            if size > 32:
                raise ValueError('Too many bits. Maximum is 32')
            fmt = '{0:0%ib}' % size
            l = list(map(int, fmt.format(val)))
            self.vector.extend(l)

    def __len__(self):
        return len(self.vector)

    def __str__(self):
        return str(self.vector)

    def getInt(self, start, size):
        'get integer value from a slice'
        if size > 32:
            raise ValueError("Maximum size is 32 bit")
        if start + size > len(self.vector):
            raise KeyError("Size extends vector size")
        result = int()
        mask = int(1) << size
        for i in range(start, start + size):
            mask >>= 1
            if self.vector[i]:
                result |= mask
        return result

if __name__ == "__main__":
    p = AisParser()
    print p.parse('!AIVDM,1,1,,A,139cJd>P1IPWunbNI:nsdOvrRHAH,0*24')
