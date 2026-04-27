'''
Created on Apr 20, 2026

@author: jrenken
'''

from qgis.PyQt.QtCore import QObject, pyqtSlot, QDateTime, Qt
from qgis.core import QgsVectorLayer, QgsVectorDataProvider, QgsProject, Qgis, QgsPointXY, QgsGeometry
from qgis.core import QgsFeature


class TrackLayer(QObject):
    '''
    Handler for a pointlayer for recording the track of a vehicle
    '''

    def __init__(self, name: str, auto_repaint=False, parent=None):
        '''
        Constructor
        '''
        super(TrackLayer, self).__init__(parent)

        self.layer = self.getLayer(name)
        QgsProject.instance().layersWillBeRemoved.connect(self.onLayersWillBeRemoved)
        self.hpr_attitude = [0.0, 0.0, 0.0]
        self.repaint = auto_repaint

    def getLayer(self, name: str):
        lname = name + '_Track'
        lrs = QgsProject.instance().mapLayersByName(lname)
        if lrs:
            for lr in lrs:
                if isinstance(lr, QgsVectorLayer) and lr.geometryType() == Qgis.GeometryType.Point:
                    if lr.dataProvider().capabilities() & QgsVectorDataProvider.AddAttributes:
                        return lr
        else:
            uri = 'Point?crs=EPSG:4326&field=fix:datetime(0,0)&field=depth:integer(10,0)&field=altitude:double(10,1)&field=heading:integer(10,0)'
            lr = QgsVectorLayer(uri, lname, 'memory')
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
        feat.setAttribute('fix', QDateTime.fromMSecsSinceEpoch(int(fix * 1e3), Qt.UTC))
        feat.setAttribute('depth', int(depth))
        feat.setAttribute('altitude', altitude)
        feat.setAttribute('heading', int(self.hpr_attitude[0]))
        res = self.layer.dataProvider().addFeature(feat)
        if res:
            self.layer.updateExtents()
            if self.repaint:
                self.layer.triggerRepaint()

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
