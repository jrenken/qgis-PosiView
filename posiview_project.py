# -*- coding: utf-8 -*-
'''
Created on 05.06.2015

@author: jrenken
'''
from __future__ import absolute_import
from builtins import str
from builtins import range
from builtins import object
from os import environ
from qgis.PyQt.QtCore import QSettings, QCoreApplication
from .mobile_item import MobileItem
from .dataprovider.data_provider import DataProvider
from qgis.gui import QgsMessageBar
from qgis.core import Qgis


class PosiViewProject(object):
    '''PosiView project holds all the provider and mobile items
       and manages the configuration
    '''

    def __init__(self, iface, params={}):
        '''
        Constructor
        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        :param params: A dictionary defining the properties of the project
        :type params: dictionary
        '''

        self.iface = iface
        self.dataProviders = dict()
        self.mobileItems = dict()
        self.missionInfo = {'cruise': 'CruiseXX', 'dive': 'DiveX', 'station' : '#xxx'}
        self.recorderPath = environ['HOME']
        self.autoRecord = False
        self.notifyDuration = 0
        self.showUtcClock = False
        self.defaultFormat = 5
        self.trackingStarted = False
        self.trackCache = dict()

    def startTracking(self):
        if not self.trackingStarted:
            for _, v in self.dataProviders.items():
                v.start()
            self.trackingStarted = True

    def stopTracking(self):
        if self.trackingStarted:
            for _, v in self.dataProviders.items():
                v.stop()
            self.trackingStarted = False

    def loadSettings(self, iniFile=None):
        self.read(iniFile)
        for k in self.mobileItems:
            item = self.mobileItems[k]
            for key in item.dataProvider:
                item.subscribePositionProvider(self.dataProviders[key], item.dataProvider[key])

    def properties(self):
        props = dict()
        props['Mission'] = self.missionInfo
        props['RecorderPath'] = self.recorderPath
        props['AutoRecord'] = self.autoRecord
        props['NotifyDuration'] = self.notifyDuration
        props['ShowUtcClock'] = self.showUtcClock
        props['DefaultFormat'] = self.defaultFormat
        m = dict()
        for k in self.mobileItems:
            p = self.mobileItems[k].properties()
            m[p['Name']] = p
        props['Mobiles'] = m
        pr = dict()
        for k in self.dataProviders:
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
        self.missionInfo = properties.get('Mission', {'cruise': 'CruiseXX', 'dive': 'DiveX', 'station' : '#xxx'})
        self.recorderPath = properties.get('RecorderPath', environ['HOME'])
        self.autoRecord = bool(properties.get('AutoRecord', False))
        self.notifyDuration = int(properties.get('NotifyDuration', 0))
        self.showUtcClock = properties.get('ShowUtcClock', False)
        self.defaultFormat = properties.get('DefaultFormat', False)

        pr = properties['Provider']
        for k in pr:
            p = DataProvider(pr[k])
            self.dataProviders[p.name] = p

        mob = properties['Mobiles']
        for k in mob:
            mob[k]['NotifyDuration'] = self.notifyDuration
            m = MobileItem(self.iface, mob[k])
            self.mobileItems[m.name] = m
            try:
                m.applyTrack(self.trackCache[m.name])
            except KeyError:
                pass

            for k1 in m.dataProvider:
                try:
                    m.subscribePositionProvider(self.dataProviders[k1], m.dataProvider[k1])
                except KeyError:
                    self.iface.messageBar().pushMessage(self.tr(u'Error'), self.tr(u"Can't subscribe dataprovider: ")
                                                        + k1 + self.tr(u' for ') + m.name,
                                                        level=Qgis.Critical, duration=5)
        self.trackCache.clear()

    def unload(self):
        self.stopTracking()
        self.dataProviders.clear()
        for _, m in self.mobileItems.items():
            self.trackCache[m.name] = m.getTrack()
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
                except Exception:
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
            mobile['Name'] = s.value('Name', 'Mobile_{:d}'.format(i), type=str)
            properties['Mobiles'][mobile['Name']] = mobile
        s.endArray()

        properties['Provider'] = dict()
        count = s.beginReadArray('DataProvider')
        for i in range(count):
            s.setArrayIndex(i)
            provider = dict()
            for k in s.childKeys():
                provider[k] = self.convertToBestType(s.value(k))
            provider['Name'] = s.value('Name', 'Provider_{:d}'.format(i), type=str)
            properties['Provider'][provider['Name']] = provider
        s.endArray()
        properties['Mission'] = dict()
        properties['Mission']['cruise'] = s.value('Mission/Cruise', 'CruiseXX')
        properties['Mission']['dive'] = s.value('Mission/Dive', 'DiveX')
        properties['Mission']['station'] = s.value('Mission/Station', '#xxx')
        properties['RecorderPath'] = s.value('Recorder/Path', environ['HOME'])
        properties['AutoRecord'] = s.value('Recorder/AutoRecord', False, type=bool)
        properties['NotifyDuration'] = s.value('Misc/NotifyDuration', 0, type=int)
        properties['ShowUtcClock'] = s.value('Misc/ShowUtcClock', False, type=bool)
        properties['DefaultFormat'] = s.value('Misc/DefaultFormat', 5, type=int)
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
        s.remove('Mobiles')
        s.remove('DataProvider')
        idx = 0
        s.beginWriteArray('Mobiles')
        try:
            for _, v in properties['Mobiles'].items():
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
            for _, v in properties['Provider'].items():
                s.setArrayIndex(idx)
                for k1, v1 in v.items():
                    s.setValue(k1, str(v1))
                idx += 1
        except KeyError:
            pass
        s.endArray()
        s.setValue('Mission/Cruise', properties['Mission']['cruise'])
        s.setValue('Mission/Dive', properties['Mission']['dive'])
        s.setValue('Mission/Station', properties['Mission']['station'])
        s.setValue('Recorder/Path', properties['RecorderPath'])
        s.setValue('Recorder/AutoRecord', properties['AutoRecord'])
        s.setValue('Misc/NotifyDuration', properties['NotifyDuration'])
        s.setValue('Misc/ShowUtcClock', properties['ShowUtcClock'])
        s.setValue('Misc/DefaultFormat', properties['DefaultFormat'])
        s.endGroup()

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('PosiViewProject', message)
