'''
Created on 03.07.2015

@author: jrenken
'''
from .datadevice import DataDevice
from PyQt4.QtNetwork import QTcpSocket, QAbstractSocket
from PyQt4.QtCore import pyqtSlot, QTimer

class TcpDevice(DataDevice):
    '''
    classdocs
    '''


    def __init__(self, params={}, parent=None):
        '''
        Constructor
        '''
        super(TcpDevice, self).__init__(params, parent)
        
        self.iodevice = QTcpSocket()
        self.reconnect = int(params.get('Reconnect', 1000))
        self.host = params.get('Host', None)
        self.port = int(params.get('Port', 2000))
        self.gpsdInit = bool(params.get('GpsdInit', False))
        self.iodevice.readyRead.connect(self.readyRead)
        self.iodevice.error.connect(self.socketError)
        self.iodevice.connected.connect(self.socketConnected)
        self.iodevice.disconnected.connect(self.socketDisconnected)


    @pyqtSlot(QAbstractSocket.SocketError)
    def socketError(self, error):
        if self.iodevice.state() != QAbstractSocket.BoundState:
            if self.reconnect > 0:
                QTimer.singleShot(self.reconnect, self.onReconnectTimer)
 

    def connectDevice(self):
        self.iodevice.connectToHost(self.host, self.port)
            
    def disconnectDevice(self):
        if self.iodevice.state() is QAbstractSocket.ConnectedState:
            self.iodevice.disconnectFromHost()

    def readData(self):
        size = self.iodevice.bytesAvailable()
        data = self.iodevice.read(size)
        return data
    
    @pyqtSlot()
    def socketConnected(self):
        self.deviceConnected.emit(True)
        if self.gpsdInit:
            self.iodevice.writeData('?WATCH={"class":"WATCH","nmea":true}')
        
    @pyqtSlot()
    def socketDisconnected(self):
        self.deviceDisconnected.emit(True)

    