'''
Created on 30.01.2015

@author: jrenken
'''

import os
from PyQt4 import uic
from PyQt4.QtCore import Qt, pyqtSlot, QModelIndex, pyqtSignal
from PyQt4.QtGui import QStringListModel, QStandardItem, QColor,\
    QFileDialog, QStandardItemModel, QAbstractButton, QDialogButtonBox
from qgis.gui import QgsOptionsDialogBase


FORM_CLASS, BASE_CLASS = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '..', 'ui', 'posiview_properties_base.ui'), True)


class PosiviewProperties(QgsOptionsDialogBase, FORM_CLASS):
    '''
    GUI class classdocs for the Configuration dialog
    '''
    applyChanges = pyqtSignal(dict)
  
    def __init__(self, project, parent=None):
        '''
        Setup dialog widgets with the project properties
        '''
        super(PosiviewProperties, self).__init__("PosiViewProperties", parent)
        self.setupUi(self)
        self.initOptionsBase(False)
        self.restoreOptionsBaseUi()
        self.project = project
        self.projectProperties = project.properties()
        print self.projectProperties
        self.mToolButtonLoad.setDefaultAction(self.actionLoadConfiguration)
        self.mToolButtonSave.setDefaultAction(self.actionSaveConfiguration)

        self.mobileModel = QStringListModel()
        self.mobileListModel = QStringListModel()
        self.mMobileListView.setModel(self.mobileListModel)
        self.mobileProviderModel = QStandardItemModel()
        self.mobileProviderModel.setHorizontalHeaderLabels(('Provider', 'Filter'))
        self.mMobileProviderTableView.setModel(self.mobileProviderModel)
              
        self.providerListModel = QStringListModel()
        self.mDataProviderListView.setModel(self.providerListModel)
        self.comboBoxProviders.setModel(self.providerListModel)
        self.setupModelData(self.projectProperties)
      
    def setupModelData(self, properties):
        self.mobileListModel.setStringList(properties['Mobiles'].keys())
        self.providerListModel.setStringList(properties['Provider'].keys())

    @pyqtSlot(QAbstractButton, name='on_buttonBox_clicked')
    def onButtonBoxClicked(self, button):
        role = self.buttonBox.buttonRole(button)
        if role == QDialogButtonBox.ApplyRole or role == QDialogButtonBox.AcceptRole:
            self.applyChanges.emit(self.projectProperties)

    @pyqtSlot(name='on_actionSaveConfiguration_triggered')
    def onActionSaveConfigurationTriggered(self):
        ''' Save the current configuration
        '''
        fn = QFileDialog.getSaveFileName(None, 'Save PosiView configuration', '', 'Configuration (*.ini *.conf)')
        self.project.store(fn)
  
    @pyqtSlot(name='on_actionLoadConfiguration_triggered')
    def onActionLoadConfigurationTriggered(self):
        ''' Load configuration from file
        '''
        fn = QFileDialog.getOpenFileName(None, 'Save PosiView configuration', '', 'Configuration (*.ini *.conf)')
        self.projectProperties = self.project.read(fn)
        self.setupModelData(self.projectProperties)
      
    @pyqtSlot(QModelIndex, name='on_mMobileListView_clicked')
    def editMobile(self, index):
        ''' Populate the widgets with the selected mobiles properties
        '''
        if index.isValid():
            self.populateMobileWidgets(index)
      
    @pyqtSlot(str, name='on_comboBoxMobileType_currentIndexChanged')
    def mobileTypeChanged(self, mType):
        if mType == 'SHAPE':
#             self.lineEditMobileShape.setText(str(mobile['shape']))
            self.lineEditMobileShape.setEnabled(True)
        else:
            self.lineEditMobileShape.setEnabled(False)
            
    @pyqtSlot(QModelIndex, name='on_mMobileListView_activated')
    def activated(self, index):
        print "activated", index.row()
        
    @pyqtSlot(name='on_toolButtonAddMobile_clicked')
    def addMobile(self):
        self.mobileListModel.insertRow(self.mobileListModel.rowCount())
        index = self.mobileListModel.index(self.mobileListModel.rowCount() - 1)
        self.lineEditMobileName.setText('NewMobile')
        self.mobileListModel.setData(index, 'NewMobile', Qt.DisplayRole)
        self.mMobileListView.setCurrentIndex(index)
        self.applyMobile()
            
    @pyqtSlot(name='on_toolButtonApplyMobile_clicked')        
    def applyMobile(self):
        index = self.mMobileListView.currentIndex()
        if index.isValid() and not self.lineEditMobileName.text() == '':
            mobile = dict()
            mobile['Name'] = self.lineEditMobileName.text()
            mobile['type'] = self.comboBoxMobileType.currentText()
            try:
                t = eval(self.lineEditMobileShape.text())
                if t.__class__ is tuple or t.__class__ is dict:
                    mobile['shape'] = t
            except SyntaxError:
                mobile['shape'] = ((0.0, -0.5), (0.3, 0.5), (0.0, 0.2), (-0.5, 0.5))
            mobile['length'] = self.doubleSpinBoxMobileLength.value()
            mobile['width'] = self.doubleSpinBoxMobileWidth.value()
            mobile['zValue'] = self.spinBoxZValue.value()
            mobile['color'] = self.mColorButtonMobileColor.color().name()
            mobile['fillColor'] = self.mColorButtonMobileFillColor.color().name()
            mobile['timeout'] = self.spinBoxMobileTimeout.value() * 1000
            mobile['trackLength'] = self.spinBoxTrackLength.value()
            mobile['trackColor'] = self.mColorButtonMobileTrackColor.color().name()
            provs = dict()
            for r in range(self.mobileProviderModel.rowCount()):
                try:
                    fil = int(self.mobileProviderModel.item(r, 1).data(Qt.DisplayRole))
                except:
                    fil = self.mobileProviderModel.item(r, 1).data(Qt.DisplayRole)
                    if not fil:
                        fil = None
                provs[self.mobileProviderModel.item(r, 0).data(Qt.DisplayRole)] = fil
            mobile['provider'] = provs    
            print "ApplyMobile ", mobile
            currName = self.mobileListModel.data(index, Qt.DisplayRole)
            if not currName == mobile['Name']:
                del self.projectProperties['Mobiles'][currName]
                self.mobileListModel.setData(index, mobile['Name'], Qt.DisplayRole)
                print self.mobileListModel.stringList()
            self.projectProperties['Mobiles'][mobile['Name']] = mobile
    
    def populateMobileWidgets(self, index):
        mobile = self.projectProperties['Mobiles'][self.mobileListModel.data(index, Qt.DisplayRole)]
        self.lineEditMobileName.setText(mobile.get('Name'))
        self.comboBoxMobileType.setCurrentIndex(self.comboBoxMobileType.findText(mobile.setdefault('type', 'BOX').upper()))
        if mobile['type'] == 'SHAPE':
            self.lineEditMobileShape.setText(str(mobile['shape']))
            self.lineEditMobileShape.setEnabled(True)
        else:
            self.lineEditMobileShape.setEnabled(False)
            self.lineEditMobileShape.clear()
        self.doubleSpinBoxMobileLength.setValue(mobile.get('length', 20.0))
        self.doubleSpinBoxMobileWidth.setValue(mobile.get('width', 5.0))
        self.spinBoxZValue.setValue(mobile.get('zValue', 100))
        self.mColorButtonMobileColor.setColor(QColor(mobile.get('color', 'black')))
        self.mColorButtonMobileFillColor.setColor(QColor(mobile.get('fillColor', 'green')))
        self.spinBoxMobileTimeout.setValue(mobile.get('timeout', 3000) / 1000)
        self.spinBoxTrackLength.setValue(mobile.get('trackLength', 100))
        self.mColorButtonMobileTrackColor.setColor(QColor(mobile.get('trackColor', 'green')))
                 
        r = 0
        self.mobileProviderModel.removeRows(0, self.mobileProviderModel.rowCount())
        if 'provider' in mobile:
            for k, v in mobile['provider'].items():
                prov = QStandardItem(k)
                val = QStandardItem(str(v))
                self.mobileProviderModel.setItem(r, 0, prov)
                self.mobileProviderModel.setItem(r, 1, val)
                r += 1
        
    @pyqtSlot(name='on_toolButtonRemoveMobile_clicked')        
    def removeMobile(self):
        idx = self.mMobileListView.currentIndex()
        if idx.isValid():
            self.projectProperties['Mobiles'].pop(self.mobileListModel.data(idx, Qt.DisplayRole))
            self.mobileListModel.removeRows(idx.row(), 1)
            self.populateMobileWidgets(self.mMobileListView.currentIndex())
            
    @pyqtSlot(name='on_toolButtonAddMobileProvider_clicked')
    def addMobileProvider(self):
        prov = self.comboBoxProviders.currentText()
        fil = None
        if self.lineEditProviderFilter.text() != '':
            fil = self.lineEditProviderFilter.text()
        items = self.mobileProviderModel.findItems(prov, Qt.MatchExactly, 0)
        print items
        if items:
            for item in items:
                self.mobileProviderModel.setItem(item.row(), 1, QStandardItem(fil))
        else:
            print prov, fil
            self.mobileProviderModel.appendRow([QStandardItem(prov), QStandardItem(fil)])
              
    @pyqtSlot(name='on_toolButtonRemoveMobileProvider_clicked')
    def removeMobileProvider(self):
        idx = self.mMobileProviderTableView.currentIndex()
        self.mobileProviderModel.removeRow(idx.row())
          
    @pyqtSlot(name='on_toolButtonApplyDataProvider_clicked')
    def applyDataProvider(self):
        index = self.mDataProviderListView.currentIndex()
        if index.isValid() and not self.lineEditProviderName.text() == '':
            provider = dict()
            provider['Name'] = self.lineEditProviderName.text()
            provider['DataDeviceType'] = self.comboBoxProviderType.currentText()
            if provider['DataDeviceType'] in ('UDP', 'TCP'):
                provider['Host'] = self.lineEditProviderHostName.text()
                provider['Port'] = self.spinBoxProviderPort.value()
            provider['Parser'] = self.comboBoxParser.currentText()
            currName = self.providerListModel.data(index, Qt.DisplayRole)
            if not currName == provider['Name']:
                del self.projectProperties['Provider'][currName]
                self.providerListModel.setData(index, provider['Name'], Qt.DisplayRole)
                print self.providerListModel.stringList()
            self.projectProperties['Provider'][provider['Name']] = provider
            print provider
                 
    @pyqtSlot(QModelIndex, name='on_mDataProviderListView_clicked')
    def editDataProvider(self, index):
        '''
        '''
        if index.isValid():
            self.populateDataProviderWidgets(index)
            
    def populateDataProviderWidgets(self, index):
        print "editProvider: ", self.providerListModel.data(index, Qt.DisplayRole)
        provider = self.projectProperties['Provider'][self.providerListModel.data(index, Qt.DisplayRole)]
        self.lineEditProviderName.setText(provider.get('Name'))
        self.comboBoxProviderType.setCurrentIndex(self.comboBoxProviderType.findText(provider.setdefault('DataDeviceType', 'UDP').upper()))
        if provider['DataDeviceType'] in ('UDP', 'TCP'):
            self.stackedWidgetDataDevice.setCurrentIndex(0)
            self.lineEditProviderHostName.setText(provider.setdefault('Host', '0.0.0.0'))
            self.spinBoxProviderPort.setValue(int(provider.setdefault('Port', 2000)))

        self.comboBoxParser.setCurrentIndex(self.comboBoxParser.findText( provider.setdefault('Parser', 'NONE').upper()))

    @pyqtSlot(name='on_toolButtonAddDataProvider_clicked')
    def addDataProvider(self):
        self.providerListModel.insertRow(self.providerListModel.rowCount())
        index = self.providerListModel.index(self.providerListModel.rowCount() - 1)
        self.lineEditProviderName.setText('NewDataProvider')
        self.providerListModel.setData(index, 'NewDataProvider', Qt.DisplayRole)
        self.mDataProviderListView.setCurrentIndex(index)
        self.applyDataProvider()
        
    @pyqtSlot(name='on_toolButtonRemoveDataProvider_clicked')        
    def removeDataProvider(self):
        idx = self.mDataProviderListView.currentIndex()
        if idx.isValid():
            self.projectProperties['Provider'].pop(self.providerListModel.data(idx, Qt.DisplayRole))
            self.providerListModel.removeRows(idx.row(), 1)
            self.populateDataProviderWidgets(self.mDataProviderListView.currentIndex())
