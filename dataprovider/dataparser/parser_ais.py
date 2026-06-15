'''
Created on 25.04.2016

@author: jrenken
'''

from datetime import datetime, timezone
from .parser import Parser
from .nmea import NmeaRecord


class AisParser(Parser):
    '''
    Parser for AIS Position Report Class A and B
    Type 1, 2 and 3 messages share a common reporting structure
    '''

    def __init__(self):
        '''
        Constructor
        '''
        super().__init__()
        self.binaryPayload = ''
        self.fragment = 0
        self.fragmentcount = 0

    def parse(self, data):
        try:
            data = data[data.index('!'):]
            if not data[3:6] in ('VDM', 'VDO'):
                return {}
        except ValueError:
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
        binPayload = BitVector(payload)

        try:
            mmsi = binPayload.getInt(8, 30)
            rtype = binPayload.getInt(0, 6)
            if rtype in (1, 2, 3):
                bs = {'lat': (89, 27, True), 'lon': (61, 28, True),
                      'ts': (137, 6, False), 'head': (128, 9, False), 'cog': (116, 12, False),
                      'speed': (50, 10, False)}
            elif rtype in (18, 19):
                bs = {'lat': (85, 27, True), 'lon': (57, 28, True),
                      'ts': (133, 6, False), 'head': (124, 9, False), 'cog': (112, 12, False),
                      'speed': (46, 10, False)}
            else:
                return {}

            result = {'id': mmsi,
                      'type': rtype,
                      'lat': float(binPayload.getInt(*bs['lat'])) / 600000.0,
                      'lon': float(binPayload.getInt(*bs['lon'])) / 600000.0,
                      'depth': 0.0,
                      'speed': float(binPayload.getInt(*bs['speed'])) * 0.0514444}
            sec = binPayload.getInt(*bs['ts'])
            dt = datetime.now(tz=timezone.utc)
            if sec < 60:
                dt.replace(second=sec)
            result['time'] = dt.timestamp()
            head = binPayload.getInt(*bs['head'])
            if head == 511:
                head = 0.1 * float(binPayload.getInt(*bs['cog']))
                result['course'] = head
            else:
                result['heading'] = head
            return dict((k, v) for k, v in result.items() if v is not None)
        except (ValueError, KeyError, IndexError):
            pass
        return {}


class BitVector():
    '''
    Helper class for handling AIS binary payload data
    '''

    SIX_BIT_CHARS = "@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_ !\"#$%&'()*+,-./0123456789:;<=>?"

    def __init__(self, val=0, size=0):
        '''
        constructor
        :param val: either an integer or a 6bit encoded string
        :type val: integer, long or string
        :param size: number of bit contained in val if val is int or long
        :type size: int
        '''
        self.vector = []
        if isinstance(val, str):
            for c in val:
                self.append6Bit(c)
        elif type(val) in (int, int) and size:
            self.extend(val, size)

    def extend(self, val, size):
        if size > 0:
            snippet = [(val >> i) & 1 for i in range(size - 1, -1, -1)]
            self.vector.extend(snippet)

    def append6Bit(self, ch):
        ''' return s the 6 bit binary value of a hex decoded bit field as used in AIS sentences
        :param ch: character
        :type ch: unsigned char
        :return 6 bit value
        '''
        res = ord(ch) - 48
        if res > 40:
            res -= 8
        self.extend(res, 6)

    def __len__(self):
        return len(self.vector)

    def __str__(self):
        return str(self.vector)

    def __repr__(self):
        return str(self.vector)

    def getInt(self, start, size, signed=False):
        '''
        get integer value from a slice
        :param start: index of first bit in vector
        :type start: int
        :param size: size of subvector
        :type size; int
        :param signed: true if result is a signe int
        :type signed: bool
        :return the int value
        '''
        if start > len(self.vector):
            return 0

        if start + size > len(self.vector):
            size = len(self.vector) - start

        mask = 1 << size
        if self.vector[start] and signed:
            result = -1
        else:
            result = mask - 1
        for i in range(start, start + size):
            mask >>= 1
            if not self.vector[i]:
                result &= ~mask
        return result

    def getText(self, start, size, bpc=6) -> str:
        '''
        get text from a slice. Uses the 6bit decoding.

        :param start: start bit number
        :type start: int
        :param size: number of characters
        :type size: int
        :param bpc: true if result is a signe int
        :type signed: bool
        :return the int value
        '''
        result = ''
        for st in range(start, size * bpc, bpc):
            c = self.getInt(st, bpc)
            if c < 64:
                result += self.SIX_BIT_CHARS[c]
            else:
                result += chr(c)
        return result


if __name__ == "__main__":
    p = AisParser()
    # fix_print_with_import
    print(p.parse('!AIVDM,1,1,,A,139cJd>P1IPWunbNI:nsdOvrRHAH,0*24'))
