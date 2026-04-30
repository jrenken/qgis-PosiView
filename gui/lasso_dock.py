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

    @pyqtSlot(name='on_pushButtonLassoOff_clicked')
    def lassoOff(self):
        self.triggered.emit(-1)

    @pyqtSlot(name='on_pushButtonLasso10_clicked')
    def lasso10m(self):
        self.triggered.emit(10)

    @pyqtSlot(name='on_pushButtonLasso30_clicked')
    def lasso30m(self):
        self.triggered.emit(30)

    @pyqtSlot(name='on_pushButtonLasso50_clicked')
    def lasso50m(self):
        self.triggered.emit(50)
