'''
Created on 05.06.2015

@author: jrenken
'''
from PyQt4.QtCore import QSettings
from mobile_item import MobileItem
from dataprovider.data_provider import DataProvider

 
class PosiViewProject(object):
    '''
    classdocs
    '''


    def __init__(self, iface, params = {}):
        '''
        Constructor
        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        :param params: A dictionary defining all the properties of the project
        :type params: dictionary
        '''
        self.iface = iface
        self.dataProviders = dict()
        self.mobileItems = dict()
        self.trackingStarted = False


    def startTracking(self):
        if not self.trackingStarted:
            for k, v in self.dataProviders.items():
                print "Start ", k
                v.start() 
            self.trackingStarted = True
            
                
    def stopTracking(self):
        if self.trackingStarted:
            for k, v in self.dataProviders.items():
                print "Stop ", k
                v.stop() 
            self.trackingStarted = False

    def loadSettings(self, iniFile = None):
        self.read(iniFile)
        for k in self.mobileItems.keys():
            item = self.mobileItems[k]
            for key in item.dataProvider.keys():
                item.subscribePositionProvider(self.dataProviders[key], item.dataProvider[key])
                
    def properties(self):
        props = dict()
        m = dict()
        for k in self.mobileItems.keys():
            p = self.mobileItems[k].properties();
            m[p['Name']] = p
        props['Mobiles'] = m
        pr = dict()
        for k in self.dataProviders.keys(): 
            p = self.dataProviders[k].properties();
            pr[p['Name']] = p
        props['Provider'] = pr
        return props
    
    def setProperties(self, properties):
        tracking = self.trackingStarted
        self.unload()
        self.load(properties)
        if tracking:
            self.startTracking()
        pass
        
    def load(self, properties):
        pr = properties['Provider']
        for k in pr.keys():
            p = DataProvider(pr[k])
            self.dataProviders[p.name] = p

        mob = properties['Mobiles']
        for k in mob.keys():
            m = MobileItem(self.iface, mob[k])
            self.mobileItems[m.name] = m
            for k1 in m.dataProvider.keys():
                m.subscribePositionProvider(self.dataProviders[k1], m.dataProvider[k1])

    
    def unload(self):
        print "Unload Project"
        self.stopTracking()
        for m in self.mobileItems.values():
            m.removeFromCanvas()
        self.mobileItems.clear()
        self.dataProviders.clear()
        
        
    
    def read(self, iniFile = None):
        if iniFile != None:
            s = QSettings(iniFile, QSettings.IniFormat)
        else:
            s = QSettings()
        s.beginGroup('PosiView')
        count = s.beginReadArray('MovingItems')
        for i in range(count):
            s.setArrayIndex(i)
            d = s.value('properties', dict())
            print "Create moving from ", d
            item = MobileItem(self.iface, d)
            self.mobileItems[item.name] = item
        s.endArray()
        count = s.beginReadArray('PositionProvider')
        for i in range(count):
            s.setArrayIndex(i)
            d = s.value('properties', dict())
            print "Create provider from ", d
            provider = DataProvider(d)
            print provider.name
            self.dataProviders[provider.name] = provider
        s.endArray()
        s.endGroup()
        
    def store(self, iniFile = None):
        if file:
            s = QSettings(iniFile, QSettings.IniFormat)
        else:
            s = QSettings()
        s.beginGroup('PosiView')
        idx = 0;
        s.beginWriteArray('MovingItems')
        for k in self.mobileItems.keys():
            print "Store ", self.mobileItems[k].name
            s.setArrayIndex(idx)
            p = self.mobileItems[k].properties();
            print p
            s.setValue('properties', p)
            idx += 1
        s.endArray()
        idx = 0;
        s.beginWriteArray('PositionProvider')
        for k in self.dataProviders.keys():
            print "Store ", self.dataProviders[k].name
            s.setArrayIndex(idx)
            p = self.dataProviders[k].properties();
            print p
            s.setValue('properties', p)
            idx += 1
        s.endArray()
        s.endGroup()
        print "Stored"


    def loadTestProject(self):
        provider = DataProvider({ 'Name': 'Gaps', 'DataDeviceType': 'UDP', 'Port': 2000, 'Parser': 'IX_USBL' })
        self.dataProviders[provider.name] = provider
        provider = DataProvider({ 'Name': 'SCC', 'DataDeviceType': 'UDP', 'Port': 10511, 'Parser': 'PISE' })
        self.dataProviders[provider.name] = provider

        item = MobileItem(self.iface, {'Name': 'Seal', 'tracklen': 100, 'type' : 'shape', 'fillColor': 'yellow', 
                                       'length': 6.0, 'width': 1.5,
                                       'provider' : { 'SCC': None }})
        self.mobileItems[item.name] = item
        for k in item.dataProvider.keys():
            item.subscribePositionProvider(self.dataProviders[k], item.dataProvider[k])
        
        item = MobileItem(self.iface, {'Name': 'Beacon_7', 'timeout': 11000, 'provider' : { 'Gaps': 7 } })
        self.mobileItems[item.name] = item
        for k in item.dataProvider.keys():
            item.subscribePositionProvider(self.dataProviders[k],  item.dataProvider[k])
        item = MobileItem(self.iface, {'Name': 'Ship', 'type' : 'shape', 'timeout': 11000,
                                       'fillColor': 'orange', 'provider' : { 'Gaps': 0 } })
        self.mobileItems[item.name] = item
        for k in item.dataProvider.keys():
            item.subscribePositionProvider(self.dataProviders[k], item.dataProvider[k])

