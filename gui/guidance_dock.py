'''
Created on 30.01.2015

@author: jrenken
'''
import os

from PyQt4 import QtGui, uic
from PyQt4.QtCore import pyqtSlot, QSettings
from qgis.core import QgsPoint, QgsDistanceArea
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
        self.compass.setMinimumHeight(80)
        self.verticalLayout.addWidget(self.compass)
        self.verticalLayout.setStretch(4, 8)
        self.distArea = QgsDistanceArea()
        self.distArea.setEllipsoid(u'WGS84')
        self.distArea.setEllipsoidalMode(True)
        self.fontSize = 11
        self.source = None
        self.target = None
        self.srcPos = [None, 0.0]
        self.trgPos = [None, 0.0]
        self.srcHeading = 0.0
        self.trgHeading = 0.0
        self.format = 1

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
        self.comboBoxSource.blockSignals(False)
        self.comboBoxTarget.blockSignals(False)
        s = QSettings()
        m = s.value('PosiView/Guidance/Source')
        if m in self.mobiles:
            self.comboBoxSource.setCurrentIndex(self.comboBoxSource.findText(m))
        m = s.value('PosiView/Guidance/Target')
        if m in self.mobiles:
            self.comboBoxTarget.setCurrentIndex(self.comboBoxTarget.findText(m))

    @pyqtSlot(name='on_pushButtonFormat_clicked')
    def switchCoordinateFormat(self):
        self.format = (self.format + 1) % 3
        print self.format

    def posToStr(self, pos):
        if self.format == 0:
            return "{:.6f}".format(pos.y()), "{:.6f}".format(pos.x())
        if self.format == 1:
            return pos.toDegreesMinutes(4, True, True).split(',')
        if self.format == 2:
            return pos.toDegreesMinutesSeconds(2, True, True).split(',')

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
            s = QSettings()
            s.setValue('PosiView/Guidance/Source', mob)
        except KeyError:
            self.source = None
        self.resetSource()

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
            s = QSettings()
            s.setValue('PosiView/Guidance/Target', mob)
        except KeyError:
            self.target = None
        self.resetTarget()

    @pyqtSlot(float, QgsPoint, float, float)
    def onNewSourcePosition(self, fix, pos, depth, altitude):
        if [pos, depth] != self.srcPos:
            lon, lat = self.posToStr(pos)
            self.labelSourceLat.setText(lat)
            self.labelSourceLon.setText(lon)
            self.labelSourceDepth.setText(str(depth))
            if self.trgPos[0] is not None:
                self.labelVertDistance.setText(str(self.trgPos[1] - depth))
                dist = self.distArea.measureLine(self.trgPos[0], pos)
                self.labelDistance.setText('{:.1f}'.format(dist))
                if dist != 0:
                    bearing = self.distArea.bearing(pos, self.trgPos[0]) * 180 / pi
                    if bearing < 0:
                        bearing += 360
                else:
                    bearing = 0.0
                self.labelDirection.setText('{:.1f}'.format(bearing))
            self.srcPos = [pos, depth]

    @pyqtSlot(float, QgsPoint, float, float)
    def onNewTargetPosition(self, fix, pos, depth, altitude):
        if [pos, depth] != self.trgPos:
            lon, lat = self.posToStr(pos)
            self.labelTargetLat.setText(lat)
            self.labelTargetLon.setText(lon)
            self.labelTargetDepth.setText(str(depth))
            if self.srcPos[0] is not None:
                self.labelVertDistance.setText(str(depth - self.srcPos[1]))
                dist = self.distArea.measureLine(pos, self.srcPos[0])
                self.labelDistance.setText('{:.1f}'.format(dist))
                if dist != 0:
                    bearing = self.distArea.bearing(self.srcPos[0], pos) * 180 / pi
                    if bearing < 0:
                        bearing += 360
                else:
                    bearing = 0.0
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
        self.resetSource()
        self.resetTarget()
        self.resetDistBearing()

    def resetSource(self):
        self.srcPos = [None, 0.0]
        self.srcHeading = -720.0

        self.labelSourceLat.setText('---')
        self.labelSourceLon.setText('---')
        self.labelSourceHeading.setText('---')
        self.labelSourceDepth.setText('---')
        self.compass.reset(1)
        self.resetDistBearing()

    def resetTarget(self):
        self.trgPos = [None, 0.0]
        self.trgHeading = -720.0

        self.labelTargetLat.setText('---')
        self.labelTargetLon.setText('---')
        self.labelTargetHeading.setText('---')
        self.labelTargetDepth.setText('---')
        self.compass.reset(2)
        self.resetDistBearing()

    def resetDistBearing(self):
        self.labelDirection.setText('---')
        self.labelDistance.setText('---')
        self.labelVertDistance.setText('---')

    def resizeEvent(self, event):
        fsize = event.size().width() / 40
        if fsize != self.fontSize:
            self.fontSize = fsize
            self.dockWidgetContents.setStyleSheet("font-weight: bold; font-size: {}pt".format(self.fontSize))
        return QtGui.QDockWidget.resizeEvent(self, event)
