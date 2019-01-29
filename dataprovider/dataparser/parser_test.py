'''
Created on Jan 28, 2019

@author: jrenken
'''
from __future__ import absolute_import

from .parser import Parser
from datetime import datetime


class TestParser(Parser):
    '''
    Sentence parser for custom protocol
    
    '''

    def __init__(self):
        super(TestParser, self).__init__()

    def parse(self, data):
        try:
            fields = data.split(',')
            dt = datetime.utcnow()
            
            return { 'id':fields[0], 'lat': float(fields[1]), 'lon':float(fields[2]),
                     'time': (dt - datetime(1970,1,1,0,0,0)).total_seconds() }
        except ValueError:
            return {}