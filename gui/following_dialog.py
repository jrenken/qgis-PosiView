'''
Created on Apr 5, 2024

@author: jrenken
'''

import os
import math
from qgis.PyQt import uic
from qgis.PyQt.QtGui import QColor, QColorConstants
from qgis.PyQt.QtCore import pyqtSlot, QSettings, Qt
from qgis.PyQt.QtWidgets import QDialog, QStatusBar
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
        self.comboBoxRadius.insertItems(0, ['10', '20', '30', '50', '75', '100', '125', '150'])
        self.comboBoxRadius.setCurrentIndex(4)
        self.labelInfo.setText(self.tr('Click on the canvas or select a target vehicle'))
        self.iface = iface
        self.mapTool = QgsMapToolEmitPoint(self.iface.mapCanvas())
        self.mapTool.canvasClicked.connect(self.mouseClicked)
        self.prevMapTool = None
        self.iface.mapCanvas().destinationCrsChanged.connect(self.onCrsChange)
        self.distArea = QgsDistanceArea()
        self.distArea.setEllipsoid(u'WGS84')
        self.onCrsChange()
        self.clickPos = None
        self.lassoColor = QColorConstants.Red

    def setMobiles(self, mobiles):
        # self.reset()
        self.mobiles = mobiles
        s = QSettings()
        self.comboBoxSource.blockSignals(True)
        self.comboBoxSource.clear()
        self.comboBoxSource.addItems(sorted(mobiles.keys()))
        self.comboBoxSource.setCurrentIndex(0)
        m = s.value('PosiView/Following/Source')
        if m in self.mobiles:
            self.comboBoxSource.setCurrentIndex(self.comboBoxSource.findText(m))
        self.comboBoxSource.blockSignals(False)
        self.comboBoxTarget.blockSignals(True)
        self.comboBoxTarget.clear()
        self.comboBoxTarget.addItems(['--'] + sorted(mobiles.keys()))
        self.comboBoxTarget.setCurrentIndex(0)
        m = s.value('PosiView/Following/Target')
        if m in self.mobiles:
            self.comboBoxTarget.setCurrentIndex(self.comboBoxTarget.findText(m))
        self.comboBoxTarget.blockSignals(False)

    @pyqtSlot(QgsPointXY, Qt.MouseButton)
    def mouseClicked(self, pos, button):
        if button == Qt.MouseButton.LeftButton:
            self.clickPos = pos
            try:
                mob = self.comboBoxSource.currentText()
                if self.mobiles[mob].coordinates:
                    self.anyPosChanged(self.mobiles[mob].coordinates, pos)
                else:
                    raise ValueError
            except (KeyError, ValueError):
                self.statusBar.showMessage(self.tr('Need a vehicle with valid position'), 1500)
                pass

    def anyPosChanged(self, src: QgsPointXY, trg: QgsPointXY):
        if src and trg:
            dist = self.distArea.measureLine(src, trg)
            bearing = math.degrees(self.distArea.bearing(src, trg))
            self.labelInfo.setText(self.tr('Distance: {:.1f}, Bearing: {:.1f}').format(dist, bearing))
        else:
            raise ValueError

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
        if self.comboBoxSource.currentIndex() > -1 and self.comboBoxTarget.currentIndex() > 0:
            try:
                mobs = self.mobiles[self.comboBoxSource.currentText()]
                mobt = self.mobiles[self.comboBoxTarget.currentText()]
                self.anyPosChanged(mobs.coordinates, mobt.coordinates)
            except (KeyError, ValueError):
                pass

    def closeEvent(self, _):
        if self.prevMapTool:
            self.iface.mapCanvas().setMapTool(self.prevMapTool)

    @pyqtSlot(name='on_pushButtonAddLasso_clicked')
    def addLasso(self, radius=0):
        try:
            mobs = self.mobiles[self.comboBoxSource.currentText()]
        except KeyError:
            self.statusBar.showMessage(self.tr('Need valid source vehicle'), 1500)
            return
        try:
            mobt = self.mobiles[self.comboBoxTarget.currentText()]
            self.clickPos = mobt.coordinates
        except KeyError:
            pass
        if radius > 0:
            rad = radius
        else:
            rad = int(self.comboBoxRadius.currentText())
        if self.clickPos and mobs.coordinates:
            lm = LassoMarker(self.iface.mapCanvas(),
                             src=mobs.coordinates,
                             target=self.clickPos,
                             radius=rad,
                             color=self.lassoColor)
            mobs.addExtraMarker('lasso', lm)
            self.close()
        else:
            self.statusBar.showMessage(self.tr('Need distance and bearing'), 1500)

    @pyqtSlot(name='on_pushButtonRemoveLasso_clicked')
    def removeLasso(self):
        try:
            mob = self.mobiles[self.comboBoxSource.currentText()]
        except KeyError:
            return
        mob.deleteExtraMarker('lasso')
        self.close()

    @pyqtSlot(str, name='on_comboBoxSource_currentTextChanged')
    def changeSource(self, txt):
        if txt:
            s = QSettings()
            s.setValue('PosiView/Following/Source', txt)
            try:
                m1 = self.mobiles[txt]
                m2 = self.mobiles[self.comboBoxTarget.currentText()]
                self.anyPosChanged(m1.coordinates, m2.coordinates)
            except (KeyError, ValueError):
                self.statusBar.showMessage(self.tr("Need vehicles with valid positions"), 1500)

    @pyqtSlot(str, name='on_comboBoxTarget_currentTextChanged')
    def changeTarget(self, txt):
        if txt:
            s = QSettings()
            s.setValue('PosiView/Following/Target', txt)
            try:
                m1 = self.mobiles[self.comboBoxSource.currentText()]
                m2 = self.mobiles[txt]
                self.anyPosChanged(m1.coordinates, m2.coordinates)
            except (KeyError, ValueError):
                self.statusBar.showMessage(self.tr("Need vehicles with valid positions"), 1500)

    @pyqtSlot(int)
    def setLasso(self, rad):
        if rad < 0:
            self.removeLasso()
        else:
            self.addLasso(rad)

    def setLassoColor(self, color: QColor):
        self.lassoColor = color
