'''
Created on 05.06.2015

@author: jrenken
'''
from PyQt4.QtCore import QSettings
from mobile_item import MobileItem
from dataprovider.data_provider import DataProvider
from qgis.gui import QgsMessageBar

 
class PosiViewProject(object):
    '''
    classdocs
    '''

    def __init__(self, iface, params={}):
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
                v.start() 
            self.trackingStarted = True
                          
    def stopTracking(self):
        if self.trackingStarted:
            for k, v in self.dataProviders.items():
                v.stop() 
            self.trackingStarted = False

    def loadSettings(self, iniFile=None):
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
            p = self.dataProviders[k].properties()
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
                try:
                    m.subscribePositionProvider(self.dataProviders[k1], m.dataProvider[k1])
                except KeyError:
                    self.iface.messageBar().pushMessage("Error", 
                                                        "Can't subscribe dataprovider " + k1 + " for " + m.name, 
                                                        level=QgsMessageBar.CRITICAL,
                                                        duration=5)

                        

    def unload(self):
        self.stopTracking()
        self.dataProviders.clear()
        for m in self.mobileItems.values():
            m.removeFromCanvas()
        self.mobileItems.clear()
        
    def convertToBestType(self, val):
        try:
            return int(val)
        except ValueError:
            try:
                return float(val)
            except ValueError:
                try:
                    return eval(val)
                except:
                    return val
        
    def read(self, iniFile=None):
        if iniFile is not None:
            s = QSettings(iniFile, QSettings.IniFormat)
        else:
            s = QSettings()
        properties = dict()
        properties['Mobiles'] = dict()
        s.beginGroup('PosiView')
        count = s.beginReadArray('Mobiles')
        for i in range(count):
            s.setArrayIndex(i)
            mobile = dict()
            for k in s.childKeys():
                mobile[k] = self.convertToBestType(s.value(k))
            properties['Mobiles'][mobile['Name']] = mobile
        s.endArray()

        properties['Provider'] = dict()
        count = s.beginReadArray('DataProvider')
        for i in range(count):
            s.setArrayIndex(i)
            provider = dict()
            for k in s.childKeys():
                provider[k] = self.convertToBestType(s.value(k))
            properties['Provider'][provider['Name']] = provider
        s.endArray()
        s.endGroup()
        return properties
        
    def store(self, iniFile=None, properties=None):
        if iniFile is not None:
            s = QSettings(iniFile, QSettings.IniFormat)
        else:
            s = QSettings()
            
        if properties is None:
            properties = self.properties()
            
        s.beginGroup('PosiView')
        s.remove('')
        idx = 0
        s.beginWriteArray('Mobiles')
        try:
            for k, v in properties['Mobiles'].items():
                s.setArrayIndex(idx)
                for k1, v1 in v.items():
                    s.setValue(k1, str(v1))
                idx += 1
        except KeyError:
            pass
        s.endArray()
        idx = 0
        s.beginWriteArray('DataProvider')
        try:
            for k, v in properties['Provider'].items():
                s.setArrayIndex(idx)
                for k1, v1 in v.items():
                    s.setValue(k1, str(v1))
                idx += 1
        except KeyError:
            pass
        s.endArray()
        s.endGroup()

    def loadTestProject(self):
        provider = DataProvider({'Name': 'Gaps', 'DataDeviceType': 'UDP', 'Port': 2000, 'Parser': 'IX_USBL'})
        self.dataProviders[provider.name] = provider
        provider = DataProvider({'Name': 'SCC', 'DataDeviceType': 'UDP', 'Port': 10511, 'Parser': 'PISE'})
        self.dataProviders[provider.name] = provider

        item = MobileItem(self.iface, {'Name': 'Seal', 'tracklen': 100, 'type' : 'shape', 'fillColor': 'yellow', 
                                       'length': 6.0, 'width': 1.5,
                                       'provider' : {'SCC': None}})
        self.mobileItems[item.name] = item
        for k in item.dataProvider.keys():
            item.subscribePositionProvider(self.dataProviders[k], item.dataProvider[k])
        
        item = MobileItem(self.iface, {'Name': 'Beacon_7', 'timeout': 11000, 'provider' : {'Gaps': 1}})
        self.mobileItems[item.name] = item
        for k in item.dataProvider.keys():
            item.subscribePositionProvider(self.dataProviders[k],  item.dataProvider[k])
        item = MobileItem(self.iface, {'Name': 'Ship', 'type' : 'shape', 'timeout': 5000,
                                       'fillColor': 'orange', 'provider' : {'Gaps': 0}})
        self.mobileItems[item.name] = item
        for k in item.dataProvider.keys():
            item.subscribePositionProvider(self.dataProviders[k], item.dataProvider[k])
