# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PositionMarker
                                 A QGIS plugin
 PosiView tracks multiple mobile object and vehicles and displays its position on the canvas
                              -------------------
        begin                : 2015-06-01
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Jens Renken/Marum/University of Bremen
        email                : renken@marum.de
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QPointF, QRectF, QLineF, Qt, QPoint
from PyQt4.QtGui import QPainter, QBrush, QColor, QPen, QPolygonF
from qgis.gui import QgsMapCanvasItem, QgsVertexMarker
from qgis.core import QgsPoint, QgsDistanceArea
from _collections import deque
from math import sqrt


class PositionMarker(QgsMapCanvasItem):
    '''
    classdocs
    '''

    def __init__(self, canvas, params={}):
        '''
        Constructor
        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        :param params: A dictionary defining all the properties of the position marker
        :type params: dictionary
        '''
        self.canvas = canvas
        self.type = params.get('type', 'BOX').upper()
        self.size = int(params.get('size', 16))
        self.bounding = 1.414213562 * self.size
        self.length = float(params.get('length', 98.0))
        self.width = float(params.get('width', 17.0))
        self.shape = params.get('shape', ((0.0, -0.5), (0.5, -0.3), (0.5, 0.5), (-0.5, 0.50), (-0.5, -0.3)))
        s = (self.size - 1) / 2
        self.paintShape = QPolygonF([QPointF(-s, -s), QPointF(s, -s), QPointF(s, s), QPointF(-s, s)])
        self.color = self.getColor(params.get('color', 'black'))
        self.fillColor = self.getColor(params.get('fillColor', 'lime'))
        self.penWidth = int(params.get('penWidth', 1))
        if self.type in ('CROSS', 'X'):
            self.penWidth = 5
        self.trackLen = int(params.get('trackLength', 100))
        self.trackColor = self.getColor(params.get('trackColor', self.fillColor))
        self.track = deque()
        self.pos = None
        self.heading = 0
        super(PositionMarker, self).__init__(canvas)
        self.setZValue(int(params.get('zValue', 100)))
        self.distArea = QgsDistanceArea()
        self.distArea.setEllipsoid(u'WGS84')
        self.distArea.setEllipsoidalMode(True)
        self.updateSize()

    def properties(self):
        return {'type': self.type,
                'size': self.size,
                'length': self.length,
                'width': self.width,
                'shape': self.shape,
                'color': self.color.rgba(),
                'fillColor': self.fillColor.rgba(),
                'penWidth': self.penWidth,
                'trackLength': self.trackLen,
                'trackColor' : self.trackColor.rgba(),
                'zValue': self.zValue()}

    def setMapPosition(self, pos):
        if self.pos != pos:
            self.updateTrack()
            self.pos = pos
            self.setPos(self.toCanvasCoordinates(self.pos))
            self.update()

    def newHeading(self, heading):
        if self.heading != heading:
            self.heading = heading
            self.setRotation(self.canvas.rotation() + self.heading)
            self.update()

    def resetPosition(self):
        self.pos = None

    def updatePosition(self):
        if self.pos:
            self.prepareGeometryChange()
            self.updateSize()
            self.setPos(self.toCanvasCoordinates(self.pos))
            self.setRotation(self.canvas.rotation() + self.heading)
            self.update()

    def updateSize(self):
        if self.type != 'SHAPE':
            return
        s = self.canvas.mapSettings()
        self.distArea.setSourceCrs(s.destinationCrs())
        try:
            p1 = self.toMapCoordinates(QPoint(0, 0))
            p2 = self.toMapCoordinates(QPoint(0, 100))
            l = self.distArea.measureLine(p1, p2)
            f = 100 / l
        except:
            f = s.outputDpi() / 0.0254 / s.scale()
        paintLength = max(self.length * f, 50)
        paintWidth = paintLength * self.width / self.length
        self.paintShape.clear()
        for v in self.shape:
            self.paintShape << QPointF(v[0] * paintWidth, v[1] * paintLength)
        self.size = max(paintLength, paintWidth)
        self.bounding = sqrt(pow(paintLength, 2) + pow(paintLength, 2))

    def updateTrack(self):
        if self.pos and self.trackLen:
            if len(self.track) >= self.trackLen:
                tpr = self.track.popleft()
                self.canvas.scene().removeItem(tpr)
                del(tpr)
            tp = QgsVertexMarker(self.canvas)
            tp.setCenter(self.pos)
            tp.setIconType(QgsVertexMarker.ICON_CROSS)
            tp.setColor(self.fillColor)
            tp.setIconSize(3)
            tp.setPenWidth(5)
            self.track.append(tp)

    def setVisible(self, visible):
        for tp in self.track:
            tp.setVisible(visible)
        QgsMapCanvasItem.setVisible(self, visible)

    def deleteTrack(self):
        for tp in self.track:
            self.canvas.scene().removeItem(tp)
        self.track.clear()

    def paint(self, painter, xxx, xxx2):
        if not self.pos:
            return

        s = (self.size - 1) / 2
        pen = QPen(self.color)
        pen.setWidth(self.penWidth)
        painter.setPen(pen)
        if self.type == 'CROSS':
            painter.drawLine(QLineF(-s, 0, s, 0))
            painter.drawLine(QLineF(0, -s, 0, s))
        elif self.type == 'X':
            painter.drawLine(QLineF(-s, -s, s, s))
            painter.drawLine(QLineF(-s, s, s, -s))
        elif self.type == 'BOX':
            brush = QBrush(self.fillColor)
            painter.setBrush(brush)
            painter.drawConvexPolygon(self.paintShape)
        elif self.type == 'SHAPE':
            painter.setRenderHint(QPainter.Antialiasing, True)
            brush = QBrush(self.fillColor)
            painter.setBrush(brush)
#             painter.rotate(self.heading + self.canvas.rotation())
            painter.drawConvexPolygon(self.paintShape)

    def boundingRect(self):
        s = self.bounding / 2
        return QRectF(QPointF(-s, -s), QPointF(s, s))

    def getColor(self, value):
        try:
            return QColor.fromRgba(int(value))
        except ValueError:
            return QColor(value)

    def removeFromCanvas(self):
        self.deleteTrack()
        self.canvas.scene().removeItem(self)
