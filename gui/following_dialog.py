'''
Created on Apr 5, 2024

@author: jrenken
'''

import os
import math
from qgis.PyQt import QtGui, uic
from qgis.PyQt.QtCore import pyqtSlot, QSettings, Qt
from qgis.PyQt.QtWidgets import QDialog, QAbstractButton
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
        self.comboBoxSource.setCurrentIndex(-1)
        s = QSettings()
        m = s.value('PosiView/Following/Source')
        if m in self.mobiles:
            self.comboBoxSource.setCurrentIndex(self.comboBoxSource.findText(m))

    @pyqtSlot(QgsPointXY, Qt.MouseButton)
    def mouseClicked(self, pos, button):
        if button == Qt.LeftButton:
            self.show()
            print(pos, self.mobiles['Merian'].coordinates)
            self.clickPos = pos
            if self.mobiles['Merian'].coordinates:
                dist = self.distArea.measureLine(self.mobiles['Merian'].coordinates, pos)
                bearing = math.degrees(self.distArea.bearing(self.mobiles['Merian'].coordinates, pos))
                self.labelInfo.setText(f'Distance: {dist:.1f}, Bearing: {bearing:.1f}')
                print(dist, bearing)
            
    @pyqtSlot()
    def onCrsChange(self):
        '''
        SLot called when the mapcanvas CRS is changed
        '''
        crsDst = self.iface.mapCanvas().mapSettings().destinationCrs()
        self.distArea.setSourceCrs(crsDst, QgsProject.instance().transformContext())

    def showEvent(self, _):
        print('show')
        mt = self.iface.mapCanvas().mapTool()
        if mt != self.mapTool:
            self.prevMapTool = self.iface.mapCanvas().mapTool()
        self.iface.mapCanvas().setMapTool(self.mapTool)
            
    def closeEvent(self, _):
        print('close')
        if self.prevMapTool:
            self.iface.mapCanvas().setMapTool(self.prevMapTool)
            
    @pyqtSlot(name='on_pushButtonAddLasso_clicked')
    def addLasso(self):
        print('clicked add')
        if self.clickPos and self.mobiles['Merian'].coordinates:
            lm = LassoMarker(self.iface.mapCanvas(), self.mobiles['Merian'].coordinates, self.clickPos)
            self.mobiles['Merian'].addExtraMarker('lasso', lm)

    @pyqtSlot(name='on_pushButtonRemoveLasso_clicked')
    def removeLasso(self):
        print('clicked remove')
        self.mobiles['Merian'].deleteExtraMarker('lasso')
            
