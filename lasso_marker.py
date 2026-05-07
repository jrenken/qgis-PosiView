# -*- coding: utf-8 -*-
'''
Created on Apr 28, 2026

@author: jrenken
'''

from math import sin, cos, hypot, atan2
from qgis.PyQt.QtCore import Qt, QRectF, QPointF
from qgis.PyQt.QtGui import QPen, QColorConstants
from qgis.core import (
    QgsPointXY,
    QgsProject,
    QgsDistanceArea,
    QgsCsException
    )
from qgis.gui import QgsMapCanvasItem


class LassoMarker(QgsMapCanvasItem):
    '''
    Display a Lasso on the Canvas
    '''

    def __init__(self, canvas, src: QgsPointXY, target: QgsPointXY, radius=30.0, color=QColorConstants.Red, params={}):
        super().__init__(canvas)
        self.canvas = canvas
        self.position = src
        self.targetPos = target
        self.distance = None
        self.bearing = None
        self.radius = radius
        self.color = color
        self.bounds = QRectF()
        self.distArea = QgsDistanceArea()
        self.distArea.setEllipsoid(u'WGS84')
        s = self.canvas.mapSettings()
        self.distArea.setSourceCrs(s.destinationCrs(), QgsProject.instance().transformContext())
        try:
            self.distance = self.distArea.measureLine(src, self.targetPos)
            self.bearing = self.distArea.bearing(src, self.targetPos)
        except QgsCsException:
            self.distance = None
            self.bearing = None
        self.paintCoords = None
        self.updateSize()

    def properties(self):
        return {}

    def updateSize(self):
        if self.distance and self.bearing:
            trg = self.toCanvasCoordinates(self.targetPos)
            trg -= self.toCanvasCoordinates(self.position)
            dist = hypot(trg.x(), trg.y())
            f = dist / self.distance
            bear = atan2(trg.x(), -trg.y())
            rad = f * self.radius
            ep = QPointF((dist - rad) * sin(bear), -(dist - rad) * cos(bear))
            cp = QPointF(dist * sin(bear), -dist * cos(bear))
            self.paintCoords = [ep, cp, rad]
            r1 = QRectF(QPointF(0.0, 0.0), cp)
            r2 = QRectF(cp.x() - rad, cp.y() - rad, 2 * rad, 2 * rad)
            self.prepareGeometryChange()
            self.bounds = r1.united(r2)
            if self.position:
                self.setPos(self.toCanvasCoordinates(self.position))

    def updateMapMagnification(self):
        self.updatePosition()

    def updatePosition(self):
        self.updateSize()

    def boundingRect(self):
        return self.bounds

    def setRadius(self, radius):
        self.radius = radius
        self.updateSize()

    def setTargetPos(self, pos: QgsPointXY):
        self.targetPos = pos
        self.updateSize()

    def setMapPosition(self, pos: QgsPointXY):
        self.position = pos
        self.setPos(self.toCanvasCoordinates(self.position))
        self.update()

    def resetPosition(self):
        self.position = None

    def newHeading(self, heading):
        self.setRotation(self.canvas.rotation())

    def setTrack(self, _):
        pass

    def deleteTrack(self):
        pass

    def removeFromCanvas(self):
        self.canvas.scene().removeItem(self)

    def paint(self, painter, option, widget):
        if not self.paintCoords or not self.position:
            return
        pen = QPen(self.color)
        pen.setWidth(1)
        pen.setStyle(Qt.PenStyle.DashDotLine)
        painter.setPen(pen)
        painter.drawLine(QPointF(0.0, 0.0), self.paintCoords[0])
        painter.drawEllipse(self.paintCoords[1], self.paintCoords[2], self.paintCoords[2])
