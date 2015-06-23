'''
Created on 29.01.2015

@author: jrenken
'''

import os

from PyQt4 import uic
from PyQt4.QtCore import Qt 
from PyQt4.Qt import pyqtSlot, QSize
from qgis.core import QgsPoint
from PyQt4.QtGui import QIcon, QAction, QLabel, QWidgetAction, QToolBar,\
    QDockWidget
from time import gmtime, strftime


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '..', 'ui', 'tracking_dock_base.ui'))


class TrackingDock(QDockWidget, FORM_CLASS):
    '''
    classdocs
    '''

    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(TrackingDock, self).__init__(parent)
        self.setupUi(self)
        
    def addMobile(self, mobile):
        display = TrackingDisplay(mobile, self)
        self.verticalLayout.addWidget(display)
        
    def removeMobiles(self):
        allTracking = self.findChildren(TrackingDisplay)
        for w in allTracking:
            self.verticalLayout.removeWidget(w)
            w.deleteLater()
        
        
class TrackingDisplay(QToolBar):
    '''
        classdocs
    '''
    
    def __init__(self, mobile, parent = None):
        super(TrackingDisplay, self).__init__(parent)
        self.setMovable(True)
        self.setFloatable(True)
        self.mobile = mobile
        self.upToDate = False
        self.createActions()
        self.mobile.newPosition.connect(self.onNewPosition)
        self.mobile.timeout.connect(self.onTimeout)
        
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
        
        self.addSeparator()
        self.posLabel = QLabel("--:--:-- 0.000000 0.000000\nd = 0.0")
        self.posLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.posLabel.setMinimumSize(180, 23)
        self.posLabel.setStyleSheet('background: red; font-size: 8pt')
        self.posLabelAction = QWidgetAction(self);
        self.posLabelAction.setDefaultWidget(self.posLabel);
        self.addAction(self.posLabelAction)
        self.centerAction = QAction(QIcon(':/plugins/PosiView/center.png'), "Center &Map", self)
        self.addAction(self.centerAction)
        self.deleteTrackAction = QAction(QIcon(':/plugins/PosiView/deletetrack.png'), 'Delete &Track', self)
        self.addAction(self.deleteTrackAction)
        self.deleteTrackAction.triggered.connect(self.mobile.deleteTrack)
        self.centerAction.triggered.connect(self.mobile.centerOnMap)
         
    @pyqtSlot(float, QgsPoint, float, float)
    def onNewPosition(self, fix, pos, depth, altitude):
        s = str()
        if fix > 0:
            s = strftime('%H:%M:%S', gmtime(fix))
        else:
            s = '--:--:--'
        s += "   {:f}  {:f}\nd = {:.1f}".format(pos.y(), pos.x(), depth)
        if altitude > 0:
            s += "   alt = {:.1f}".format(altitude) 
        self.posLabel.setText(s)
        if not self.upToDate:
            self.posLabel.setStyleSheet('background: lime; font-size: 8pt')
            self.upToDate = True
        
    @pyqtSlot()
    def onTimeout(self):
        self.upToDate = False
        self.posLabel.setStyleSheet('background: red; font-size: 8pt')
        
    @pyqtSlot(bool)
    def onEnableClicked(self, enable):
        self.mobile.setEnabled(enable)
        self.upToDate = False
        if enable:
            self.posLabel.setStyleSheet('background: red; font-size: 8pt')
        else:
            self.posLabel.setStyleSheet('background: white; font-size: 8pt')
