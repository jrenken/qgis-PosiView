'''
Created on 03.06.2015

@author: jrenken
'''

        
class NmeaRecord:
    '''Handle NMEA Records'''
    
    def __init__(self, data = None):
        self.valid = True
        if (data is None):
            self.fields = []
        else:
            s = data.strip()
            if s[-3] == '*':
                chs = 0
                for i in range(1, len(s) - 3):
                    chs ^= ord(s[i])
                if chs != int(s[-2:], 16):
                    self.valid = False
                s = s[:-3]
            self.fields = s.split(',')

    def __str__(self):
        return self.sentence(True)
        
    def sentence(self, cs=False):
        s = ",".join(self.fields)
        if cs:
            chs = 0;
            for i in range(1, len(s)):
                chs ^= ord(s[i])
            s += "*%02x" % chs
        return s + "\r\n"

    def __getitem__(self, key):
        if key < len(self.fields):
            return self.fields[key]
        return ""
    
    def __setitem__(self, key, value):
        if key < len(self.fields):
            self.fields[key] = format(value)
        else:
            self.fields.extend([''] * (key - len(self.fields)))
            self.fields.append(format(value))

    def fromDDM(self, val, hem=0):
        try:
            dot = self.fields[val].index('.')
            deg = float(self.fields[val][0:(dot - 2)])
            minute = float(self.fields[val][(dot - 2):])
            deg = deg + minute / 60.0
            if (hem > 0):
                if self.fields[hem] == 'S' or self.fields[hem] == 'W':
                    deg *= -1
            return deg
        except:
            return 0.0
