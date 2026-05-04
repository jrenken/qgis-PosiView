'''
Created on Apr 30, 2026

@author: jrenken
'''

import os
from qgis.PyQt import QtGui, uic
from qgis.PyQt.QtCore import pyqtSignal, pyqtSlot
from qgis.PyQt.QtWidgets import QDockWidget

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.split(os.path.dirname(__file__))[0], 'ui', 'lasso_dock_base.ui'))


class LassoDock(QDockWidget, FORM_CLASS):
    '''
    classdocs
    '''

    triggered = pyqtSignal(int)

    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(LassoDock, self).__init__(parent)
        self.setupUi(self)
        self.buttons = [
            self.pushButtonLasso1,
            self.pushButtonLasso2,
            self.pushButtonLasso3,
            self.pushButtonLasso4] 

    def setRadii(self, rad=[]):
        for but in self.buttons:
            but.hide()
        for rad, but in zip(rad, self.buttons):
            but.setText(rad)
            but.setVisible(True)

    @pyqtSlot(name='on_pushButtonLassoOff_clicked')
    def lassoOff(self):
        self.triggered.emit(-1)

    @pyqtSlot(name='on_pushButtonLasso1_clicked')
    def lasso1(self):
        self.triggered.emit(int(self.pushButtonLasso1.text()[:-1]))

    @pyqtSlot(name='on_pushButtonLasso2_clicked')
    def lasso2(self):
        self.triggered.emit(int(self.pushButtonLasso2.text()[:-1]))

    @pyqtSlot(name='on_pushButtonLasso3_clicked')
    def lasso3(self):
        self.triggered.emit(int(self.pushButtonLasso3.text()[:-1]))

    @pyqtSlot(name='on_pushButtonLasso4_clicked')
    def lasso4(self):
        self.triggered.emit(int(self.pushButtonLasso4.text()[:-1]))
