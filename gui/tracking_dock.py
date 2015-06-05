'''
Created on 29.01.2015

@author: jrenken
'''

import os

from PyQt4 import QtGui, uic
from PyQt4.QtCore import Qt 
from PyQt4.Qt import pyqtSlot, QSize
from qgis.core import QgsPoint
import resources_rc
from PyQt4.QtGui import QIcon

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'tracking_dock_base.ui'))

class TrackingDock(QtGui.QDockWidget, FORM_CLASS):
    '''
    classdocs
    '''

    def __init__(self, parent = None):
        '''
        Constructor
        '''
        super(TrackingDock, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        
    def addMobile(self, mobile):
        display = TrackingDisplay(mobile, self)
        self.verticalLayout.addWidget(display)
        
        
        
        
class TrackingDisplay(QtGui.QToolBar):
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
        self.nameLabel = QtGui.QLabel(self.mobile.name)
        self.nameLabel.setMinimumSize(80, 23)
        self.nameLabelAction = QtGui.QWidgetAction(self);
        self.nameLabelAction.setDefaultWidget(self.nameLabel);
        self.addAction(self.nameLabelAction)

        self.enableAction = QtGui.QAction("Enable Display", self)
        self.enableAction.setCheckable(True)
        self.enableAction.setChecked(True)
        icon = QIcon(':/plugins/PosiView/ledgrey.png')
        icon.addFile(':/plugins/PosiView/ledgreen.png', QSize(), QIcon.Normal, QIcon.On)
        self.enableAction.setIcon(icon)
        self.addAction(self.enableAction)
        self.enableAction.triggered.connect(self.onEnableClicked)
        
        self.addSeparator()
        self.posLabel = QtGui.QLabel("--:--:-- 0.000000 0.000000\nd = 0.0")
        self.posLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.posLabel.setMinimumSize(180, 23)
        self.posLabel.setStyleSheet('background: red; font-size: 8pt')
        self.posLabelAction = QtGui.QWidgetAction(self);
        self.posLabelAction.setDefaultWidget(self.posLabel);
        self.addAction(self.posLabelAction)
        self.centerAction = QtGui.QAction(QIcon(':/plugins/PosiView/center.png'), "Center &Map", self)
        self.addAction(self.centerAction)
        self.deleteTrackAction = QtGui.QAction(QIcon(':/plugins/PosiView/deletetrack.png'), 'Delete &Track', self)
        self.addAction(self.deleteTrackAction)
        self.deleteTrackAction.triggered.connect(self.mobile.deleteTrack)

                
    @pyqtSlot(QgsPoint, float)
    def onNewPosition(self, pos, depth):
        s = "{:f}  {:f}\nd = {:.1f}".format(pos.y(), pos.x(), depth)
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
        print "enable clicked"
        self.mobile.setEnabled(enable)
        self.upToDate = False
        if enable:
            self.posLabel.setStyleSheet('background: red;')
        else:
            self.posLabel.setStyleSheet('background: white;')
            
            
        