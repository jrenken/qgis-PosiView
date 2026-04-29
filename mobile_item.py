'''
Created on 05.06.2015

@author: jrenken
'''

from qgis.PyQt.QtCore import QObject, pyqtSlot, QTimer, pyqtSignal
from qgis.core import (
    Qgis,
    QgsPointXY,
    QgsCoordinateTransform,
    QgsCoordinateReferenceSystem,
    QgsCsException,
    QgsException,
    QgsBearingUtils,
    QgsProject)
from qgis.gui import QgsMapCanvasItem
from qgis.PyQt.QtWidgets import QLabel
from qgis.PyQt.QtGui import QMovie
from .position_marker import PositionMarker
from .track_layer import TrackLayer
from .lasso_marker import LassoMarker

FILTER_FLAGS = ('-head', '-pos', '+course', '+utm')


class MobileItem(QObject):
    '''
    A Mobile Item that reveives its position from a dataprovider
    and is displayed on the canvas
    Could be everything liek vehicles or simple beacons
    '''

    mobileItemCount = 0

    newPosition = pyqtSignal(float, QgsPointXY, float, float)
    newAttitude = pyqtSignal(float, float, float)  # heading, pitch, roll
    timeout = pyqtSignal()

    def __init__(self, iface, params={}, parent=None):
        '''
        Constructor
        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        :param params: A dictionary defining all the properties of the item
        :type params: dictionary
        :param parent: Parent object for the new item. Defaults None.
        :type parent: QObject
        '''
        super(MobileItem, self).__init__(parent)

        self.iface = iface
        self.canvas = iface.mapCanvas()
        MobileItem.mobileItemCount += 1
        self.name = params.setdefault('Name',
                'MobileItem_' + str(MobileItem.mobileItemCount))
        self.markers = {'main': PositionMarker(self.canvas, params)}
        self.markers['main'].setToolTip(self.name)
        # if self.name == 'Merian':
        #     self.markers['lasso'] = LassoMarker(self.canvas, QgsPointXY(454724.78, 3546222.77), QgsPointXY(454795.64, 3546163.14))
        #     self.markers['eilasso'] = LassoMarker(self.canvas, QgsPointXY(454724.78, 3546222.77), QgsPointXY(454739.44, 3546161.68))
        self.dataProvider = params.get('provider', dict())
        self.messageFilter = dict()
        self.extData = dict()
        self.coordinates = None
        self.position = None
        self.heading = -9999.9
        self.depth = -9999.9
        self.altitude = -9999.9
        self.lastFix = 0.0
        self.crsXform = QgsCoordinateTransform()
        self.crsXform.setSourceCrs(QgsCoordinateReferenceSystem('EPSG:4326'))
        self.onCrsChange()
        self.canvas.destinationCrsChanged.connect(self.onCrsChange)
        if hasattr(self.canvas, 'magnificationChanged'):
            self.canvas.magnificationChanged.connect(self.onMagnificationChanged)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timeout)
        self.notifyCount = int(params.get('nofixNotify', 0))
        self.fadeOut = bool(params.get('fadeOut', False))
        if self.notifyCount or self.fadeOut:
            self.timer.timeout.connect(self.notifyTimeout)
        self.timeoutCount = 0
        self.timeoutTime = int(params.get('timeout', 3000))
        self.notifyDuration = int(params.get('NotifyDuration', 0))
        self.timedOut = False
        self.enabled = True
        self.recordTrack = params.get('recordTrack', False)
        self.recordTrackRepaint = params.get('recordTrackRepaint', False)
        if self.recordTrack:
            self.trackLayer = TrackLayer(self.name, self.recordTrackRepaint)
            self.newPosition.connect(self.trackLayer.onNewPosition)
            self.newAttitude.connect(self.trackLayer.onNewAttitude)

    def removeFromCanvas(self):
        '''
        Remove the item and its track from the canvas
        '''
        for m in self.markers.values(): 
            m.removeFromCanvas()
        # self.lm.removeFromCanvas()

    def properties(self):
        '''
        Return the items properties as dictionary
        :returns: Items properties
        :rtype: dict
        '''
        d = {'Name': self.name,
             'timeout': self.timeoutTime,
             'nofixNotify': self.notifyCount,
             'fadeOut': self.fadeOut,
             'enabled': self.enabled,
             'provider': self.dataProvider,
             'recordTrack': self.recordTrack,
             'recordTrackRepaint': self.recordTrackRepaint}
        for m in self.markers.values():
            d.update(m.properties())
        return d

    def subscribePositionProvider(self, provider, filterId=None):
        '''
        Subscribe the provider for this item
        by connecting to the providers signals
        :param provider: Provider to connect to
        :type provider: DataProvider
        :param filterId: Filter Id for this item
        :type filterId:
        '''
        provider.newDataReceived.connect(self.processNewData)
        try:
            if filterId['id'] not in (None, 'None') or filterId['flags']:
                self.messageFilter[provider.name] = filterId
            elif provider.name in self.messageFilter:
                self.messageFilter.pop(provider.name, None)
        except (KeyError, TypeError):
            self.messageFilter.pop(provider.name, None)

    def unsubscribePositionProvider(self, provider):
        '''
        Unsubscribe provider by disconnecting the providers signals
        :param provider: Provider to diconnect from
        :type provider: DataProvider
        '''
        try:
            provider.newDataReceived.disconnect(self.processData)
            self.messageFilter.pop(provider.name, None)
        except KeyError:
            pass

    @pyqtSlot(dict)
    def processNewData(self, data):
        '''
        Process incoming data from the data provider
        :param data: Positon or attitude data
        :type data: dict
        '''
        if not self.enabled:
            return

        flags = list()
        try:
            pname = data['name']
            flags = self.messageFilter[pname]['flags']
            if not self.messageFilter[pname]['id'] in (None, 'None'):
                if not data['id'] in (self.messageFilter[pname]['id'], str(self.messageFilter[pname]['id'])):
                    return
        except Exception:
            pass

        self.extData.update(data)
        if '-pos' not in flags:

            if ('lat' in data and 'lon' in data) or self.hasUtmCoords(flags, data):
                if self.fadeOut and self.timedOut:
                    for m in self.markers.values():
                        m.setVisible(True)
                    self.timedOut = False
                self.position = QgsPointXY(data['lon'], data['lat'])
                self.heading = data.get('heading', self.heading)
                self.depth = data.get('depth', self.depth)
                self.altitude = data.get('altitude', self.altitude)
                try:
                    self.coordinates = self.crsXform.transform(self.position)
                    for m in self.markers.values():
                        m.setMapPosition(self.coordinates)
                    # self.lm.setMapPosition(self.coordinates)
                    if 'time' in data:
                        self.lastFix = data['time']
                        self.newPosition.emit(self.lastFix, self.position,
                                              self.extData.get('depth', -9999.9),
                                              self.extData.get('altitude', -9999.9))
                        self.timer.start(self.timeoutTime)
                        self.timeoutCount = 0
                except QgsCsException:
                    pass
            elif self.position is not None:
                if 'depth' in data or 'altitude' in data:
                    self.newPosition.emit(self.lastFix, self.position,
                                          self.extData.get('depth', -9999.9),
                                          self.extData.get('altitude', -9999.9))

        if 'heading' in data and '-head' not in flags:
            self.newAttitude.emit(data['heading'], data.get('pitch', 0.0),
                                  data.get('roll', 0.0))
            for m in self.markers.values():
                m.newHeading(data['heading'])
            self.heading = data['heading']
        elif 'course' in data and '+course' in flags:
            self.newAttitude.emit(data['course'], data.get('pitch', 0.0),
                                  data.get('roll', 0.0))
            for m in self.markers.values():
                m.newHeading(data['course'])
            self.heading = data['course']
        if 'text' in data:
            for m in self.markers.values():
                m.newHeading(data['text'])

    def hasUtmCoords(self, flags, data):
        if '+utm' in flags:
            if 'easting' in data and 'northing' in data:
                try:
                    point = self.crsXform.transform(data['easting'], data['northing'], Qgis.TransformDirection.Reverse)
                    data['lat'] = point.y()
                    data['lon'] = point.x()
                    if data['headtype'] == 'G' and 'heading' in data:
                        try:
                            bearing = QgsBearingUtils.bearingTrueNorth(self.crsXform.destinationCrs(), QgsProject.instance().transformContext(),
                                                             QgsPointXY(data['easting'], data['northing']))
                            data['heading'] = (data['heading'] - bearing) % 360.0
                        except QgsException:
                            pass
                    return True
                except QgsCsException:
                    pass
        return False

    @pyqtSlot(float)
    def onScaleChange(self,):
        '''
        Slot called when the map is zoomed
        :param scale: New scale
        :type scale: float
        '''
        for m in self.markers.values():
            m.updatePosition()
        # self.lm.updateSize()

    @pyqtSlot()
    def onCrsChange(self):
        '''
        SLot called when the mapcanvas CRS is changed
        '''
        crsDst = self.canvas.mapSettings().destinationCrs()
        self.crsXform.setDestinationCrs(crsDst)
        for m in self.markers.values():
            m.updatePosition()
        # self.marker.updatePosition()
        # self.lm.updateSize()

    @pyqtSlot(float)
    def onMagnificationChanged(self,):
        '''
        Slot called when the map magnification has changed
        :param scale: New scale
        :type scale: float
        '''
        for m in self.markers.values():
            m.updateMapMagnification()
        # self.marker.updateMapMagnification()

    @pyqtSlot(bool)
    def setEnabled(self, enabled):
        '''
        Hide or display the item and its track on the map
        :param enabled: what to do
        :type enabled: bool
        '''
        self.enabled = enabled
        # self.marker.setVisible(self.enabled)
        # self.lm.setVisible(self.enabled)
        for m in self.markers.values():
            m.setVisible(self.enabled)
            m.resetPosition()
        # self.marker.resetPosition()
        self.extData.clear()
        if self.enabled:
            self.timer.start(self.timeoutTime)
            self.timeoutCount = 0
        else:
            self.timer.stop()

    @pyqtSlot()
    def deleteTrack(self):
        '''
        Delete the track all points
        '''
        for m in self.markers.values():
            m.deleteTrack()

    @pyqtSlot()
    def centerOnMap(self):
        '''
        Center the item on the map
        '''
        if self.coordinates is not None:
            self.canvas.setCenter(self.coordinates)
            self.canvas.refresh()

    def reportPosition(self):
        '''
        Report the position of the item. Used for logging
        :returns: geographic postion, depth and altitude
        :rtype: float, float, float, float, float
        '''
        if self.position is None:
            return -9999.9, -9999.9, -9999.9, 0.0, -9999.9
        return self.position.y(), self.position.x(), self.depth, self.heading, self.altitude

    @pyqtSlot()
    def notifyTimeout(self):
        if self.fadeOut and not self.timedOut:
            for m in self.markers.values():
                m.setVisible(False)
            self.timedOut = True
        if self.notifyCount:
            self.timeoutCount += 1
            if self.timeoutCount == self.notifyCount:
                msg = self.tr(u'No fix for %s since more than %d seconds!') % (self.name, self.timeoutTime * self.timeoutCount / 1000)
                w = self.iface.messageBar().createMessage(self.tr(u'PosiView Attention'), msg)
                label = QLabel(w)
                m = QMovie(':/plugins/PosiView/hand.gif')
                m.setSpeed(75)
                label.setMovie(m)
                m.setParent(label)
                m.start()
                w.layout().addWidget(label)
                self.iface.messageBar().pushWidget(w, level=Qgis.Critical, duration=self.notifyDuration)

    def getTrack(self):
        for m in self.markers.values():
            if hasattr(m, 'track'):
                tr = [e[1] for e in m.track]
                return tr

    def applyTrack(self, track):
        for m in self.markers.values():
            m.setTrack(track)

    def addExtraMarker(self, key: str, marker: QgsMapCanvasItem):
        print('add Lasso')
        if not isinstance(marker, QgsMapCanvasItem):
            return
        if key in self.markers:
            self.markers[key].removeFromCanvas()
        self.markers[key] = marker

    def deleteExtraMarker(self, key: str):
        if key in self.markers and key != 'main':
            self.markers[key].removeFromCanvas();
            del self.markers[key]
