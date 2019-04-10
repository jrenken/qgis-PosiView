'''
Created on Oct 23, 2018

@author: jrenken
'''

import os
from qgis.PyQt import QtGui, uic
from qgis.PyQt.QtCore import pyqtSlot, QSettings
from qgis.PyQt.QtWidgets import QDockWidget
from .compass import CompassWidget


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.split(os.path.dirname(__file__))[0], 'ui', 'compass_dock_base.ui'))


class CompassDock(QDockWidget, FORM_CLASS):
    '''
    Displays a compass with two independant needles with selectabel source
    '''

    def __init__(self, parent=None):
        '''
        Constructor
        '''
        '''
        Constructor
        '''
        super(CompassDock, self).__init__(parent)

        self.setupUi(self)
        self.setStyleSheet("QLabel { padding-left: 5px; padding-right: 5px; }")
        self.compass = CompassWidget()
        self.compass.setMinimumHeight(80)
        self.verticalLayout.addWidget(self.compass)
        self.verticalLayout.setStretch(1, 8)
        self.fontSize = 11
        self.source = None
        self.target = None
        self.srcHeading = 0.0
        self.trgHeading = 0.0
        s = QSettings()

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
        m = s.value('PosiView/Compass/Source')
        if m in self.mobiles:
            self.comboBoxSource.setCurrentIndex(self.comboBoxSource.findText(m))
        m = s.value('PosiView/Compass/Target')
        if m in self.mobiles:
            self.comboBoxTarget.setCurrentIndex(self.comboBoxTarget.findText(m))

    @pyqtSlot(str, name='on_comboBoxSource_currentIndexChanged')
    def sourceChanged(self, mob):
        if self.source is not None:
            try:
                self.source.newAttitude.disconnect(self.onNewSourceAttitude)
            except TypeError:
                pass

        try:
            self.source = self.mobiles[mob]
            self.source.newAttitude.connect(self.onNewSourceAttitude)
            s = QSettings()
            s.setValue('PosiView/Compass/Source', mob)
        except KeyError:
            self.source = None
        self.resetSource()

    @pyqtSlot(str, name='on_comboBoxTarget_currentIndexChanged')
    def targetChanged(self, mob):
        if self.target is not None:
            try:
                self.target.newAttitude.disconnect(self.onNewTargetAttitude)
            except TypeError:
                pass
        try:
            self.target = self.mobiles[mob]
            self.target.newAttitude.connect(self.onNewTargetAttitude)
            s = QSettings()
            s.setValue('PosiView/Compass/Target', mob)
        except KeyError:
            self.target = None
        self.resetTarget()

    @pyqtSlot(float, float, float)
    def onNewTargetAttitude(self, heading, pitch, roll):
        if self.trgHeading != heading:
            self.trgHeading = heading
            self.labelTargetHeading.setText('{:.1f}\xb0'.format(heading))
            self.compass.setAngle2(heading)

    @pyqtSlot(float, float, float)
    def onNewSourceAttitude(self, heading, pitch, roll):
        if self.srcHeading != heading:
            self.srcHeading = heading
            self.labelSourceHeading.setText('{:.1f}\xb0'.format(heading))
            self.compass.setAngle(heading)

    def reset(self):
        try:
            if self.source is not None:
                self.source.newAttitude.disconnect(self.onNewSourceAttitude)
            if self.target is not None:
                self.target.newAttitude.disconnect(self.onNewTargetAttitude)
        except TypeError:
            pass

        self.source = None
        self.target = None
        self.resetSource()
        self.resetTarget()

    def resetSource(self):
        self.srcHeading = -720.0
        self.labelSourceHeading.setText('---')
        self.compass.reset(1)

    def resetTarget(self):
        self.trgHeading = -720.0
        self.labelTargetHeading.setText('---')
        self.compass.reset(2)

    def resizeEvent(self, event):
        fsize = max(9, event.size().width() / 45)
        if fsize != self.fontSize:
            self.fontSize = fsize
            self.dockWidgetContents.setStyleSheet("font-weight: bold; font-size: {}pt".format(self.fontSize))
        return QDockWidget.resizeEvent(self, event)
