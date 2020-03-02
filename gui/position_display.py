'''
Created on 09.07.2015

@author: jrenken
'''
from qgis.PyQt.QtWidgets import QWidget, QHBoxLayout, QToolButton, QLineEdit
from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsPointXY, QgsProject, QgsCoordinateFormatter
from qgis.PyQt.Qt import pyqtSlot, pyqtSignal
from qgis.PyQt.QtCore import Qt, QSettings


class PositionDisplay(QWidget):
    '''
    Widget to display the mouse position on the canvas in geographic coordinates (lat/lon)
    The display format can be altered.
    '''

    __FORMATS = ('DD', 'DDM', 'DMDS')

    exportPosition = pyqtSignal(str)

    def __init__(self, iface, parent=None):
        '''Constructor

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        '''
        super(PositionDisplay, self).__init__(parent)
        self.setObjectName('positionDisplay')
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 3, 0)
        self.button = QToolButton(self)
        self.button.setObjectName('toolButtonFormat')
        self.button.clicked.connect(self.switchCoordinateFormat)
        self.button.setAutoRaise(True)
        layout.addWidget(self.button)
        self.label = QLineEdit('---  ---')
        self.label.setReadOnly(True)
        self.label.setAlignment(Qt.AlignHCenter)
        self.label.setStyleSheet('font-weight: bold;')
        layout.addWidget(self.label)
        self.setLayout(layout)

        s = QSettings()
        self.format = s.value('PosiView/PositionDisplay/Format', defaultValue=1, type=int)
        self.button.setText(self.__FORMATS[self.format])

        canvas = iface.mapCanvas()
        crsDest = QgsCoordinateReferenceSystem('EPSG:4326')
        crsSrc = canvas.mapSettings().destinationCrs()
        self.xform = QgsCoordinateTransform(crsSrc, crsDest, QgsProject.instance())
        canvas.xyCoordinates.connect(self.mouseMoved)
        canvas.destinationCrsChanged.connect(self.mapCrsHasChanged)
        self.canvas = canvas

    @pyqtSlot(name='on_toolButtonFormat_clicked')
    def switchCoordinateFormat(self):
        self.format = (self.format + 1) % 3
        self.button.setText(self.tr(self.__FORMATS[self.format]))
        s = QSettings()
        s.setValue('PosiView/PositionDisplay/Format', self.format)

    @pyqtSlot()
    def mapCrsHasChanged(self):
        crsSrc = self.canvas.mapSettings().destinationCrs()
        self.xform.setSourceCrs(crsSrc)

    @pyqtSlot(QgsPointXY)
    def mouseMoved(self, point):
        pt = self.xform.transform(point)
        pos = self.posToStr(pt)
        self.label.setText(pos)
        self.exportPosition.emit(pos)

    def posToStr(self, pos):
        if self.format == 0:
            return '{:.6f}, {:.6f}'.format(pos.y(), pos.x())
        if self.format == 1:
            return ', '.join(QgsCoordinateFormatter.format(pos, QgsCoordinateFormatter.FormatDegreesMinutes, 4).rsplit(',')[::-1])
        if self.format == 2:
            return ', '.join(QgsCoordinateFormatter.format(pos, QgsCoordinateFormatter.FormatDegreesMinutesSeconds, 2).rsplit(',')[::-1])
