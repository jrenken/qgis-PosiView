'''
Created on 04.06.2015

@author: jrenken
'''
from qgis.PyQt.QtCore import QObject, pyqtSlot, pyqtSignal


class DataDevice(QObject):
    '''
    Baseclass for all data devices
    '''

    readyRead = pyqtSignal()
    deviceConnected = pyqtSignal(bool)
    deviceDisconnected = pyqtSignal(bool)

    def __init__(self, params={}, parent=None):
        '''
        Constructor
        '''
        super(DataDevice, self).__init__(parent)
        self.buffered = False

    def readData(self):
        return ''

    def readLine(self):
        return ''

    def connectDevice(self):
        pass

    def disconnectDevice(self):
        pass

    @pyqtSlot()
    def onReconnectTimer(self):
        self.connectDevice()
