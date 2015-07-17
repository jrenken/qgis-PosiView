# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PosiView
                                 A QGIS plugin
 PosiView tracks multiple mobile object and vehicles and displays its position on the canvas
                              -------------------
        begin                : 2015-06-01
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Jens Renken/Marum/University of Bremen
        email                : renken@marum.de
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt,\
    pyqtSlot, QSize
from PyQt4.QtGui import QAction, QIcon
# Initialize Qt resources from file resources.py
import resources_rc
import os.path
from posiview_project import PosiViewProject
from gui.tracking_dock import TrackingDock
from gui.guidance_dock import GuidanceDock
from gui.posiview_properties import PosiviewProperties
from gui.dataprovider_dump import DataProviderDump
from gui.position_display import PositionDisplay
from recorder import Recorder
from qgis.gui import QgsMessageBar


class PosiView:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'PosiView_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = {}
        self.menu = self.tr(u'&PosiView')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'PosiView')
        self.toolbar.setObjectName(u'PosiView')
        self.project = PosiViewProject(self.iface)

        self.tracking = TrackingDock()
        self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.tracking)
        self.tracking.hide()
        self.tracking.providerToolbar.triggered.connect(self.dumpProvider)
        self.guidance = GuidanceDock()
        self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.guidance)
        self.guidance.hide()
        self.providerDump = None
        self.positionDisplay = PositionDisplay(self.iface)
        self.recorder = None

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
        return QCoreApplication.translate('PosiView', message)

    def add_action(
        self,
        name,
        icon_path,
        text,
        callback,
        toggle_flag=False,
        enabled_flag=True,
        checkable_flag=False,
        visible_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.
        :param name: Objectname of the action. Serves also as key for the stored actions.
        :type name: str

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param toggle_flag: A flag indicating if the action should connect
            the toggled or triggered signal by default.
            Defaults to triggered (False)
        :type toggle_flag: bool

        :param checkable_flag: A flag indicating if the action should be checkable
            by default. Defaults to False.
        :type checkable: bool

        :param visible_flag: A flag indicating if the action should be displayed
            by default. Defaults to True.
        :type visible: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.setObjectName(name)
        if toggle_flag:
            action.toggled.connect(callback)
        else:
            action.triggered.connect(callback)
        action.setEnabled(enabled_flag)
        action.setCheckable(checkable_flag)
        action.setVisible(visible_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions[name] = action

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        iconPath = ':/plugins/PosiView'
        loadAction = self.add_action(
            u'loadAction',
            os.path.join(iconPath, 'icon.png'),
            text=self.tr(u'&Enable PosiView'),
            callback=self.run,
            status_tip=self.tr(u'Enable PosiView'),
            checkable_flag=True,
            parent=self.iface.mainWindow())

        trackingAction = self.add_action(
            u'trackingAction',
            os.path.join(iconPath, 'track_start.png'),
            text=self.tr(u'&Start/stop tracking'),
            callback=self.startStopTracking,
            toggle_flag=True,
            visible_flag=False,
            checkable_flag=True,
            status_tip=self.tr(u'Start/stop tracking'),
            parent=self.iface.mainWindow())

        icon = trackingAction.icon()
        icon.addFile(os.path.join(iconPath, 'track_stop.png'), QSize(), QIcon.Normal, QIcon.On)
        trackingAction.setIcon(icon)

        recordAction = self.add_action(
            u'recordAction',
            os.path.join(iconPath, 'record.png'),
            text=self.tr(u'Start/stop &recording'),
            callback=self.startStopRecording,
            toggle_flag=True,
            visible_flag=False,
            checkable_flag=True,
            status_tip=self.tr(u'Start/stop recording'),
            parent=self.iface.mainWindow())

        icon = recordAction.icon()
        icon.addFile(os.path.join(iconPath, 'record-stop.png'), QSize(), QIcon.Normal, QIcon.On)
        recordAction.setIcon(icon)

        configAction = self.add_action(
            u'configAction',
            os.path.join(iconPath, 'preferences.png'),
            text=self.tr(u'&Configure PosiView'),
            callback=self.configure,
            visible_flag=False,
            status_tip=self.tr(u'Configure PosiView'),
            parent=self.iface.mainWindow())

        loadAction.toggled.connect(trackingAction.setVisible)
        loadAction.toggled.connect(configAction.setVisible)
        loadAction.toggled.connect(recordAction.setVisible)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI.
           Unloads and removes also the project.
        """
        self.project.stopTracking()
        self.tracking.removeMobiles()
        self.tracking.removeProviders()
        self.project.unload()
        self.saveGuiSettings()
        self.iface.mainWindow().statusBar().removeWidget(self.positionDisplay)
        for action in self.actions.values():
            self.iface.removePluginMenu(
                self.tr(u'&PosiView'),
                action)
            self.iface.removeToolBarIcon(action)
        del self.toolbar

    def run(self, checked=False):
        """Load the project, display actions and tracking windows
        :param checked: decide wether to load or unload the project
        :type checked: bool
        """
        if checked:
            p = self.project.read()
            self.project.load(p)
            self.tracking.setMobiles(self.project.mobileItems)
            self.guidance.setMobiles(self.project.mobileItems)
            self.tracking.setProviders(self.project.dataProviders)
            self.recorder = Recorder(self.project.recorderPath)
            self.recorder.setMobiles(self.project.mobileItems)
            self.recorder.recordingStarted.connect(self.recordingStarted)
            self.loadGuiSettings()
            self.tracking.show()
            self.iface.mainWindow().statusBar().insertPermanentWidget(1, self.positionDisplay)
            self.positionDisplay.show()
        else:
            self.actions['trackingAction'].setChecked(False)
            self.actions['recordAction'].setChecked(False)
            self.recorder = None
            self.saveGuiSettings()
            self.tracking.removeMobiles()
            self.tracking.removeProviders()
            self.tracking.hide()
            self.guidance.hide()
            self.project.unload()
            self.iface.mainWindow().statusBar().removeWidget(self.positionDisplay)

    @pyqtSlot(bool)
    def startStopTracking(self, checked=False):
        ''' Start or stop the online tracking
        :param checked: decide wether to start or stop tracking
        :type checked: bool
        '''
        if checked:
            self.project.startTracking()
            if self.project.autoRecord:
                self.actions['recordAction'].setChecked(checked)
        else:
            self.project.stopTracking()
            self.actions['recordAction'].setChecked(checked)

    @pyqtSlot(dict)
    def onApplyConfigChanges(self, properties):
        '''Apply the changed configuration to the posiview project. The is done
           by unloading and loading again the project.
        :param properties: project configuration
        :type properties: dict
        '''
        if self.actions['loadAction'].isChecked():
            track = self.actions['trackingAction'].isChecked()
            self.actions['trackingAction'].setChecked(False)
            self.actions['recordAction'].setChecked(False)
            self.tracking.removeMobiles()
            self.tracking.removeProviders()
            self.project.unload()
            self.project.load(properties)
            self.project.store()
            self.recorder.path = self.project.recorderPath
            self.tracking.setMobiles(self.project.mobileItems)
            self.guidance.setMobiles(self.project.mobileItems)
            self.tracking.setProviders(self.project.dataProviders)
            self.recorder.setMobiles(self.project.mobileItems)
            self.actions['trackingAction'].setChecked(track)

    def configure(self):
        '''Execute the configuration dialogue and apply properties if accepted
        '''
        propDlg = PosiviewProperties(self.project)
        propDlg.applyChanges.connect(self.onApplyConfigChanges)
        result = propDlg.exec_()
        if result:
            self.onApplyConfigChanges(propDlg.projectProperties)

    def saveGuiSettings(self):
        '''Save the visibility state of the dock windows
        '''
        settings = QSettings()
        settings.beginGroup('PosiView')
        settings.setValue('Gui/TrackingVisible', self.tracking.isVisible())
        settings.setValue('Gui/GuidanceVisible', self.guidance.isVisible())
        settings.endGroup()

    def loadGuiSettings(self):
        '''Restore the visibility state of the dock windows
        '''
        settings = QSettings()
        settings.beginGroup('PosiView')
        self.guidance.setVisible(settings.value('Gui/GuidanceVisible', False) in ['True', 'true'])
        settings.endGroup()

    @pyqtSlot(str)
    def dumpProvider(self, name):
        '''Opens the dataprovider dump window which shows the raw input and the parsed output
           of a dataprovider
        :param name: name of the dataprovider to dump
        :type name: str
        '''
        try:
            provider = self.project.dataProviders[name]
            self.providerDump = DataProviderDump()
            self.providerDump.subscribeProvider(provider)
            self.providerDump.show()
        except KeyError:
            pass

    @pyqtSlot(bool)
    def startStopRecording(self, checked=False):
        '''Start or stop the position recording
        :param checked: decide wether to start or stop recording
        :type checked: bool
        '''
        if self.recorder is not None:
            if checked:
                self.recorder.startRecording()
            else:
                self.recorder.stopRecording()

    @pyqtSlot(str)
    def recordingStarted(self, fileName):
        '''Display a message with filename if recording is stated
        :param fileName: name of the recorder file
        :type name: str
        '''
        self.iface.messageBar().pushMessage(self.tr(u'PosiView Recorder'),
                self.tr(u'Recording started: ') + fileName,
                level=QgsMessageBar.INFO, duration=3)
