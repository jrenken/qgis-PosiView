'''
Created on Jan 28, 2019

@author: jrenken
'''

from datetime import datetime, timezone
from .parser import Parser


class TargetPosParser(Parser):
    '''
    Sentence parser for simple text protocol
    <target>,<lat>,<lon>[,<depth>,<altitude>,<heading>]\r\n
    '''

    def parse(self, data):
        try:
            fields = data.split(',')
            dt = datetime.now(tz=timezone.utc)
            result = {'id': fields[0], 'lat': float(fields[1]), 'lon': float(fields[2]),
                      'time': dt.timestamp()}
            if len(fields) > 3:
                result['depth'] = self.getOptValue(fields, 3)
                result['altitude'] = self.getOptValue(fields, 4)
                result['heading'] = self.getOptValue(fields, 5)
                return dict((k, v) for k, v in result.items() if v is not None)
            return result
        except ValueError:
            return {}

    def getOptValue(self, fields, idx):
        try:
            return float(fields[idx])
        except (IndexError, ValueError):
            return None
