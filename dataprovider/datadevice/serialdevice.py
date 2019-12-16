'''
Created on Dec 13, 2019

@author: jrenken
'''

from .datadevice import DataDevice
from qgis.PyQt.QtCore import QObject, QTimer, QIODevice, pyqtSlot, pyqtSignal
from PyQt5.QtSerialPort import QSerialPort


class SerialDevice(DataDevice):
    '''
    Implementation of a Serial Device
    Requires PyQt5 QtSerialPort module
    '''

    readyRead = pyqtSignal()

    def __init__(self, params={}, parent=None):
        '''
        Constructor
        '''
        super(SerialDevice, self).__init__(params, parent)
        self.iodevice = QSerialPort()
        self.reconnect = int(params.get('Reconnect', 1000))
        self.serialPort = params.get('SerialPort', None)
        self.baudrate = int(params.get('Baudrate', QSerialPort.Baud9600))
        self.databits = int(params.get('Databits', QSerialPort.Data8))
        self.parity = int(params.get('Parity', QSerialPort.NoParity))
        self.stopbits = int(params.get('Stopbits', QSerialPort.OneStop))
        self.flowControl = int(params.get('FlowControl', QSerialPort.NoFlowControl))
        self.iodevice.readyRead.connect(self.readyRead)
        self.buffer = bytearray()

    def connectDevice(self):
        if not self.serialPort:
            return
        self.iodevice.setPortName(self.serialPort)
        self.iodevice.setBaudRate(self.baudrate)
        self.iodevice.setDataBits(self.databits)
        self.iodevice.setParity(self.parity)
        self.iodevice.setStopBits(self.stopbits)
        self.iodevice.setFlowControl(self.flowControl)
        if not self.iodevice.open(QIODevice.ReadOnly):
            if self.reconnect > 0:
                QTimer.singleShot(self.reconnect, self.onReconnectTimer)
        else:
            self.deviceConnected.emit(True)

    def disconnectDevice(self):
        self.iodevice.close()
        self.deviceDisconnected.emit(True)

    def readData(self):
        size = self.iodevice.bytesAvailable()
        if size:
            data = self.iodevice.read(size)
            try:
                return data.decode()
            except UnicodeDecodeError:
                return '<decode error>'
        return ''

    def readLine(self):
        if self.iodevice.canReadLine():
            try:
                return self.iodevice.readLine().data().decode()
            except UnicodeDecodeError:
                return '<decode error>'
        return ''
