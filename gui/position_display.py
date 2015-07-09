'''
Created on 09.07.2015

@author: jrenken
'''
from PyQt4.QtGui import QWidget, QHBoxLayout, QPushButton, QLabel
from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsPoint
from PyQt4.Qt import pyqtSlot
from PyQt4.QtCore import Qt

class PositionDisplay(QWidget):
    '''
    classdocs
    '''

    
    def __init__(self, iface, parent=None):
        '''
        Constructor
        '''
        super(PositionDisplay, self).__init__(parent)
        layout = QHBoxLayout()
        button = QPushButton('..')
        button.setObjectName('pushButtonFormat')
        button.clicked.connect(self.switchCoordinateFormat)
        button.setMaximumWidth(23)
        layout.addWidget(button)
        self.label = QLabel('---, ---')
        self.label.setMinimumWidth(200)
        self.label.setAlignment(Qt.AlignHCenter)
        layout.addWidget(self.label)
        self.setLayout(layout)
        
        self.format = 1
        
        canvas = iface.mapCanvas()
        crsDest = QgsCoordinateReferenceSystem(4326)
        crsSrc = canvas.mapSettings().destinationCrs()
        self.xform = QgsCoordinateTransform(crsSrc, crsDest)
        canvas.xyCoordinates.connect(self.mouseMoved)
        canvas.destinationCrsChanged.connect(self.mapCrsHasChanged)
        self.canvas = canvas
        
    @pyqtSlot(name='on_pushButtonFormat_clicked')
    def switchCoordinateFormat(self):
        self.format = (self.format + 1) % 3
        print self.format
    
    @pyqtSlot()
    def mapCrsHasChanged(self):
        crsSrc = self.canvas.mapSettings().destinationCrs()
        self.xform.setSourceCrs(crsSrc)
    
    @pyqtSlot(QgsPoint)        
    def mouseMoved(self, point):
        pt = self.xform.transform(point)
        self.label.setText(self.posToStr(pt))
       
    def posToStr(self, pos):
        if self.format == 0:
            return "{:.6f},{:.6f}".format(pos.y(), pos.x())
        if self.format == 1:
            return pos.toDegreesMinutes(4)
        if self.format == 2:
            return pos.toDegreesMinutesSeconds(2)
