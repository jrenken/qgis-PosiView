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
        self.positionProviders = dict()
        self.movingItems = dict()
        self.trackingStarted = False


    def startTracking(self):
        if not self.trackingStarted:
            for k, v in self.positionProviders.items():
                print "Start ", k
                v.start() 
            self.trackingStarted = True
            
                
    def stopTracking(self):
        if self.trackingStarted:
            for k, v in self.positionProviders.items():
                print "Stop ", k
                v.stop() 
            self.trackingStarted = False

    def loadSettings(self, iniFile = None):
        self.read(iniFile)
        for k in self.movingItems.keys():
            item = self.movingItems[k]
            for key in item.dataProvider.keys():
                item.subscribePositionProvider(self.positionProviders[key], item.dataProvider[key])
                
    def properties(self):
        props = dict()
        m = dict()
        for k in self.movingItems.keys():
            p = self.movingItems[k].properties();
            m[p['Name']] = p
        props['Mobiles'] = m
        pr = dict()
        for k in self.positionProviders.keys(): 
            p = self.positionProviders[k].properties();
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
            p = DataProvider.create(pr[k])
            self.positionProviders[p.name] = p

        mob = properties['Mobiles']
        for k in mob.keys():
            m = MobileItem(self.iface, mob[k])
            self.movingItems[m.name] = m
            for k1 in m.dataProvider.keys():
                m.subscribePositionProvider(self.positionProviders[k1], m.dataProvider[k1])

    
    def unload(self):
        self.stopTracking()
        self.movingItems.clear()
        self.positionProviders.clear()
        
        
    
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
            self.movingItems[item.name] = item
        s.endArray()
        count = s.beginReadArray('PositionProvider')
        for i in range(count):
            s.setArrayIndex(i)
            d = s.value('properties', dict())
            print "Create provider from ", d
            provider = DataProvider.create(d)
            print provider.name
            self.positionProviders[provider.name] = provider
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
        for k in self.movingItems.keys():
            print "Store ", self.movingItems[k].name
            s.setArrayIndex(idx)
            p = self.movingItems[k].properties();
            print p
            s.setValue('properties', p)
            idx += 1
        s.endArray()
        idx = 0;
        s.beginWriteArray('PositionProvider')
        for k in self.positionProviders.keys():
            print "Store ", self.positionProviders[k].name
            s.setArrayIndex(idx)
            p = self.positionProviders[k].properties();
            print p
            s.setValue('properties', p)
            idx += 1
        s.endArray()
        s.endGroup()
        print "Stored"

