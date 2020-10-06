'''
Created on 30.01.2015

@author: jrenken
'''
from builtins import str
from builtins import range

import os
import sys
from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt, QCoreApplication, pyqtSlot, QModelIndex, pyqtSignal, QUrl, QStringListModel
from qgis.PyQt.QtGui import QStandardItem, QColor, QStandardItemModel, QDesktopServices
from qgis.PyQt.QtWidgets import QFileDialog, QAbstractButton, QDialogButtonBox, QMenu
from qgis.gui import QgsOptionsDialogBase
from qgis.PyQt.Qt import QPoint
from PosiView.dataprovider.dataparser import PARSERS
from PosiView.dataprovider.datadevice import DEVICE_TYPES, NETWORK_TYPES
from PosiView.gui.ui_posiview_properties_base import Ui_PosiviewPropertiesBase
from PosiView.mobile_item import FILTER_FLAGS


class PosiviewProperties(QgsOptionsDialogBase, Ui_PosiviewPropertiesBase):
    '''
    GUI class classdocs for the Configuration dialog
    '''
    applyChanges = pyqtSignal(dict)

    PROVIDER_FLAGS = {}

    def __init__(self, project, parent=None):
        '''
        Setup dialog widgets with the project properties
        '''
        super(PosiviewProperties, self).__init__("PosiViewProperties", parent)
        self.setupUi(self)
        if not self.PROVIDER_FLAGS:
            self.PROVIDER_FLAGS[FILTER_FLAGS[0]] = self.tr('ignore heading')
            self.PROVIDER_FLAGS[FILTER_FLAGS[1]] = self.tr('ignore position')
            self.PROVIDER_FLAGS[FILTER_FLAGS[2]] = self.tr('course as heading')
        self.comboBoxProviderFlags.addItems(list(self.PROVIDER_FLAGS.values()))
        self.groupBox_6.hide()
        self.initOptionsBase(False)
        self.restoreOptionsBaseUi()
        self.comboBoxParser.addItems(PARSERS)
        self.comboBoxProviderType.addItems(DEVICE_TYPES)
        self.project = project
        self.projectProperties = project.properties()
        self.mToolButtonLoad.setDefaultAction(self.actionLoadConfiguration)
        self.mToolButtonSave.setDefaultAction(self.actionSaveConfiguration)

        self.mobileListModel = QStringListModel()
        self.mMobileListView.setModel(self.mobileListModel)
        self.mobileProviderModel = QStandardItemModel()
        self.mobileProviderModel.setHorizontalHeaderLabels((self.tr('Provider'),
                                                           self.tr('Filter'),
                                                           self.tr('Advanced Filter')))
        self.mMobileProviderTableView.setModel(self.mobileProviderModel)

        self.providerListModel = QStringListModel()
        self.mDataProviderListView.setModel(self.providerListModel)
        self.comboBoxProviders.setModel(self.providerListModel)
        self.setupModelData(self.projectProperties)
        self.setupGeneralData(self.projectProperties)

    def setupModelData(self, properties):
        self.mobileListModel.setStringList(sorted(properties['Mobiles'].keys()))
        self.providerListModel.setStringList(sorted(properties['Provider'].keys()))

    def setupGeneralData(self, properties):
        self.lineEditCruise.setText(properties['Mission']['cruise'])
        self.lineEditDive.setText(properties['Mission']['dive'])
        self.lineEditStation.setText(properties['Mission']['station'])
        self.lineEditRecorderPath.setText(properties['RecorderPath'])
        self.checkBoxAutoRecording.setChecked(properties['AutoRecord'])
        self.spinBoxNotifyDuration.setValue(properties['NotifyDuration'])
        self.checkBoxUtcClock.setChecked(properties['ShowUtcClock'])
        self.checkBoxWithSuffix.setChecked(properties['DefaultFormat'] & 4)
        self.comboBoxDefaultPositionFormat.setCurrentIndex((properties['DefaultFormat']) & 3)

    def updateGeneralData(self):
        self.projectProperties['Mission']['cruise'] = self.lineEditCruise.text()
        self.projectProperties['Mission']['dive'] = self.lineEditDive.text()
        self.projectProperties['Mission']['station'] = self.lineEditStation.text()
        self.projectProperties['RecorderPath'] = self.lineEditRecorderPath.text()
        self.projectProperties['AutoRecord'] = self.checkBoxAutoRecording.isChecked()
        self.projectProperties['NotifyDuration'] = self.spinBoxNotifyDuration.value()
        self.projectProperties['ShowUtcClock'] = self.checkBoxUtcClock.isChecked()
        self.projectProperties['DefaultFormat'] = self.comboBoxDefaultPositionFormat.currentIndex()
        if self.checkBoxWithSuffix.isChecked():
            self.projectProperties['DefaultFormat'] |= 4

    def getColor(self, value):
        try:
            return QColor.fromRgba(int(value))
        except ValueError:
            return QColor(value)

    @pyqtSlot(QAbstractButton, name='on_buttonBox_clicked')
    def onButtonBoxClicked(self, button):
        role = self.buttonBox.buttonRole(button)
        if role == QDialogButtonBox.ApplyRole or role == QDialogButtonBox.AcceptRole:
            self.updateGeneralData()
            self.applyChanges.emit(self.projectProperties)

    @pyqtSlot(name='on_actionSaveConfiguration_triggered')
    def onActionSaveConfigurationTriggered(self):
        ''' Save the current configuration
        '''
        fn, __ = QFileDialog.getSaveFileName(None, 'Save PosiView configuration', '', 'Configuration (*.ini *.conf)')
        if fn:
            if not os.path.splitext(fn)[1]:
                fn += u'.conf'
            self.project.store(fn)

    @pyqtSlot(name='on_actionLoadConfiguration_triggered')
    def onActionLoadConfigurationTriggered(self):
        ''' Load configuration from file
        '''
        fn, __ = QFileDialog.getOpenFileName(None, 'Save PosiView configuration', '', 'Configuration (*.ini *.conf)')
        self.projectProperties = self.project.read(fn)
        self.setupModelData(self.projectProperties)
        self.setupGeneralData(self.projectProperties)

    @pyqtSlot(QModelIndex, name='on_mMobileListView_clicked')
    def editMobile(self, index):
        ''' Populate the widgets with the selected mobiles properties
        '''
        if index.isValid():
            self.populateMobileWidgets(index)

    @pyqtSlot(str, name='on_comboBoxMobileType_currentIndexChanged')
    def mobileTypeChanged(self, mType):
        if mType == 'SHAPE':
            self.lineEditMobileShape.setEnabled(True)
        else:
            self.lineEditMobileShape.setEnabled(False)

    @pyqtSlot(QModelIndex, name='on_mMobileListView_activated')
    def activated(self, index):
        pass

    @pyqtSlot(name='on_toolButtonAddMobile_clicked')
    def addMobile(self):
        self.mobileListModel.insertRow(self.mobileListModel.rowCount())
        index = self.mobileListModel.index(self.mobileListModel.rowCount() - 1)
        self.lineEditMobileName.setText('NewMobile')
        self.mobileListModel.setData(index, 'NewMobile', Qt.DisplayRole)
        self.mMobileListView.setCurrentIndex(index)
        self.applyMobile()

    @pyqtSlot(name='on_pushButtonApplyMobile_clicked')
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
            mobile['defaultIcon'] = self.checkBoxDefaultIcon.isChecked()
            mobile['defaultIconFilled'] = self.checkBoxDefIconFilled.isChecked()
            mobile['offsetX'] = self.doubleSpinBoxXOffset.value()
            mobile['offsetY'] = self.doubleSpinBoxYOffset.value()
            mobile['zValue'] = self.spinBoxZValue.value()
            mobile['color'] = self.mColorButtonMobileColor.color().rgba()
            mobile['fillColor'] = self.mColorButtonMobileFillColor.color().rgba()
            mobile['timeout'] = self.spinBoxMobileTimeout.value() * 1000
            mobile['nofixNotify'] = self.spinBoxMobileNotification.value()
            mobile['fadeOut'] = self.checkBoxFadeOut.isChecked()
            mobile['trackLength'] = self.spinBoxTrackLength.value()
            mobile['trackColor'] = self.mColorButtonMobileTrackColor.color().rgba()
            mobile['showLabel'] = self.checkBoxShowLabel.isChecked()
            provs = dict()
            for r in range(self.mobileProviderModel.rowCount()):
                try:
                    fil = self.mobileProviderModel.item(r, 1).data(Qt.DisplayRole)
                    try:
                        fil = int(fil)
                    except (TypeError, ValueError):
                        if not fil:
                            fil = None
                except AttributeError:
                    fil = None

                try:
                    flags = list()
                    flgs = self.mobileProviderModel.item(r, 2).data(Qt.DisplayRole).split(', ')
                    for k, v in self.PROVIDER_FLAGS.items():
                        if v in flgs:
                            flags.append(k)
                except AttributeError:
                    pass

                provs[self.mobileProviderModel.item(r, 0).data(Qt.DisplayRole)] = {'id': fil, 'flags': flags}

            mobile['provider'] = provs
            currName = self.mobileListModel.data(index, Qt.DisplayRole)
            if not currName == mobile['Name']:
                del self.projectProperties['Mobiles'][currName]
                self.mobileListModel.setData(index, mobile['Name'], Qt.DisplayRole)
            self.projectProperties['Mobiles'][mobile['Name']] = mobile

    def populateMobileWidgets(self, index):
        mobile = self.projectProperties['Mobiles'][self.mobileListModel.data(index, Qt.DisplayRole)]
        self.lineEditMobileName.setText(mobile.get('Name'))
        self.comboBoxMobileType.setCurrentIndex(self.comboBoxMobileType.findText(mobile.setdefault('type', 'BOX').upper()))
        if mobile['type'] == 'SHAPE':
            self.lineEditMobileShape.setText(str(mobile['shape']))
            self.lineEditMobileShape.setEnabled(True)
            self.doubleSpinBoxXOffset.setEnabled(True)
            self.doubleSpinBoxYOffset.setEnabled(True)
        else:
            self.lineEditMobileShape.setEnabled(False)
            self.doubleSpinBoxXOffset.setEnabled(False)
            self.doubleSpinBoxYOffset.setEnabled(False)
            self.lineEditMobileShape.clear()
        self.doubleSpinBoxMobileLength.setValue(mobile.get('length', 20.0))
        self.doubleSpinBoxMobileWidth.setValue(mobile.get('width', 5.0))
        self.checkBoxDefaultIcon.setChecked(mobile.get('defaultIcon', True))
        self.checkBoxDefIconFilled.setChecked(mobile.get('defaultIconFilled', False))
        self.doubleSpinBoxXOffset.setValue(mobile.get('offsetX', 0.0))
        self.doubleSpinBoxYOffset.setValue(mobile.get('offsetY', 0.0))
        self.spinBoxZValue.setValue(mobile.get('zValue', 100))
        self.mColorButtonMobileColor.setColor(self.getColor(mobile.get('color', 'black')))
        self.mColorButtonMobileFillColor.setColor(self.getColor(mobile.get('fillColor', 'green')))
        self.spinBoxMobileTimeout.setValue(mobile.get('timeout', 3000) / 1000)
        self.spinBoxMobileNotification.setValue(mobile.get('nofixNotify', 0))
        self.checkBoxFadeOut.setChecked(mobile.get('fadeOut', False))
        self.spinBoxTrackLength.setValue(mobile.get('trackLength', 100))
        self.mColorButtonMobileTrackColor.setColor(self.getColor(mobile.get('trackColor', 'green')))
        self.checkBoxShowLabel.setChecked(mobile.get('showLabel', False))
        r = 0
        self.mobileProviderModel.removeRows(0, self.mobileProviderModel.rowCount())
        if 'provider' in mobile:
            for k, v in mobile['provider'].items():
                try:
                    prov = QStandardItem(k)
                    self.mobileProviderModel.setItem(r, 0, prov)
                    try:
                        val = QStandardItem(str(v['id']))
                    except TypeError:
                        val = QStandardItem(str(v))         # for compatibility reasons
                    self.mobileProviderModel.setItem(r, 1, val)
                    s = ', '.join([self.PROVIDER_FLAGS[i] for i in v['flags']])
                    flags = QStandardItem(s)
                    flags.setToolTip(s)
                    self.mobileProviderModel.setItem(r, 2, flags)
                except (KeyError, TypeError, ValueError):
                    pass
                r += 1
        self.mMobileProviderTableView.resizeColumnToContents(2)

    @pyqtSlot(name='on_toolButtonRemoveMobile_clicked')
    def removeMobile(self):
        idx = self.mMobileListView.currentIndex()
        if idx.isValid():
            self.projectProperties['Mobiles'].pop(self.mobileListModel.data(idx, Qt.DisplayRole))
            self.mobileListModel.removeRows(idx.row(), 1)
            idx = self.mMobileListView.currentIndex()
            if idx.isValid():
                self.populateMobileWidgets(idx)

    @pyqtSlot(QModelIndex, name='on_mMobileProviderTableView_clicked')
    def pupulateMobileProviderWidgets(self, idx):
        if idx.isValid():
            try:
                self.comboBoxProviders.setCurrentText(self.mobileProviderModel.item(idx.row(), 0).data(Qt.DisplayRole))
                self.lineEditProviderFilter.setText(self.mobileProviderModel.item(idx.row(), 1).data(Qt.DisplayRole))
                flgs = self.mobileProviderModel.item(idx.row(), 2).data(Qt.DisplayRole)
                self.comboBoxProviderFlags.deselectAllOptions()
                if flgs:
                    self.comboBoxProviderFlags.setCheckedItems(flgs.split(', '))
            except (AttributeError, TypeError):
                pass

    @pyqtSlot(name='on_toolButtonRefreshMobileProvider_clicked')
    def refreshMobileProvider(self):
        prov = self.comboBoxProviders.currentText()
        if prov == '':
            return
        fil = None
        if self.lineEditProviderFilter.text() != '':
            fil = self.lineEditProviderFilter.text()
        flags = ', '.join(self.comboBoxProviderFlags.checkedItems())
        items = self.mobileProviderModel.findItems(prov, Qt.MatchExactly, 0)
        if items:
            for item in items:
                self.mobileProviderModel.setItem(item.row(), 1, QStandardItem(fil))
                self.mobileProviderModel.setItem(item.row(), 2, QStandardItem(flags))
        else:
            self.mobileProviderModel.appendRow([QStandardItem(prov), QStandardItem(fil), QStandardItem(flags)])

    @pyqtSlot(name='on_toolButtonRemoveMobileProvider_clicked')
    def removeMobileProvider(self):
        idx = self.mMobileProviderTableView.currentIndex()
        if idx.isValid():
            self.mobileProviderModel.removeRow(idx.row())

    @pyqtSlot(name='on_pushButtonApplyDataProvider_clicked')
    def applyDataProvider(self):
        index = self.mDataProviderListView.currentIndex()
        if index.isValid() and not self.lineEditProviderName.text() == '':
            provider = dict()
            provider['Name'] = self.lineEditProviderName.text()
            provider['DataDeviceType'] = self.comboBoxProviderType.currentText()
            if provider['DataDeviceType'] in NETWORK_TYPES:
                provider['Host'] = self.lineEditProviderHostName.text()
                provider['Port'] = self.spinBoxProviderPort.value()
                provider['ReuseAddr'] = self.checkBoxReuseAddr.isChecked()
            elif provider['DataDeviceType'] == 'SERIAL':
                provider['SerialPort'] = self.comboBoxSerialPort.currentText()
                provider['Baudrate'] = int(self.comboBoxBaudRate.currentText())
                provider['Databits'] = self.comboBoxDatabits.currentIndex() + 5
                provider['Parity'] = self.comboBoxParity.currentIndex()
                provider['Stopbits'] = self.comboBoxStopbits.currentIndex() + 1
                provider['FlowControl'] = self.comboBoxFlow.currentIndex()
            provider['Parser'] = self.comboBoxParser.currentText()
            currName = self.providerListModel.data(index, Qt.DisplayRole)
            if not currName == provider['Name']:
                del self.projectProperties['Provider'][currName]
                self.providerListModel.setData(index, provider['Name'], Qt.DisplayRole)
            self.projectProperties['Provider'][provider['Name']] = provider

    @pyqtSlot(QModelIndex, name='on_mDataProviderListView_clicked')
    def editDataProvider(self, index):
        '''
        '''
        if index.isValid():
            self.populateDataProviderWidgets(index)

    def populateDataProviderWidgets(self, index):
        provider = self.projectProperties['Provider'][self.providerListModel.data(index, Qt.DisplayRole)]
        self.lineEditProviderName.setText(provider.get('Name'))
        self.comboBoxProviderType.setCurrentIndex(self.comboBoxProviderType.findText(provider.setdefault('DataDeviceType', 'UDP').upper()))
        if provider['DataDeviceType'] in NETWORK_TYPES:
            self.stackedWidgetDataDevice.setCurrentIndex(0)
            self.lineEditProviderHostName.setText(provider.setdefault('Host', '0.0.0.0'))
            self.spinBoxProviderPort.setValue(int(provider.setdefault('Port', 2000)))
            self.checkBoxReuseAddr.setChecked(provider.setdefault('ReuseAddr', False))
        elif provider['DataDeviceType'] == 'SERIAL' and 'PyQt5.QtSerialPort' in sys.modules:
            self.stackedWidgetDataDevice.setCurrentIndex(1)
            self.comboBoxSerialPort.setCurrentText(provider.setdefault('SerialPort', ''))
            self.comboBoxBaudRate.setCurrentText(str(provider.setdefault('Baudrate', '9600')))
            self.comboBoxDatabits.setCurrentIndex(provider.setdefault('Databits', 8) - 5)
            self.comboBoxParity.setCurrentIndex(provider.setdefault('Parity', 0))
            self.comboBoxStopbits.setCurrentIndex(provider.setdefault('Stopbits', 1) - 1)
            self.comboBoxFlow.setCurrentIndex(provider.setdefault('FlowControl', 0))
        self.comboBoxParser.setCurrentIndex(self.comboBoxParser.findText(provider.setdefault('Parser', 'NONE').upper()))

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
            idx = self.mDataProviderListView.currentIndex()
            if idx.isValid():
                self.populateDataProviderWidgets(idx)

    @pyqtSlot(str, name='on_comboBoxProviderType_currentIndexChanged')
    def setProviderType(self, pType):
        if pType == 'UDP':
            self.checkBoxReuseAddr.show()
        else:
            self.checkBoxReuseAddr.hide()
        if pType == 'SERIAL':
            try:
                from PyQt5.QtSerialPort import QSerialPortInfo
                ports = QSerialPortInfo.availablePorts()
                cport = self.comboBoxSerialPort.currentText()
                self.comboBoxSerialPort.clear()
                for port in ports:
                    self.comboBoxSerialPort.addItem(port.portName())
                self.comboBoxSerialPort.setCurrentText(cport)
                self.stackedWidgetDataDevice.setCurrentIndex(1)
            except (ModuleNotFoundError, ImportError):
                self.comboBoxSerialPort.clear()
                self.stackedWidgetDataDevice.setCurrentIndex(0)
        else:
            self.stackedWidgetDataDevice.setCurrentIndex(0)

    @pyqtSlot(name='on_toolButtonSelectLogPath_clicked')
    def selectRecorderPath(self):
        path = QFileDialog.getExistingDirectory(self, self.tr('Select Recorder Path'), self.lineEditRecorderPath.text(),
                                                QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        if path != '':
            self.lineEditRecorderPath.setText(path)

    @pyqtSlot(QPoint, name='on_lineEditMobileShape_customContextMenuRequested')
    def mobileShapeContextMenu(self, pos):
        menu = QMenu(self.lineEditMobileShape)
        vesselAction = menu.addAction(self.tr('Vessel'))
        rovAction = menu.addAction(self.tr('ROV'))
        auvAction = menu.addAction(self.tr('AUV'))
        arrowAction = menu.addAction(self.tr('Arrow'))
        selectedAction = menu.exec_(self.lineEditMobileShape.mapToGlobal(pos))
        if selectedAction == vesselAction:
            self.lineEditMobileShape.setText(u'((0, -0.5), (0.5, -0.3), (0.5, 0.5), (-0.5, 0.5), (-0.5, -0.3))')
        elif selectedAction == rovAction:
            self.lineEditMobileShape.setText(u'((0.3, -0.5), (0.5, -0.3), (0.5, 0.5), (-0.5, 0.5), (-0.5, -0.3), (-0.3, -0.5))')
        elif selectedAction == auvAction:
            self.lineEditMobileShape.setText(u'((0, -0.5), (0.4, -0.3), (0.5, -0.3), (0.5, -0.2), (0.4, -0.2), (0.4, 0.3), (0.5, 0.3), (0.5, 0.4), (0.4, 0.4), (0.0, 0.5), \
             (-0.4, 0.4), (-0.5, 0.4), (-0.5, 0.3), (-0.4, 0.3), (-0.4, -0.2), (-0.5, -0.2), (-0.5, -0.3), (-0.4, -0.3))')
        elif selectedAction == arrowAction:
            self.lineEditMobileShape.setText(u'((0, -0.5), (0.5, 0.5), (0, 0), (-0.5, 0.5))')

    @pyqtSlot(name='on_buttonBox_helpRequested')
    def showHelp(self):
        """Display application help to the user."""
        help_file = os.path.join(os.path.split(os.path.dirname(__file__))[0], 'help', 'index.html')
        QDesktopServices.openUrl(QUrl.fromLocalFile(help_file))
