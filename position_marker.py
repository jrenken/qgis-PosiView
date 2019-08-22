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
from qgis.PyQt.QtCore import QPointF, QRectF, QPoint, QLineF
from qgis.PyQt.QtGui import QPainter, QBrush, QColor, QPen, QPolygonF
from qgis.gui import QgsMapCanvasItem, QgsVertexMarker
from qgis.core import QgsDistanceArea, QgsProject
from _collections import deque
from math import fmod, pi


class PositionMarker(QgsMapCanvasItem):
    '''
    MapCanvasItem for showing the MobileItem on the MapCanvas
    Can have different appearences, fixed ones like corss, x or box
    or a userdefined shape.
    Can display also a label on the canvas
    '''

    MIN_SIZE = 30
    CIRLCE_SIZE = 30

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
        self.showLabel = bool(params.get('showLabel', True))
        s = (self.size - 1) / 2
        self.length = float(params.get('length', 98.0))
        self.width = float(params.get('width', 17.0))
        self.offsetX = float(params.get('offsetX', 0.0))
        self.offsetY = float(params.get('offsetY', 0.0))
        self.shape = params.get('shape', ((0.0, -0.5), (0.5, -0.3), (0.5, 0.5), (-0.5, 0.50), (-0.5, -0.3)))
        self.paintShape = QPolygonF([QPointF(-s, -s), QPointF(s, -s), QPointF(s, s), QPointF(-s, s)])
        self.color = self.getColor(params.get('color', 'black'))
        self.fillColor = self.getColor(params.get('fillColor', 'lime'))
        self.defaultIcon = bool(params.get('defaultIcon', True))
        self.defaultIconFilled = bool(params.get('defaultIconFilled', False))
        self.paintCircle = False
        self.penWidth = int(params.get('penWidth', 1))
        spw = s + self.penWidth + 1
        self.bounding = QRectF(-spw, -spw, spw * 2, spw * 2)
        if self.type in ('CROSS', 'X'):
            self.penWidth = 5
        self.trackLen = int(params.get('trackLength', 100))
        self.trackColor = self.getColor(params.get('trackColor', self.fillColor))
        self.track = deque()
        self.position = None
        self.heading = 0
        self.northAlign = 0.0
        super(PositionMarker, self).__init__(canvas)
        self.setZValue(int(params.get('zValue', 100)))
        self.distArea = QgsDistanceArea()
        self.distArea.setEllipsoid(u'WGS84')
        if self.showLabel:
            self.label = MarkerLabel(self.canvas, params)
            self.label.setZValue(self.zValue() + 0.1)
        self.updateSize()

    def properties(self):
        return {'type': self.type,
                'size': self.size,
                'length': self.length,
                'width': self.width,
                'defaultIcon': self.defaultIcon,
                'defaultIconFilled': self.defaultIconFilled,
                'offsetX': self.offsetX,
                'offsetY': self.offsetY,
                'shape': self.shape,
                'color': self.color.rgba(),
                'fillColor': self.fillColor.rgba(),
                'penWidth': self.penWidth,
                'trackLength': self.trackLen,
                'trackColor' : self.trackColor.rgba(),
                'zValue': self.zValue(),
                'showLabel': self.showLabel}

    def setMapPosition(self, pos):
        if self.position != pos:
            self.updateTrack()
            self.position = pos
            self.setPos(self.toCanvasCoordinates(self.position))
            if self.showLabel:
                self.label.setMapPosition(pos)
            self.update()

    def newHeading(self, heading):
        if self.heading != heading:
            self.heading = heading
            self.setRotation(self.canvas.rotation() + self.heading - self.northAlign)
            self.update()

    def resetPosition(self):
        self.position = None
        if self.showLabel:
            self.label.resetPosition()

    def updatePosition(self):
        if self.position:
            self.prepareGeometryChange()
            self.updateSize()
            self.setPos(self.toCanvasCoordinates(self.position))
            self.setRotation(self.canvas.rotation() + self.heading - self.northAlign)

    def updateMapMagnification(self):
        self.updatePosition()
        if self.showLabel:
            self.label.updatePosition()
        for tp in self.track:
            tp[0].updatePosition()

    def updateSize(self):
        if self.type != 'SHAPE':
            return
        s = self.canvas.mapSettings()
        self.distArea.setSourceCrs(s.destinationCrs(), QgsProject.instance().transformContext())
        try:
            if self.position:
                p1 = self.position
                p = self.toCanvasCoordinates(self.position)
                p2 = self.toMapCoordinates(QPoint(p.x(), p.y() + 100.0))
            else:
                p = self.canvas.viewport().rect().center()
                p1 = self.toMapCoordinates(p)
                p2 = self.toMapCoordinates(QPoint(p.x(), p.y() + 100))
            lngth = self.distArea.measureLine(p1, p2)
            f = 100.0 / lngth
            self.northAlign = fmod(self.distArea.bearing(p2, p1) * 180.0 / pi + self.canvas.rotation(), 360.0)
        except Exception:
            f = s.outputDpi() / 0.0254 / s.scale()
        paintLength = max(self.length * f, self.MIN_SIZE)
        paintWidth = paintLength * self.width / self.length
        offsY = self.offsetX / self.length * paintLength
        offsX = self.offsetY / self.width * paintWidth
        self.paintShape.clear()
        if (self.length * f) < self.MIN_SIZE and self.defaultIcon:
            self.paintCircle = True
            self.bounding = QRectF(-self.CIRLCE_SIZE * 0.5, -self.CIRLCE_SIZE - 2, self.CIRLCE_SIZE, self.CIRLCE_SIZE * 1.5)
        else:
            self.paintCircle = False
            for v in self.shape:
                self.paintShape << QPointF(v[0] * paintWidth - offsX, v[1] * paintLength + offsY)
            self.bounding = self.paintShape.boundingRect()
        self.size = max(paintLength, paintWidth)

    def newTrackPoint(self, pos):
        tp = QgsVertexMarker(self.canvas)
        tp.setCenter(pos)
        tp.setIconType(QgsVertexMarker.ICON_CROSS)
        tp.setColor(self.trackColor)
        tp.setZValue(self.zValue() - 0.1)
        tp.setIconSize(3)
        tp.setPenWidth(3)
        return tp

    def updateTrack(self):
        if self.position and self.trackLen:
            if len(self.track) >= self.trackLen:
                tpr = self.track.popleft()
                self.canvas.scene().removeItem(tpr[0])
                del(tpr)
            tp = self.newTrackPoint(self.position)
            self.track.append((tp, self.position))

    def setVisible(self, visible):
        for tp in self.track:
            tp[0].setVisible(visible)
        QgsMapCanvasItem.setVisible(self, visible)
        if self.showLabel:
            self.label.setVisible(visible)

    def deleteTrack(self):
        for tp in self.track:
            self.canvas.scene().removeItem(tp[0])
        self.track.clear()

    def setTrack(self, track):
        self.track.clear()
        for tp in track:
            tpn = self.newTrackPoint(tp)
            self.track.append((tpn, tp))

    def paint(self, painter, xxx, xxx2):
        if not self.position:
            return

        s = (self.size - 1) / 2
        pen = QPen(self.color)
        pen.setWidth(self.penWidth)
        painter.setPen(pen)
        painter.setRenderHint(QPainter.Antialiasing, True)
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
            if self.paintCircle:
                pen.setWidth(self.penWidth * 2)
                if self.defaultIconFilled:
                    brush = QBrush(self.fillColor)
                    painter.setBrush(brush)
                painter.setPen(pen)
                painter.drawEllipse(QPointF(0, 0), self.CIRLCE_SIZE * 0.4, self.CIRLCE_SIZE * 0.4)
                painter.drawLine(QLineF(0, -self.CIRLCE_SIZE * 0.4, 0, -self.CIRLCE_SIZE))
            else:
                brush = QBrush(self.fillColor)
                painter.setBrush(brush)
                painter.drawConvexPolygon(self.paintShape)

    def boundingRect(self):
        return self.bounding

    def getColor(self, value):
        try:
            return QColor.fromRgba(int(value))
        except ValueError:
            return QColor(value)

    def removeFromCanvas(self):
        self.deleteTrack()
        if self.showLabel:
            self.canvas.scene().removeItem(self.label)
        self.canvas.scene().removeItem(self)


class MarkerLabel(QgsMapCanvasItem):
    '''
    Visual representation of the markers/mobiles name
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
        self.label = params.get('Name', 'Item')
        self.LABEL_DISTANCE = 50
        self.labelDistance = params.get('labelDistance', self.LABEL_DISTANCE)
        self.labelRect = QRectF(self.canvas.fontMetrics().boundingRect(
                self.label)).translated(QPointF(self.labelDistance, -self.labelDistance))
        self.labelRect.setBottomLeft(QPointF(0, 0))
        self.color = self.getColor(params.get('color', 'black'))
        self.position = None
        super(MarkerLabel, self).__init__(canvas)

    def boundingRect(self):
        return self.labelRect

    def paint(self, painter, xxx, xxx2):
        if not self.position:
            return
        pen = QPen(self.color)
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawLine(QPointF(0, 0), QPointF(self.labelDistance, -self.labelDistance / 2))
        painter.drawText(QPointF(self.labelDistance + 2, -self.labelDistance / 2 + 2), self.label)

    def setMapPosition(self, pos):
        if self.position != pos:
            self.position = pos
            self.setPos(self.toCanvasCoordinates(self.position))
            self.update()

    def resetPosition(self):
        self.position = None

    def updatePosition(self):
        if self.position:
            self.setPos(self.toCanvasCoordinates(self.position))

    def getColor(self, value):
        try:
            return QColor.fromRgba(int(value))
        except ValueError:
            return QColor(value)
