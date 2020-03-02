'''
Created on 13.07.2015

@author: jrenken
'''
from qgis.PyQt.QtCore import QObject, QTimer, pyqtSlot, pyqtSignal
import os
from datetime import datetime, timezone


class Recorder(QObject):
    '''
    classdocs
    '''

    recordingStarted = pyqtSignal(str, bool)

    def __init__(self, path, interval=1000, maxLines=10000, parent=None):
        '''
        Constructor
        '''
        super(Recorder, self).__init__(parent)
        self.path = path
        self.filePrefix = ''
        self.mobiles = None
        self.interval = 1000
        self.timer = QTimer()
        self.timer.timeout.connect(self.takeSnapshot)
        self.fileName = ''
        self.file = None
        self.lineCount = 0
        self.maxLines = 10000

    def setMobiles(self, mobiles):
        self.stopRecording()
        self.mobiles = mobiles

    def openFile(self):
        dt = datetime.now(tz=timezone.utc)
        s = self.filePrefix + dt.strftime('%Y%m%d-%H%M%S') + '.csv'
        self.fileName = os.path.join(self.path, self.filePrefix, s)
        try:
            self.file = open(self.fileName, 'w')
            self.file.write(self.fileHeader())
            self.lineCount = 0
            self.recordingStarted.emit(self.fileName, True)
        except (IOError, FileNotFoundError):
            self.file = None
            self.recordingStarted.emit(self.fileName, False)

    @pyqtSlot()
    def startRecording(self):
        self.openFile()
        self.timer.start(self.interval)

    @pyqtSlot()
    def stopRecording(self):
        self.timer.stop()
        if self.file is not None:
            self.file.close()
            self.file = None

    @pyqtSlot()
    def takeSnapshot(self):
        if self.file is None:
            return
        dt = datetime.now(tz=timezone.utc)
        line = dt.strftime('%d.%m.%Y\t%H:%M:%S')
        for v in self.mobiles.values():
            lat, lon, depth, heading, altitude = v.reportPosition()
            line += '\t{:.9f}\t{:.9f}\t{:.1f}\t{:.1f}\t{:.1f}'.format(lat, lon, depth, heading, altitude)
        line += '\n'
        try:
            self.file.write(line)
            self.lineCount += 1
            if self.lineCount > self.maxLines:
                self.file.close()
                self.openFile()
        except (IOError, ValueError):
            pass

    def fileHeader(self):
        header = 'Date\tTime'
        for k in self.mobiles:
            header = header + '\t' + k + ' Lat\t' + k + ' Lon\t' + k + ' Depth\t' + k + ' Heading\t' + k + ' Altitude'
        header += '\n'
        return header
