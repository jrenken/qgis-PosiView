'''
Created on 04.06.2015

@author: jrenken
'''
from .datadevice import DataDevice
from PyQt4.QtNetwork import QUdpSocket, QHostAddress, QAbstractSocket
from PyQt4.QtCore import pyqtSignal, QTimer


class UdpDevice(DataDevice):
    '''
    Implementation of a UDP server socket
    '''

    readyRead = pyqtSignal()

    def __init__(self, params={}, parent=None):
        '''
        Constructor
        '''
        super(UdpDevice, self).__init__(params, parent)
        
        self.iodevice = QUdpSocket()
        self.reconnect = int(params.get('Reconnect', 1000))
        self.host = params.get('Host', None)
        self.port = int(params.get('Port', 2000))
        self.iodevice.readyRead.connect(self.readyRead)

    def connectDevice(self):
        print "Hey, try to connect ", self.host, self.port
        result = False
        if self.host is None:
            print "Connect"
            result = self.iodevice.bind(self.port)
        else:        
            ha = QHostAddress(self.host)
            result = self.iodevice.bind(ha, self.port)  
        print "Device connected?: ", result
        if result is False:
            if self.reconnect > 0:
                QTimer.singleShot(self.reconnect, self.onReconnectTimer)
        else:
            self.deviceConnected.emit() 
            
    def disconnectDevice(self):
        if self.iodevice.state() is QAbstractSocket.BoundState:
            self.iodevice.disconnectFromHost()
            self.deviceDisconnected.emit()

    def readData(self):
        (data, ha, port) = self.iodevice.readDatagram(self.iodevice.pendingDatagramSize())
        self.remoteHost = ha.toString()
        self.remotePort = port 
        return data
    
    
        
        