'''
Created on Apr 5, 2024

@author: jrenken
'''

import os
import math
from qgis.PyQt import QtGui, uic
from qgis.PyQt.QtCore import pyqtSlot, QSettings, Qt
from qgis.PyQt.QtWidgets import QDialog, QAbstractButton, QStatusBar, QLabel, QFrame
from qgis.gui import QgsMapToolEmitPoint
from qgis.core import QgsPointXY, QgsDistanceArea, QgsProject
from ..lasso_marker import LassoMarker

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.split(os.path.dirname(__file__))[0], 'ui', 'following_dialog_base.ui'))


class FollowingDialog(QDialog, FORM_CLASS):
    '''
    classdocs
    '''

    def __init__(self, iface, parent=None):
        '''
        Constructor
        '''
        super(FollowingDialog, self).__init__(parent)
        self.setupUi(self)
        self.statusBar = QStatusBar()
        self.statusBar.setStyleSheet('background: lightgray;')
        self.gridLayout.addWidget(self.statusBar, 10, 0, 1, -1)
        
        self.comboBoxRadius.insertItems(0, ['10', '20', '25', '30', '50', '75', '100', '125', '150'])
        self.comboBoxRadius.setCurrentIndex(4)
        self.labelInfo.setText('Click on the canvas to select a target position')
        self.iface = iface
        self.mapTool = QgsMapToolEmitPoint(self.iface.mapCanvas())
        self.mapTool.canvasClicked.connect(self.mouseClicked)
        self.prevMapTool = None
        self.iface.mapCanvas().destinationCrsChanged.connect(self.onCrsChange)
        self.distArea = QgsDistanceArea()
        self.distArea.setEllipsoid(u'WGS84')
        self.onCrsChange()
        self.clickPos = None


    def setMobiles(self, mobiles):
        # self.reset()
        self.mobiles = mobiles
        self.comboBoxSource.blockSignals(True)
        self.comboBoxSource.clear()
        self.comboBoxSource.addItems(sorted(mobiles.keys()))
        self.comboBoxSource.setCurrentIndex(0)
        s = QSettings()
        m = s.value('PosiView/Following/Source')
        if m in self.mobiles:
            self.comboBoxSource.setCurrentIndex(self.comboBoxSource.findText(m))

    @pyqtSlot(QgsPointXY, Qt.MouseButton)
    def mouseClicked(self, pos, button):
        if button == Qt.LeftButton:
            self.show()
            self.clickPos = pos
            try:
                mob = self.comboBoxSource.currentText()
                if self.mobiles[mob].coordinates:
                    dist = self.distArea.measureLine(self.mobiles[mob].coordinates, pos)
                    bearing = math.degrees(self.distArea.bearing(self.mobiles[mob].coordinates, pos))
                    self.labelInfo.setText(f'Distance: {dist:.1f}, Bearing: {bearing:.1f}')
                else:
                    raise ValueError
            except (KeyError, ValueError):
                self.statusBar.showMessage(self.tr("Need a vehicle with valid position"), 1500);
                pass
            
    @pyqtSlot()
    def onCrsChange(self):
        '''
        SLot called when the mapcanvas CRS is changed
        '''
        crsDst = self.iface.mapCanvas().mapSettings().destinationCrs()
        self.distArea.setSourceCrs(crsDst, QgsProject.instance().transformContext())

    def showEvent(self, _):
        mt = self.iface.mapCanvas().mapTool()
        if mt != self.mapTool:
            self.prevMapTool = self.iface.mapCanvas().mapTool()
        self.iface.mapCanvas().setMapTool(self.mapTool)
            
    def closeEvent(self, _):
        if self.prevMapTool:
            self.iface.mapCanvas().setMapTool(self.prevMapTool)
            
    @pyqtSlot(name='on_pushButtonAddLasso_clicked')
    def addLasso(self):
        try:
            mob = self.mobiles[self.comboBoxSource.currentText()]
        except:
            return
        if self.clickPos and mob.coordinates:
            lm = LassoMarker(self.iface.mapCanvas(), 
                             src=mob.coordinates, 
                             target=self.clickPos, 
                             radius=int(self.comboBoxRadius.currentText()))
            mob.addExtraMarker('lasso', lm)
            self.close()
        else:
            self.statusBar.showMessage(self.tr("Need distance and bearing"), 1500);

    @pyqtSlot(name='on_pushButtonRemoveLasso_clicked')
    def removeLasso(self):
        try:
            mob = self.mobiles[self.comboBoxSource.currentText()]
        except KeyError:
            return
        mob.deleteExtraMarker('lasso')
        self.close()
            
