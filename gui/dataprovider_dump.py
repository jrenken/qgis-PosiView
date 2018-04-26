'''
Created on 08.07.2015

@author: jrenken
'''
from builtins import str

import os
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog
from qgis.PyQt.QtCore import pyqtSlot, Qt

FORM_CLASS, BASE_CLASS = uic.loadUiType(os.path.join(
    os.path.split(os.path.dirname(__file__))[0], 'ui', 'dataprovider_dump_base.ui'), False)


class DataProviderDump(QDialog, FORM_CLASS):
    '''
    classdocs
    '''

    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(DataProviderDump, self).__init__(parent)
        self.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose, True)

    def subscribeProvider(self, provider):
        self.labelProviderName.setText(provider.name)
        provider.newDataReceived.connect(self.appendParsed)
        provider.newRawDataReceived.connect(self.appendRawData)

    @pyqtSlot(str)
    def appendRawData(self, data):
        self.textBrowserRaw.append(data)

    @pyqtSlot(dict)
    def appendParsed(self, data):
        self.textBrowserParsed.append(str(data))
