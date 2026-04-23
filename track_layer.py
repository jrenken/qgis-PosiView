'''
Created on Apr 20, 2026

@author: jrenken
'''

from qgis.PyQt.QtCore import QObject, pyqtSlot
from qgis.core import QgsVectorLayer, QgsVectorDataProvider, QgsProject, Qgis, QgsPointXY, QgsGeometry
from qgis.core import QgsFeature, QgsMapLayer


class TrackLayer(QObject):
    '''
    Handler for a pointlayer for recording the track of a vehicle
    '''

    def __init__(self, name:str, parent=None):
        '''
        Constructor
        '''
        super(TrackLayer, self).__init__(parent)

        self.layer = self.getLayer(name)
        QgsProject.instance().layersWillBeRemoved.connect(self.onLayersWillBeRemoved)
        self.hpr_attitude = [0.0, 0.0, 0.0]

    def getLayer(self, name:str): 
        lrs = QgsProject.instance().mapLayersByName(name)
        if lrs:
            for l in lrs:
                if isinstance(l, QgsVectorLayer) and l.geometryType() == Qgis.GeometryType.Point:
                    if l.dataProvider().capabilities() & QgsVectorDataProvider.AddAttributes:
                        return l
        else:
            uri = 'Point?crs=EPSG:4326&field=depth:integer(10,0)&field=altitude:double(10,1)&field=heading:integer(10,0)'
            lr = QgsVectorLayer(uri, name, 'memory')
            if lr.isValid():
                QgsProject.instance().addMapLayer(lr)
            else:
                lr = None
            return lr 
    
    @pyqtSlot(float, QgsPointXY, float, float)
    def onNewPosition(self, fix, pos, depth, altitude):
        if not self.layer:
            return
        feat = QgsFeature(self.layer.fields())
            # feat.initAttributes(self.attributeCount)
        feat.setGeometry(QgsGeometry.fromPointXY(pos))
        feat.setAttribute('depth', int(depth))
        feat.setAttribute('altitude', altitude)
        feat.setAttribute('heading', int(self.hpr_attitude[0]))
        # feat.setAttribute('description', description)
        # feat.setAttribute('class', category)
        # feat.setAttribute('timestamp', timestamp)
        (res, _) = self.layer.dataProvider().addFeatures([feat])
        if res:
            self.layer.updateExtents()
        return res

    @pyqtSlot(float, float, float)
    def onNewAttitude(self, heading, pitch, roll):
        self.hpr_attitude = [heading, pitch, roll]
        
    @pyqtSlot("QStringList")
    def onLayersWillBeRemoved(self, layers: list[str]):
        if not self.layer:
            return
        for lid in layers:
            if lid == self.layer.id():
                self.layer = None
                return
        
