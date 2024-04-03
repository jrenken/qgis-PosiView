'''
Created on Apr 3, 2024

@author: jrenken
'''

from .datadevice import DataDevice
from qgis.PyQt.QtNetwork import QTcpServer, QHostAddress, QTcpSocket, QAbstractSocket
from qgis.PyQt.QtCore import pyqtSlot, QTimer
from PyQt5.Qt import QTcpSocket


class TcpServerDevice(DataDevice):
    '''
    Provides a TCP server socket.
    Only one client connection is allowed per time.
    The connection is single threaded. It requires that the client closes the connection.
    '''


    def __init__(self, params={}, parent=None):
        '''
        Constructor
        '''
        super(TcpServerDevice, self).__init__(params, parent)

        self.server = QTcpServer(self)
        self.server.setMaxPendingConnections(1)
        self.server.newConnection.connect(self.acceptConnection)
        self.reconnect = int(params.get('Reconnect', 3000))
        self.address = QHostAddress(params.get('Host', 'any'))
        self.port = int(params.get('Port', 2000))
        self.client = QTcpSocket(self)  # dummy socket

    def acceptConnection(self):
        if self.server.hasPendingConnections():
            self.client = self.server.nextPendingConnection()
            self.client.readyRead.connect(self.readyRead)
            self.client.errorOccurred.connect(self.socketError)
            self.socketConnected()
            self.client.disconnected.connect(self.socketDisconnected)

    @pyqtSlot(QAbstractSocket.SocketError)
    def socketError(self, error):
        pass

    def connectDevice(self):
        if not self.server.listen(self.address, self.port):
            if self.reconnect > 0:
                QTimer.singleShot(self.reconnect, self.onReconnectTimer)

    def disconnectDevice(self):
        if self.client.state() == QAbstractSocket.ConnectedState:
            self.client.disconnectFromHost()
            self.client.close()
        self.server.close()

    def readData(self):
        size = self.client.bytesAvailable()
        if size:
            data = self.client.read(size)
            try:
                return data.decode()
            except UnicodeDecodeError:
                return '<decode error>'
        return ''

    def readLine(self):
        if self.client.canReadLine():
            try:
                return self.client.readLine().data().decode()
            except UnicodeDecodeError:
                return '<decode error>'
        return ''

    @pyqtSlot()
    def socketConnected(self):
        self.deviceConnected.emit(True)

    @pyqtSlot()
    def socketDisconnected(self):
        self.deviceDisconnected.emit(True)
