# -*- coding: utf-8 -*-
'''
Created on Apr 4, 2018

@author: jrenken
'''
from PyQt4.QtCore import pyqtSlot
from qgis.gui import QgsMapToolEmitPoint, QgsRubberBand
from PyQt4.Qt import Qt
from qgis.core import QgsGeometry, QGis, QgsDistanceArea
from PyQt4.QtGui import QToolTip
from math import pi


class MeasureMapTool(QgsMapToolEmitPoint):
    '''
    MapTool for measuring distance and azimuth
    Display result as tooltip on the canvas
    '''


    def __init__(self, canvas):
        '''
        Constructor
        '''
        self.canvas = canvas
        super(MeasureMapTool, self).__init__(self.canvas)
        self.canvas.destinationCrsChanged.connect(self.onCrsChange)
        self.distArea = QgsDistanceArea()
        self.distArea.setEllipsoid(u'WGS84')
        self.distArea.computeAreaInit()
        self.distArea.setEllipsoidalMode(True)
        self.onCrsChange()

        self.rubberBand = QgsRubberBand(self.canvas, QGis.Line)
        self.rubberBand.setZValue(1e6)
        self.rubberBand.setColor(Qt.red)
        self.rubberBand.setWidth(1)
        self.reset()

    def reset(self):
        self.startPoint = self.endPoint = None
        self.rubberBand.reset(QGis.Line)

    def canvasPressEvent(self, e):
        self.startPoint = self.toMapCoordinates(e.pos())

    def canvasReleaseEvent(self, e):
        self.startPoint = None
        self.reset()

    def canvasMoveEvent(self, e):
        if not self.startPoint:
            return
        self.endPoint = self.toMapCoordinates(e.pos())
        self.rubberBand.setToGeometry(
            QgsGeometry.fromPolyline([
                self.startPoint,
                self.endPoint
            ]),
            None
            )
        if self.startPoint != self.endPoint:
            dist = self.distArea.measureLine(self.startPoint, self.endPoint)
            bearing = self.distArea.bearing(self.startPoint, self.endPoint) * 180 / pi
            if bearing < 0:
                bearing += 360.0 
            text = u'{:.1f} m; {:.1f}\u00b0'.format(dist, bearing)
            QToolTip.showText( self.canvas.mapToGlobal( e.pos() ), text, self.canvas )

    def activate(self):
        self.reset()
        super(MeasureMapTool, self).activate()

    def deactivate(self):
        self.reset()
        super(MeasureMapTool, self).deactivate()

    @pyqtSlot()
    def onCrsChange(self):
        '''
        SLot called when the mapcanvas CRS is changed
        '''
        crsDst = self.canvas.mapSettings().destinationCrs()
        self.distArea.setSourceCrs(crsDst)
