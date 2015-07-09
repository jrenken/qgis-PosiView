'''
Created on 09.07.2015

@author: jrenken
'''
from PyQt4.QtGui import QWidget, QHBoxLayout, QToolButton, QLineEdit
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
        self.setObjectName('positionDisplay')
        self.setMaximumWidth(270)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 3, 0)
        button = QToolButton(self)
        button.setObjectName('toolButtonFormat')
        button.clicked.connect(self.switchCoordinateFormat)
        button.setMaximumSize(23, 23)
        button.setAutoRaise(True)
        layout.addWidget(button)
        self.label = QLineEdit('---  ---')
        self.label.setReadOnly(True)
        self.label.setMinimumSize(220, 33)
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
        
    @pyqtSlot(name='on_toolButtonFormat_clicked')
    def switchCoordinateFormat(self):
        self.format = (self.format + 1) % 3
    
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
            return '{:.6f},{:.6f}'.format(pos.y(), pos.x())
        if self.format == 1:
            return '  '.join(pos.toDegreesMinutes(4, True, True).rsplit(',')[::-1])
        if self.format == 2:
            return '  '.join(pos.toDegreesMinutesSeconds(2, True, True).split(',')[::-1])
