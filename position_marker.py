'''
Created on 05.06.2015

@author: jrenken
'''
from PyQt4.QtCore import QPointF, QRectF, QLineF, Qt
from PyQt4.QtGui import QPainter, QBrush, QColor, QPen, QPolygonF
from qgis.gui import QgsMapCanvasItem, QgsVertexMarker
from qgis.core import QgsPoint
from _collections import deque

class PositionMarker(QgsMapCanvasItem):
    '''
    classdocs
    '''


    def __init__(self, canvas, params = {}):
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
        self.size = int( params.get('size', 16) )
        self.length = float( params.get('length', 98.0))
        self.width = float( params.get('width', 17.0))
        self.shape =  params.get('shape', (( 0.0, -0.5), (0.5, -0.3), (0.5, 0.5), (-0.5, 0.50), (-0.5, -0.3))) 
        print self.shape
        s = ( self.size - 1 ) / 2
        self.paintShape = QPolygonF( [ QPointF(-s, -s), QPointF(s, -s), QPointF(s, s), QPointF(-s, s) ] )
        self.color = QColor(params.get('color', 'black'))
        self.fillColor = QColor( params.get('fillColor', 'lime') )
        self.penWidth = int( params.get('penWidth', 1) )
        self.alpha = int( params.get('alpha', 255) )
        self.trackLen = int( params.get('tracklen', 100) )
        self.trackColor = QColor( params.get('trackColor', self.fillColor) )
        self.track = deque()
        self.pos = None
        self.heading = 0
        super(PositionMarker, self).__init__(canvas)
        self.setZValue(int( params.get('zValue', 100) ))
        self.updateSize()
        
        
    def properties(self):
        return { 'type': self.type,
                 'size': self.size,
                 'length': self.length,
                 'width': self.width,
                 'shape': self.shape,
                 'color': self.color.name(),
                 'fillColor': self.fillColor.name(),
                 'penWidth': self.penWidth,
                 'alpha': self.alpha,
                 'trackLength': self.trackLen,
                 'trackColor' : self.trackColor.name(),
                 'zValue':self.zValue() }
   
    def newCoords(self, pos):
        if self.pos != pos:
            self.updateTrack()
            self.pos = QgsPoint(pos) # copy
            self.updatePosition()

    def newHeading(self, heading):
        if self.heading != heading:
            self.heading = heading
            self.update()
        
        
    def resetPosition(self):
        self.pos = None
        
    def updatePosition(self):
        if self.pos:
            self.setPos(self.toCanvasCoordinates(self.pos))
            self.update()

    def updateSize(self):
        if self.type != 'SHAPE':
            return
        s = self.canvas.mapSettings()
        f =  s.outputDpi() / 0.0254 / s.scale()
        paintLength = max( self.length * f, 50)
        paintWidth = paintLength * self.width / self.length
        self.paintShape.clear()
        for v in self.shape:
            self.paintShape << QPointF(v[0] * paintWidth, v[1] * paintLength)
        self.size = max(paintLength, paintWidth) 

    def updateTrack(self):
        if self.pos:
            if len(self.track) >= self.trackLen:
                tpr = self.track.popleft()
                self.canvas.scene().removeItem(tpr)
                del(tpr)
            tp = QgsVertexMarker(self.canvas)
            tp.setCenter(self.pos)
            tp.setIconType(QgsVertexMarker.ICON_BOX)
            tp.setColor(self.fillColor)
            tp.setIconSize(5)
            tp.setPenWidth(2)
            self.track.append(tp)
            
    def deleteTrack(self):
        for tp in self.track:
            self.canvas.scene().removeItem(tp)
        self.track.clear()
 
    def paint(self, painter, xxx, xxx2):
        if not self.pos:
            return

        s = ( self.size - 1 ) / 2
        pen = QPen(self.color)
        pen.setWidth( self.penWidth )
        painter.setPen( pen )
        if self.type is 'CROSS':
            painter.drawLine( QLineF( -s, 0, s, 0) )
            painter.drawLine( QLineF( 0, -s, 0, s) )
        elif self.type is 'X':
            painter.drawLine( QLineF( -s, -s, s, s) )
            painter.drawLine( QLineF( -s, s, s, -s) )
        elif self.type is 'BOX':
            brush = QBrush(self.fillColor)
            painter.setBrush(brush)
            painter.drawConvexPolygon(self.paintShape)
        elif self.type is 'SHAPE':
            painter.setRenderHint(QPainter.Antialiasing, True)
            brush = QBrush(self.fillColor)
            painter.setBrush(brush)
            painter.rotate(self.heading)
            painter.drawConvexPolygon(self.paintShape)
                
        
    def boundingRect(self):
        s = ( self.size - 1 ) / 2
        return QRectF(QPointF(-s,-s), QPointF(s, s))

      
