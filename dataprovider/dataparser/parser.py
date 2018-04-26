'''
Created on 03.06.2015

@author: jrenken
'''
from builtins import object


class Parser(object):
    '''
    Base class for sentence parser
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.hasPosition = False
        self.hasAttitude = False
        self.id = None
        self.state = {}

    def parse(self, data):
        return {}
