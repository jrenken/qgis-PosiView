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


    def __init__(self, parent = None):
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
        self.pushButtonFontSize.clicked.connect(self.switchFontSize)
        self.fontSize = 11
        
        
    @pyqtSlot()
    def switchFontSize(self):
        if self.fontSize == 11:
            self.fontSize = 16
        elif self.fontSize == 16:
            self.fontSize = 24
        else:
            self.fontSize = 11
        self.dockWidgetContents.setStyleSheet("font-weight: bold; font-size: {}pt".format(self.fontSize))
        
        