'''
Created on 03.06.2015

@author: jrenken
'''
from PyQt4.Qt import QObject
import dataparser
from PyQt4.QtCore import pyqtSignal, pyqtSlot
import datadevice
from collections import deque

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
        self.dataDevice = None
        self.keepConnection = True
        self.parser = dataparser.createParser( self.params.setdefault('Parser', 'IxUsbl') )
        self.dataDevice = None
        self.lineBuffer = deque()
     
    def properties(self):
        return self.params

    
    def connectDevice(self):
        self.dataDevice = datadevice.createDataDevice(self.params)
        if self.dataDevice is not None:
            pass
    
    def disconnectDevice(self):
        pass
    
    @pyqtSlot()
    def onDataAvailable(self):
        data = self.dataDevice.readData()
        self.lineBuffer.extend(data.splitlines())
        for s in self.lineBuffer:
            d = self.parser.parse(s)
            if d:
                d['name'] = self.name
                self.newDataReceived.emit( d )
            
