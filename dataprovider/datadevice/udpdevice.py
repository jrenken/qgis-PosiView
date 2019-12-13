'''
Created on 04.06.2015

@author: jrenken
'''
from .datadevice import DataDevice
from qgis.PyQt.QtNetwork import QUdpSocket, QHostAddress, QAbstractSocket
from qgis.PyQt.QtCore import pyqtSignal, QTimer


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
        self.reuse = bool(params.get('ReuseAddr', False))
        self.iodevice.readyRead.connect(self.readyRead)
        self.buffer = bytearray()

    def connectDevice(self):
        result = False
        if self.host is None:
            result = self.iodevice.bind(self.port)
        else:
            ha = QHostAddress(self.host)
            if self.reuse:
                result = self.iodevice.bind(ha, self.port, QAbstractSocket.ReuseAddressHint)
            else:
                result = self.iodevice.bind(ha, self.port)
        if result is False:
            if self.reconnect > 0:
                QTimer.singleShot(self.reconnect, self.onReconnectTimer)
        else:
            self.deviceConnected.emit(True)

    def disconnectDevice(self):
        if self.iodevice.state() is QAbstractSocket.BoundState:
            self.iodevice.disconnectFromHost()
            self.deviceDisconnected.emit(True)

    def readData(self):
        (data, ha, port) = self.iodevice.readDatagram(self.iodevice.pendingDatagramSize())
        self.remoteHost = ha.toString()
        self.remotePort = port
        return data

    def readLine(self):
        if self.iodevice.hasPendingDatagrams():
            self.buffer.extend(self.readData())
        try:
            i = self.buffer.index(b'\n')
            data = self.buffer[0:i]
            del self.buffer[0:i + 1]
            return data.decode()
        except UnicodeDecodeError:
            return '<decode error>'
        except ValueError:
            return ''
