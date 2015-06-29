'''
Created on 30.01.2015

@author: jrenken
'''
import os

from PyQt4 import QtGui, uic
from PyQt4.QtCore import pyqtSlot
from qgis.core import QgsPoint, QgsDistanceArea, QgsCoordinateReferenceSystem
from math import pi
from .compass import CompassWidget

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.split(os.path.dirname(__file__))[0], 'ui', 'guidance_dock_base.ui'))


class GuidanceDock(QtGui.QDockWidget, FORM_CLASS):
    '''
    classdocs
    '''

    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(GuidanceDock, self).__init__(parent)

        self.setupUi(self)
        self.compass = CompassWidget() 
        self.verticalLayout.addWidget(self.compass)
        self.verticalLayout.setStretch(4, 5)
        self.distArea = QgsDistanceArea()
        self.distArea.setEllipsoid(u'WGS84')
        self.distArea.setEllipsoidalMode(True)
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
        self.reset()
        self.mobiles = mobiles
        self.comboBoxSource.blockSignals(True)
        self.comboBoxTarget.blockSignals(True)
        self.comboBoxSource.clear()
        self.comboBoxSource.addItems(sorted(mobiles.keys()))
        self.comboBoxSource.setCurrentIndex(-1)
        self.comboBoxTarget.clear()
        self.comboBoxTarget.addItems(sorted(mobiles.keys()))
        self.comboBoxTarget.setCurrentIndex(-1)
        self.comboBoxSource.blockSignals(False )
        self.comboBoxTarget.blockSignals(False)
        
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
            dist = self.distArea.measureLine(self.trgPos[0], pos)
            self.labelDistance.setText('{:.1f}'.format(dist))
            bearing = self.distArea.bearing(pos, self.trgPos[0]) * 180 / pi
            if bearing < 0:
                bearing += 360
            self.labelDirection.setText('{:.1f}'.format(bearing))
            self.srcPos = [pos, depth]

    @pyqtSlot(float, QgsPoint, float, float)
    def onNewTargetPosition(self, fix, pos, depth, altitude):
        if [pos, depth] != self.trgPos:
            lon, lat = pos.toDegreesMinutes(4).split(',')
            self.labelTargetLat.setText(lat)
            self.labelTargetLon.setText(lon)
            self.labelTargetDepth.setText(str(depth))
            self.labelVertDistance.setText(str( depth - self.srcPos[1]))
            dist = self.distArea.measureLine(pos, self.srcPos[0])
            self.labelDistance.setText('{:.1f}'.format(dist))
            bearing = self.distArea.bearing(self.srcPos[0], pos) * 180 / pi
            if bearing < 0:
                bearing += 360
            self.labelDirection.setText('{:.1f}'.format(bearing))
            self.trgPos = [pos, depth]

    @pyqtSlot(float, float, float)
    def onNewTargetAttitude(self, heading, pitch, roll):
        if self.trgHeading != heading:
            self.trgHeading = heading
            self.labelTargetHeading.setText(str(heading))
            self.compass.setAngle2(heading)

    @pyqtSlot(float, float, float)
    def onNewSourceAttitude(self, heading, pitch, roll):
        if self.srcHeading != heading:
            self.srcHeading = heading
            self.labelSourceHeading.setText(str(heading))
            self.compass.setAngle(heading)
        
    def reset(self):
        try:
            if self.source is not None:
                self.source.newPosition.disconnect(self.onNewSourcePosition)
                self.source.newAttitude.disconnect(self.onNewSourceAttitude)
            if self.target is not None:
                self.target.newPosition.disconnect(self.onNewTargetPosition)
                self.target.newAttitude.disconnect(self.onNewTargetAttitude)
        except TypeError:
            pass

        self.source = None
        self.target = None
        self.srcPos = [QgsPoint(), 0.0]
        self.trgPos = [QgsPoint(), 0.0]
        self.srcHeading = 0.0
        self.trgHeading = 0.0

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
