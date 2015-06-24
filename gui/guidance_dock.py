'''
Created on 30.01.2015

@author: jrenken
'''
import os

from PyQt4 import QtGui, uic
from PyQt4.QtCore import pyqtSlot
from qgis.core import QgsPoint, QgsDistanceArea
from math import pi

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '..', 'ui', 'guidance_dock_base.ui'))


class GuidanceDock(QtGui.QDockWidget, FORM_CLASS):
    '''
    classdocs
    '''

    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(GuidanceDock, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
#         self.pushButtonFontSize.clicked.connect(self.switchFontSize)
        self.distance = QgsDistanceArea()
        self.distance.setSourceCrs(4326)
        self.fontSize = 11
        self.source = None
        self.target = None
        self.srcPos = [QgsPoint(), 0.0]
        self.trgPos = [QgsPoint(), 0.0]
        self.srcHeading = 0.0
        self.trgHeading = 0.0
        
    @pyqtSlot(name='on_pushButtonFontSize_clicked')
    def switchFontSize(self):
        if self.fontSize == 11:
            self.fontSize = 16
        elif self.fontSize == 16:
            self.fontSize = 24
        else:
            self.fontSize = 11
        self.dockWidgetContents.setStyleSheet("font-weight: bold; font-size: {}pt".format(self.fontSize))

    def setMobiles(self, mobiles):
        self.mobiles = mobiles
        self.comboBoxSource.blockSignals(True)
        self.comboBoxTarget.blockSignals(True)
        self.comboBoxSource.clear()
        self.comboBoxSource.addItems(mobiles.keys())
        self.comboBoxSource.setCurrentIndex(-1)
        self.comboBoxTarget.clear()
        self.comboBoxTarget.addItems(mobiles.keys())
        self.comboBoxTarget.setCurrentIndex(-1)
        self.comboBoxSource.blockSignals(False )
        self.comboBoxTarget.blockSignals(False)
        self.resetDisplay()
        
    @pyqtSlot(str, name='on_comboBoxSource_currentIndexChanged')
    def sourceChanged(self, mob):
        if self.source is not None:
            try:
                self.source.newPosition.disconnect(self.onNewSourcePosition)
                self.source.newAttitude.disconnect(self.onNewSourceAttitude)
            except TypeError:
                pass
                    
        try:
            self.source = self.mobiles[mob]
            self.source.newPosition.connect(self.onNewSourcePosition)
            self.source.newAttitude.connect(self.onNewSourceAttitude)
        except KeyError:
            self.source = None
    
    @pyqtSlot(str, name='on_comboBoxTarget_currentIndexChanged')
    def targetChanged(self, mob):
        if self.target is not None:
            try:
                self.target.newPosition.disconnect(self.onNewTargetPosition)
                self.target.newAttitude.disconnect(self.onNewTargetAttitude)
            except TypeError:
                pass
        try:
            self.target = self.mobiles[mob]
            self.target.newPosition.connect(self.onNewTargetPosition)
            self.target.newAttitude.connect(self.onNewTargetAttitude)
        except KeyError:
            self.target = None

    @pyqtSlot(float, QgsPoint, float, float)
    def onNewSourcePosition(self, fix, pos, depth, altitude):
        if [pos, depth] != self.srcPos:
            lon, lat = pos.toDegreesMinutes(4).split(',')
            self.labelSourceLat.setText(lat)
            self.labelSourceLon.setText(lon)
            self.labelSourceDepth.setText(str(depth))
            self.labelVertDistance.setText(str( self.trgPos[1] - depth))
            dist = self.distance.measureLine(self.trgPos[0], pos)
            self.labelDistance.setText(str(dist))
            bearing = self.distance.bearing(pos, self.trgPos[0]) * 180 / pi
            if bearing < 0:
                bearing += 360
            self.labelDirection.setText(str(bearing))
            self.srcPos = [pos, depth]

    @pyqtSlot(float, QgsPoint, float, float)
    def onNewTargetPosition(self, fix, pos, depth, altitude):
        if [pos, depth] != self.trgPos:
            lon, lat = pos.toDegreesMinutes(4).split(',')
            self.labelTargetLat.setText(lat)
            self.labelTargetLon.setText(lon)
            self.labelTargetDepth.setText(str(depth))
            self.labelVertDistance.setText(str( depth - self.srcPos[1]))
            dist = self.distance.measureLine(pos, self.srcPos[0])
            self.labelDistance.setText(str(dist))
            bearing = self.distance.bearing(self.srcPos[0], pos) * 180 / pi
            if bearing < 0:
                bearing += 360
            self.labelDirection.setText(str(bearing))
            self.trgPos = [pos, depth]

    @pyqtSlot(float, float, float)
    def onNewTargetAttitude(self, heading, pitch, roll):
        if self.trgHeading != heading:
            self.trgHeading = heading
            self.labelTargetHeading.setText(str(heading))

    @pyqtSlot(float, float, float)
    def onNewSourceAttitude(self, heading, pitch, roll):
        if self.srcHeading != heading:
            self.srcHeading = heading
            self.labelSourceHeading.setText(str(heading))
        
    def resetDisplay(self):
        self.labelSourceLat.setText('---')
        self.labelSourceLon.setText('---')
        self.labelTargetLat.setText('---')
        self.labelTargetLon.setText('---')
        self.labelSourceHeading.setText('---')
        self.labelTargetHeading.setText('---')
        self.labelSourceDepth.setText('---')
        self.labelTargetDepth.setText('---')
        self.labelDirection.setText('---')
        self.labelDistance.setText('---')
        self.labelVertDistance.setText('---')
