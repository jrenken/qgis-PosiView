'''
Created on 30.01.2015

@author: jrenken
'''
import os

from PyQt4 import QtGui, uic
from PyQt4.QtCore import pyqtSlot
from qgis.core import QgsPoint

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
        self.fontSize = 11
        self.source = None
        self.target = None
        
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
            self.source.newPosition.disconnect()
        try:
            self.mobiles[mob].newPosition.connect(self.onNewSourcePosition)
        except KeyError:
            self.source = None
    
    @pyqtSlot(str, name='on_comboBoxTarget_currentIndexChanged')
    def targetChanged(self, mob):
        if self.target is not None:
            self.target.newPosition.disconnect()
        try:
            self.mobiles[str(mob)].newPosition.connect(self.onNewTargetPosition)
        except KeyError:
            self.target = None

    @pyqtSlot(float, QgsPoint, float, float)
    def onNewSourcePosition(self, fix, pos, depth, altitude):
        self.labelSourceLat.setText(str(pos.y()))
        self.labelSourceLon.setText(str(pos.x()))
        self.labelSourceDepth.setText(str(depth))

    @pyqtSlot(float, QgsPoint, float, float)
    def onNewTargetPosition(self, fix, pos, depth, altitude):
        self.labelTargetLat.setText(str(pos.y()))
        self.labelTargetLon.setText(str(pos.x()))
        self.labelTargetDepth.setText(str(depth))

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
