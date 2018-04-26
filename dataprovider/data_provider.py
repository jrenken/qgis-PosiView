'''
Created on 03.06.2015

@author: jrenken
'''
from __future__ import absolute_import
from builtins import str
from qgis.PyQt.Qt import QObject
from qgis.PyQt.QtCore import pyqtSignal, pyqtSlot
from . import dataparser
from . import datadevice


class DataProvider(QObject):
    '''
    Base class for all data provider
    '''

    newDataReceived = pyqtSignal(dict)
    newRawDataReceived = pyqtSignal(str)
    deviceConnected = pyqtSignal(bool)
    deviceDisconnected = pyqtSignal(bool)

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

    def properties(self):
        return self.params

    def start(self):
        self.connectDevice()

    def stop(self):
        self.disconnectDevice()

    def connectDevice(self):
        self.dataDevice = datadevice.createDataDevice(self.params)
        self.dataDevice.deviceConnected.connect(self.deviceConnected)
        self.dataDevice.deviceDisconnected.connect(self.deviceDisconnected)
        if self.dataDevice is not None:
            self.dataDevice.readyRead.connect(self.onDataAvailable)
            self.dataDevice.connectDevice()

    def disconnectDevice(self):
        if self.dataDevice is not None:
            self.dataDevice.disconnectDevice()
            self.dataDevice.readyRead.disconnect()
            self.dataDevice = None
            self.deviceDisconnected.emit(True)

    @pyqtSlot()
    def onDataAvailable(self):
        while True:
            line = self.dataDevice.readLine()
            if line:
                self.newRawDataReceived.emit(line)
                d = self.parser.parse(line)
                if d:
                    d['name'] = self.name
                    self.newDataReceived.emit(d)
            else:
                break
