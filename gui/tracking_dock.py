'''
Created on 29.01.2015

@author: jrenken
'''
from builtins import str

import os

from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt, QSettings, QSignalMapper, QMimeData, pyqtSignal
from qgis.PyQt.Qt import pyqtSlot, QSize
from qgis.core import QgsPointXY, QgsCoordinateFormatter as cf
from qgis.PyQt.QtGui import QIcon, QDrag, QGuiApplication
from qgis.PyQt.QtWidgets import QAction, QLabel, QWidgetAction, QToolBar, QDockWidget, QToolButton
from time import gmtime, strftime


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.split(os.path.dirname(__file__))[0], 'ui', 'tracking_dock_base.ui'))


class TrackingDock(QDockWidget, FORM_CLASS):
    '''
    Dock widget that displays position and status of the object and vehicles
    '''

    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(TrackingDock, self).__init__(parent)
        self.setupUi(self)
        self.providerToolbar = ProviderToolBar()
        self.verticalLayoutWindow.insertWidget(0, self.providerToolbar)

    def addMobile(self, mobile):
        display = TrackingDisplay(mobile)
        self.verticalLayout.insertWidget(0, display)

    def removeMobiles(self):
        allTracking = self.findChildren(TrackingDisplay)
        for w in allTracking:
            w.releaseMobile()
            self.verticalLayout.removeWidget(w)
            w.deleteLater()

    def setMobiles(self, mobiles):
        self.removeMobiles()
        for key in sorted(mobiles):
            self.addMobile(mobiles[key])

    def addProvider(self, provider):
        self.providerToolbar.createAction(provider)

    def setProviders(self, providers):
        self.providerToolbar.clear()
        for key in sorted(providers):
            self.addProvider(providers[key])

    def removeProviders(self):
        self.providerToolbar.clear()
        self.providerToolbar.actions = []


class TrackingDisplay(QToolBar):
    '''
        Display the position of a mobile and add action for centering
        the map on the vehicle and erasing the track
    '''

    def __init__(self, mobile, parent=None):
        super(TrackingDisplay, self).__init__(parent)
        self.setMovable(True)
        self.setFloatable(True)
        self.mobile = mobile
        self.timedOut = True
        self.lastFix = 0.0
        s = QSettings()
        self.defFormat = s.value('PosiView/Misc/DefaultFormat', defaultValue=0, type=int)
        self.format = self.defFormat & 3
        self.withSuff = cf.FlagDegreesUseStringSuffix if bool(self.defFormat & 4) else cf.FormatFlag(0)
        try:
            self.sep = cf.separator() + ' '
        except AttributeError:
            self.sep = '  '
        self.createActions()
        self.mobile.newPosition.connect(self.onNewPosition)
        self.mobile.timeout.connect(self.onTimeout)
        self.posText = '0.000000, 0.000000'

    def createActions(self):
        self.nameLabel = QLabel(self.mobile.name)
        self.nameLabel.setMinimumSize(80, 23)
        self.nameLabelAction = QWidgetAction(self)
        self.nameLabelAction.setDefaultWidget(self.nameLabel)
        self.addAction(self.nameLabelAction)

        self.enableAction = QAction("Enable Display", self)
        self.enableAction.setCheckable(True)
        self.enableAction.setChecked(True)
        icon = QIcon(':/plugins/PosiView/ledgrey.png')
        icon.addFile(':/plugins/PosiView/ledgreen.png', QSize(), QIcon.Normal, QIcon.On)
        self.enableAction.setIcon(icon)
        self.addAction(self.enableAction)
        self.enableAction.triggered.connect(self.onEnableClicked)
        self.enableAction.triggered.connect(self.mobile.setEnabled)

        self.addSeparator()
        self.posLabel = QLabel("--:--:-- 0.000000, 0.000000")
        self.posLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        widths = (180, 196, 204, 180, 184, 200, 208, 184)
        self.posLabel.setMinimumSize(widths[self.format], 23)
        self.posLabel.setStyleSheet('background: red; font-size: 8pt; color: white;')
        self.posLabelAction = QWidgetAction(self)
        self.posLabelAction.setDefaultWidget(self.posLabel)
        self.addAction(self.posLabelAction)
        self.centerAction = QAction(QIcon(':/plugins/PosiView/center.png'), "Center &Map", self)
        self.addAction(self.centerAction)
        self.deleteTrackAction = QAction(QIcon(':/plugins/PosiView/deletetrack.png'), 'Delete &Track', self)
        self.addAction(self.deleteTrackAction)
        self.deleteTrackAction.triggered.connect(self.mobile.deleteTrack)
        self.centerAction.triggered.connect(self.mobile.centerOnMap)

    @pyqtSlot(float, QgsPointXY, float, float)
    def onNewPosition(self, fix, pos, depth, altitude):
        s = str()
        if fix > 0:
            s = strftime('%H:%M:%S   ', gmtime(fix))
        else:
            s = '--:--:-- '

        if self.format == 1:
            f, pr = cf.FormatDegreesMinutes, 4
        elif self.format == 2:
            f, pr = cf.FormatDegreesMinutesSeconds, 2
        else:
            f, pr = cf.FormatDecimalDegrees, 6
        self.posText = self.sep.join((cf.formatY(pos.y(), f, pr, self.withSuff),
                                      cf.formatX(pos.x(), f, pr, self.withSuff)))
        s += self.posText
        if depth > -9999:
            s += "\nd = {:.1f}".format(depth)
        if altitude > -9999:
            if depth > -9999:
                s += "   alt = {:.1f}".format(altitude)
            else:
                s += "\nalt = {:.1f}".format(altitude)
        self.posLabel.setText(s)
        if self.timedOut:
            if fix > self.lastFix:
                self.posLabel.setStyleSheet('background: lime; font-size: 8pt; color: black;')
                self.timedOut = False
        self.lastFix = fix

    @pyqtSlot()
    def onTimeout(self):
        if not self.timedOut:
            self.timedOut = True
            self.posLabel.setStyleSheet('background: red; font-size: 8pt; color: white;')

    @pyqtSlot(bool)
    def onEnableClicked(self, enable):
        self.timedOut = True
        if enable:
            self.posLabel.setStyleSheet('background: red; font-size: 8pt; color: white;')
        else:
            self.posLabel.setStyleSheet('background: white; font-size: 8pt; color: black;')

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if event.modifiers() == Qt.ControlModifier:
                QGuiApplication.clipboard().setText(self.posText)
            else:
                drag = QDrag(self)
                mimeData = QMimeData()
                mimeData.setText(self.posText)
                drag.setMimeData(mimeData)
                drag.exec_()

    def releaseMobile(self):
        self.mobile = None


class ProviderToolBar(QToolBar):
    '''
    Widget to display the dataprovider status
    '''

    triggered = pyqtSignal(str)

    def __init__(self, parent=None):
        super(ProviderToolBar, self).__init__(parent)
        self.signalMapper = QSignalMapper(self)
        self.setMovable(True)
        self.setFloatable(True)
        self.actions = []
        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.signalMapper.mapped['QString'].connect(self.triggered)

    def createAction(self, provider):
        icon = QIcon(':/plugins/PosiView/ledgreen.png')
        icon.addFile(':/plugins/PosiView/ledgrey.png', QSize(), QIcon.Disabled, QIcon.Off)
        action = QAction(icon, provider.name, None)
        button = QToolButton()
        button.setDefaultAction(action)
        action.setEnabled(False)
        provider.deviceConnected.connect(action.setEnabled)
        provider.deviceDisconnected.connect(action.setDisabled)
        self.signalMapper.setMapping(action, provider.name)
        action.triggered.connect(self.signalMapper.map)
        self.addAction(action)
        self.actions.append(action)
