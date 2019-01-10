'''
Created on 05.06.2015

@author: jrenken
'''
from PyQt4.QtCore import QObject, pyqtSlot, QTimer, pyqtSignal
from qgis.core import QgsPoint, QgsCoordinateTransform, \
        QgsCoordinateReferenceSystem, QgsCsException
from qgis.gui import QgsMessageBar
from position_marker import PositionMarker
from PyQt4.QtGui import QLabel, QMovie


class MobileItem(QObject):
    '''
    A Mobile Item that reveives its position from a dataprovider
    and is displayed on the canvas
    Could be everything liek vehicles or simple beacons
    '''

    mobileItemCount = 0

    newPosition = pyqtSignal(float, QgsPoint, float, float)
    newAttitude = pyqtSignal(float, float, float)   # heading, pitch, roll
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
        self.name = params.setdefault('Name', 'MobileItem_' +
                                      str(MobileItem.mobileItemCount))
        self.marker = PositionMarker(self.canvas, params)
        self.marker.setToolTip(self.name)
        self.dataProvider = params.get('provider', dict())
        self.messageFilter = dict()
        self.extData = dict()
        self.coordinates = None
        self.position = None
        self.heading = 0.0
        self.depth = 0.0
        self.altitude = 0.0
        self.lastFix = 0.0
        self.crsXform = QgsCoordinateTransform()
        self.crsXform.setSourceCrs(QgsCoordinateReferenceSystem(4326))
        self.onCrsChange()
        self.canvas.destinationCrsChanged.connect(self.onCrsChange)
        if hasattr(self.canvas, 'magnificationChanged'):
            self.canvas.magnificationChanged.connect(self.onMagnificationChanged)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timeout)
        self.notifyCount = int(params.get('nofixNotify', 0))
        if self.notifyCount:
            self.timer.timeout.connect(self.notifyTimeout)
        self.timeoutCount = 0
        self.timeoutTime = int(params.get('timeout', 3000))
        self.notifyDuration = int(params.get('NotifyDuration', 0))
        self.enabled = True

    def removeFromCanvas(self):
        '''
        Remove the item and its track from the canvas
        '''
        self.marker.removeFromCanvas()

    def properties(self):
        '''
        Return the items properties as dictionary
        :returns: Items properties
        :rtype: dict
        '''
        d = {'Name' : self.name,
             'timeout': self.timeoutTime,
             'nofixNotify': self.notifyCount,
             'enabled': self.enabled,
             'provider' : self.dataProvider}
        d.update(self.marker.properties())
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
        if filterId not in (None, 'None'):
            self.messageFilter[provider.name] = filterId
        elif provider.name in self.messageFilter.keys():
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
        try:
            name = data['name']
            if name in self.messageFilter.keys():
                if not data['id'] in (self.messageFilter[name], str(self.messageFilter[name])):
                    return
        except:
            pass
        self.extData.update(data)

        if 'lat' in data and 'lon' in data:
            self.position = QgsPoint(data['lon'], data['lat'])
            self.heading = data.get('heading', -9999.9)
            self.depth = data.get('depth', -9999.9)
            self.altitude = data.get('altitude', -9999.9)
            try:
                self.coordinates = self.crsXform.transform(self.position)
                self.marker.setMapPosition(self.coordinates)
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

        if 'heading' in data:
            self.newAttitude.emit(data['heading'], data.get('pitch', 0.0),
                                  data.get('roll', 0.0))
            self.marker.newHeading(data['heading'])

    @pyqtSlot(float)
    def onScaleChange(self, ):
        '''
        Slot called when the map is zoomed
        :param scale: New scale
        :type scale: float
        '''
        self.marker.updatePosition()

    @pyqtSlot()
    def onCrsChange(self):
        '''
        SLot called when the mapcanvas CRS is changed
        '''
        crsDst = self.canvas.mapSettings().destinationCrs()
        self.crsXform.setDestCRS(crsDst)
        self.marker.updatePosition()

    @pyqtSlot(float)
    def onMagnificationChanged(self, ):
        '''
        Slot called when the map magnification has changed
        :param scale: New scale
        :type scale: float
        '''
        self.marker.updateMapMagnification()

    @pyqtSlot(bool)
    def setEnabled(self, enabled):
        '''
        Hide or display the item and its track on the map
        :param enabled: what to do
        :type enabled: bool
        '''
        self.enabled = enabled
        self.marker.setVisible(self.enabled)
        self.marker.resetPosition()
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
        self.marker.deleteTrack()

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
        self.timeoutCount += 1
        if self.timeoutCount == self.notifyCount:
            msg = self.tr(u'No fix for %s since more than %d seconds!') % (self.name, self.timeoutTime * self.timeoutCount / 1000)
            w = self.iface.messageBar().createMessage(self.tr(u'PosiView Attention'), msg)
            l = QLabel(w)
            m = QMovie(':/plugins/PosiView/hand.gif')
            m.setSpeed(75)
            l.setMovie(m)
            m.setParent(l)
            m.start()
            w.layout().addWidget(l)
            self.iface.messageBar().pushWidget(w, QgsMessageBar.CRITICAL, duration=self.notifyDuration)

    def getTrack(self):
        tr = [e[1] for e in self.marker.track]
        return tr

    def applyTrack(self, track):
        self.marker.setTrack(track)
