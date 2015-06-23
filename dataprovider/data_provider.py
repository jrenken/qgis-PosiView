'''
Created on 03.06.2015

@author: jrenken
'''
from PyQt4.Qt import QObject
from PyQt4.QtCore import pyqtSignal, pyqtSlot
import dataparser
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

    def __init__(self, params={}, parent=None):
        '''
        Constructor
        '''
        super(DataProvider, self).__init__(parent)
        DataProvider.dataProviderCount += 1
        self.name = params.setdefault('Name', 'DataProvider_' + str(DataProvider.dataProviderCount))
        self.params = params
        self.connected = False
        self.dataDevice = None
        self.keepConnection = True
        self.parser = dataparser.createParser(self.params.setdefault('Parser', 'IX_USBL'))
        self.dataDevice = None
        self.lineBuffer = deque()
             
    def properties(self):
        return self.params

    def start(self):
        self.connectDevice()
        
    def stop(self):
        self.disconnectDevice()
    
    def connectDevice(self):
        self.dataDevice = datadevice.createDataDevice(self.params)
        if self.dataDevice is not None:
            self.dataDevice.readyRead.connect(self.onDataAvailable)
            self.dataDevice.connectDevice()
    
    def disconnectDevice(self):
        if self.dataDevice is not None:
            self.dataDevice.disconnectDevice()
            self.dataDevice.readyRead.disconnect()
#             self.dataDevice.deleteLater()
#             del self.dataDevice
            self.dataDevice = None
    
    @pyqtSlot()
    def onDataAvailable(self):
        data = self.dataDevice.readData()
        self.lineBuffer.extend(data.splitlines())
        while len(self.lineBuffer):
            d = self.parser.parse(self.lineBuffer.popleft())
            if d:
                d['name'] = self.name
                self.newDataReceived.emit(d)
            
