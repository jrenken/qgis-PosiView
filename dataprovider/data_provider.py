'''
Created on 03.06.2015

@author: jrenken
'''
from PyQt4.Qt import QObject
import dataparser
from PyQt4.QtCore import pyqtSignal


class DataProvider(QObject):
    '''
    Base class for all data provider
    '''
    
    newDataReceived = pyqtSignal([dict])
    deviceConnected = pyqtSignal()
    deviceDisconnected = pyqtSignal()

    dataProviderCount = 0

    def __init__(self, params = {}, parent = None):
        '''
        Constructor
        '''
        DataProvider.dataProviderCount += 1
        self.name = params.setdefault('Name', 'DataProvider_' + str(DataProvider.dataProviderCount))
        self.params = params
        self.connected = False
        self.iodevice = None
        self.keepConnection = True
        self.parser = dataparser.createParser( self.params.setdefault('Parser', 'IxUsbl') )
        
     
    def properties(self):
        return self.params


