'''
Created on 30.01.2015

@author: jrenken
'''
import os
from qgis.PyQt import uic
from qgis.PyQt.QtCore import pyqtSlot, QSettings
from qgis.core import QgsPointXY, QgsDistanceArea, QgsProject, QgsCoordinateReferenceSystem
from qgis.core import QgsCoordinateFormatter, QgsMapLayer, QgsWkbTypes
from qgis.PyQt.QtWidgets import QDockWidget
from datetime import datetime, timezone
from math import pi
from .compass import CompassWidget

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.split(os.path.dirname(__file__))[0], 'ui', 'guidance_dock_base.ui'))


class GuidanceDock(QDockWidget, FORM_CLASS):
    '''
    classdocs
    '''

    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(GuidanceDock, self).__init__(parent)

        self.setupUi(self)
        self.setStyleSheet("QLabel { padding-left: 5px; padding-right: 5px; }")
        self.compass = CompassWidget()
        self.compass.setMinimumHeight(80)
        self.verticalLayout.addWidget(self.compass)
        self.verticalLayout.setStretch(5, 8)
        self.distArea = QgsDistanceArea()
        self.distArea.setEllipsoid(u'WGS84')
        self.distArea.setSourceCrs(QgsCoordinateReferenceSystem('EPSG:4326'), QgsProject.instance().transformContext())
        self.fontSize = 11
        self.source = None
        self.target = None
        self.srcPos = [None, 0.0]
        self.trgPos = [None, 0.0]
        self.srcHeading = 0.0
        self.trgHeading = 0.0
        s = QSettings()
        self.format = s.value('PosiView/Guidance/Format', defaultValue=1, type=int)
        self.showUtc = s.value('PosiView/Misc/ShowUtcClock', defaultValue=False, type=bool)
        self.timer = 0
        self.setUtcClock()
        self.layer = None

    def setUtcClock(self):
        if self.showUtc:
            if not self.timer:
                self.timer = self.startTimer(1000)
            self.frameUtcClock.show()
        else:
            self.frameUtcClock.hide()
            self.killTimer(self.timer)
            self.timer = 0

    def setMobiles(self, mobiles):
        self.reset()
        self.mobiles = mobiles
        self.comboBoxSource.blockSignals(True)
        self.comboBoxTarget.blockSignals(True)
        mobs = sorted(mobiles.keys())
        self.comboBoxSource.clear()
        self.comboBoxSource.addItems(mobs)
        self.comboBoxSource.setCurrentIndex(-1)
        self.comboBoxTarget.clear()
        self.comboBoxTarget.addItems(mobs)
        self.comboBoxTarget.setCurrentIndex(-1)
        self.comboBoxSource.blockSignals(False)
        self.comboBoxTarget.blockSignals(False)
        s = QSettings()
        m = s.value('PosiView/Guidance/Source')
        if m in self.mobiles:
            self.comboBoxSource.setCurrentText(m)  # Index(self.comboBoxSource.findText(m))
        m = s.value('PosiView/Guidance/Target')
        if m in self.mobiles:
            self.comboBoxTarget.setCurrentText(m)  # Index(self.comboBoxTarget.findText(m))
        self.showUtc = s.value('PosiView/Misc/ShowUtcClock', defaultValue=False, type=bool)
        self.setUtcClock()

    @pyqtSlot(name='on_pushButtonFormat_clicked')
    def switchCoordinateFormat(self):
        self.format = (self.format + 1) % 3
        s = QSettings()
        s.setValue('PosiView/Guidance/Format', self.format)
        if self.trgPos[0]:
            lon, lat = self.posToStr(self.trgPos[0])
            self.labelTargetLat.setText(lat)
            self.labelTargetLon.setText(lon)
        if self.srcPos[0]:
            lon, lat = self.posToStr(self.srcPos[0])
            self.labelSourceLat.setText(lat)
            self.labelSourceLon.setText(lon)

    def posToStr(self, pos):
        if self.format == 0:
            return "{:.6f}".format(pos.x()), "{:.6f}".format(pos.y())
        if self.format == 1:
            return QgsCoordinateFormatter.format(pos, QgsCoordinateFormatter.FormatDegreesMinutes, 4).split(',')
        if self.format == 2:
            return QgsCoordinateFormatter.format(pos, QgsCoordinateFormatter.FormatDegreesMinutesSeconds, 2).split(',')

    @pyqtSlot(str, name='on_comboBoxSource_currentIndexChanged')
    def sourceChanged(self, mob):
        if self.source is not None:
            try:
                self.source.newPosition.disconnect(self.onNewSourcePosition)
                self.source.newAttitude.disconnect(self.onNewSourceAttitude)
            except TypeError:
                pass

        if mob in self.mobiles:
            try:
                self.source = self.mobiles[mob]
                self.source.newPosition.connect(self.onNewSourcePosition)
                self.source.newAttitude.connect(self.onNewSourceAttitude)
                s = QSettings()
                s.setValue('PosiView/Guidance/Source', mob)
            except KeyError:
                self.source = None
            self.resetSource()
        elif self.layer:
            for f in self.layer.getFeatures():
                if f['name'] == mob[:-2]:
                    pos = f.geometry().asPoint()
                    self.resetSource()
                    self.onNewSourcePosition(None, pos, -9999, -9999)

    @pyqtSlot(str, name='on_comboBoxTarget_currentIndexChanged')
    def targetChanged(self, mob):
        if self.target is not None:
            try:
                self.target.newPosition.disconnect(self.onNewTargetPosition)
                self.target.newAttitude.disconnect(self.onNewTargetAttitude)
            except TypeError:
                pass

        if mob in self.mobiles:
            try:
                self.target = self.mobiles[mob]
                self.target.newPosition.connect(self.onNewTargetPosition)
                self.target.newAttitude.connect(self.onNewTargetAttitude)
                s = QSettings()
                s.setValue('PosiView/Guidance/Target', mob)
            except KeyError:
                self.target = None
            self.resetTarget()
        elif self.layer:
            for f in self.layer.getFeatures():
                if f['name'] == mob[:-2]:
                    pos = f.geometry().asPoint()
                    self.resetTarget()
                    self.onNewTargetPosition(None, pos, -9999, -9999)

    @pyqtSlot(float, QgsPointXY, float, float)
    def onNewSourcePosition(self, fix, pos, depth, altitude):
        if [pos, depth] != self.srcPos:
            lon, lat = self.posToStr(pos)
            self.labelSourceLat.setText(lat)
            self.labelSourceLon.setText(lon)
            if depth > -9999:
                self.labelSourceDepth.setText('{:.1f}'.format(depth))
            if self.trgPos[0] is not None:
                if depth > -9999 and self.trgPos[1] > -9999:
                    self.labelVertDistance.setText('{:.1f}'.format(self.trgPos[1] - depth))
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

    @pyqtSlot(float, QgsPointXY, float, float)
    def onNewTargetPosition(self, fix, pos, depth, altitude):
        if [pos, depth] != self.trgPos:
            lon, lat = self.posToStr(pos)
            self.labelTargetLat.setText(lat)
            self.labelTargetLon.setText(lon)
            if depth > -9999:
                self.labelTargetDepth.setText('{:.1f}'.format(depth))
            if self.srcPos[0] is not None:
                if depth > -9999 and self.srcPos[1] > -9999:
                    self.labelVertDistance.setText('{:.1f}'.format(depth - self.srcPos[1]))
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
            self.labelTargetHeading.setText('{:.1f}'.format(heading))
            self.compass.setAngle2(heading)

    @pyqtSlot(float, float, float)
    def onNewSourceAttitude(self, heading, pitch, roll):
        if self.srcHeading != heading:
            self.srcHeading = heading
            self.labelSourceHeading.setText('{:.1f}'.format(heading))
            self.compass.setAngle(heading)

    @pyqtSlot(QgsMapLayer)
    def onActiveLayerChanged(self, layer):
        if self.cleanComboBox(self.comboBoxSource):
            self.resetSource()
        if self.cleanComboBox(self.comboBoxTarget):
            self.resetTarget()

        self.layer = None
        if not layer:
            return
        if layer.type() == QgsMapLayer.VectorLayer and layer.wkbType() == QgsWkbTypes.Point:
            if layer.fields().indexOf('name') != -1:
                self.layer = layer
                self.comboBoxSource.blockSignals(True)
                self.comboBoxTarget.blockSignals(True)
                items = sorted([str(f['name']) + '  ' for f in layer.getFeatures()])
                self.comboBoxSource.addItems(items)
                self.comboBoxTarget.addItems(items)
                self.comboBoxSource.blockSignals(False)
                self.comboBoxTarget.blockSignals(False)

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
        self.srcHeading = -9999.0

        self.labelSourceLat.setText('---')
        self.labelSourceLon.setText('---')
        self.labelSourceHeading.setText('---')
        self.labelSourceDepth.setText('---')
        self.compass.reset(1)
        self.resetDistBearing()

    def resetTarget(self):
        self.trgPos = [None, 0.0]
        self.trgHeading = -9999.0

        self.labelTargetLat.setText('---')
        self.labelTargetLon.setText('---')
        self.labelTargetHeading.setText('---')
        self.labelTargetDepth.setText('---')
        self.compass.reset(2)
        self.resetDistBearing()

    def cleanComboBox(self, comboBox):
        comboBox.blockSignals(True)
        ct = comboBox.currentText()
        for _ in range(comboBox.count() - len(self.mobiles)):
            comboBox.removeItem(len(self.mobiles))
        if ct not in self.mobiles:
            comboBox.setCurrentIndex(-1)
            res = True
        else:
            res = False
        comboBox.blockSignals(False)
        return res

    def resetDistBearing(self):
        self.labelDirection.setText('---')
        self.labelDistance.setText('---')
        self.labelVertDistance.setText('---')

    def resizeEvent(self, event):
        fsize = max(8, event.size().width() / 50)
        if fsize != self.fontSize:
            self.fontSize = fsize
            self.dockWidgetContents.setStyleSheet("font-weight: bold; font-size: {}pt;".format(self.fontSize))
        return QDockWidget.resizeEvent(self, event)

    def timerEvent(self, event):
        dt = datetime.now(tz=timezone.utc)
        self.labelTimeUtc.setText(dt.strftime("%H:%M:%S"))
