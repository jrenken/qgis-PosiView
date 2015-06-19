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
    pyqtSlot
from PyQt4.QtGui import QAction, QIcon
# Initialize Qt resources from file resources.py
import resources_rc
import os.path
from posiview_project import PosiViewProject
from gui.tracking_dock import TrackingDock
from gui.guidance_dock import GuidanceDock
from gui.posiview_properties import PosiviewProperties



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
        self.actions = []
        self.menu = self.tr(u'&PosiView')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'PosiView')
        self.toolbar.setObjectName(u'PosiView')
        self.project = PosiViewProject(self.iface)
        
        self.tracking = TrackingDock()
        self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.tracking)
        self.tracking.hide()
        self.guidance = GuidanceDock()
        self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.guidance)
        self.guidance.hide()

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
        icon_path,
        text,
        callback,
        enabled_flag=True,
        checkable_flag=False,
        visible_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

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

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        iconPath = ':/plugins/PosiView'
        self.loadAction = self.add_action(
            os.path.join(iconPath, 'icon.png'),
            text=self.tr(u'Enable PosiView'),
            callback=self.run,
            status_tip=self.tr(u'Enable PosiView'),
            checkable_flag=True,
            parent=self.iface.mainWindow())
        
        startAction = self.add_action(
            os.path.join(iconPath, 'icon.png'),            
            text=self.tr(u'Start Tracking'),
            callback=self.startTracking,
            visible_flag=False,
            status_tip=self.tr(u'Start tracking'),
            parent=self.iface.mainWindow())

        stopAction = self.add_action(
            os.path.join(iconPath, 'icon.png'),
            text=self.tr(u'Stop Tracking'),
            callback=self.stopTracking,
            visible_flag=False,
            status_tip=self.tr(u'Stop tracking'),
            parent=self.iface.mainWindow())

        configAction = self.add_action(
            os.path.join(iconPath, 'icon.png'),
            text=self.tr(u'Configurem PosiView'),
            callback=self.configure,
            visible_flag=False,
            status_tip=self.tr(u'Configure PosiView'),
            parent=self.iface.mainWindow())

        self.loadAction.toggled.connect(startAction.setVisible)
        self.loadAction.toggled.connect(stopAction.setVisible)
        self.loadAction.toggled.connect(configAction.setVisible)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI.
           Unloads and removes also the project.
        """
        self.project.unload()
        self.saveGuiSettings()
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&PosiView'),
                action)
            self.iface.removeToolBarIcon(action)
        del self.toolbar

    def run(self, checked=False):
        """Run method that performs all the real work"""
        if checked:
            p = self.project.read()
            self.project.load(p)            
            for item in self.project.mobileItems.values():
                self.tracking.addMobile(item)
            self.guidance.setMobiles(self.project.mobileItems)
            self.loadGuiSettings()
            self.tracking.show()
        else:
#             self.project.store()
            self.saveGuiSettings()
            self.tracking.removeMobiles()
            self.tracking.hide()
            self.guidance.hide()
            self.project.unload()

    def startTracking(self):
        self.project.startTracking()
        
    def stopTracking(self):
        self.project.stopTracking()
    
    @pyqtSlot(dict)
    def onApplyConfigChanges(self, properties):
        print "Config apply"
        if self.loadAction.isChecked():
            self.tracking.removeMobiles()
            self.project.unload()
            self.project.load(properties)
            self.project.store()
            for item in self.project.mobileItems.values():
                self.tracking.addMobile(item)
            self.guidance.setMobiles(self.project.mobileItems)

    
    def configure(self):
        propDlg = PosiviewProperties(self.project)
        propDlg.applyChanges.connect(self.onApplyConfigChanges)
        result = propDlg.exec_()
        if result:
            self.onApplyConfigChanges(propDlg.projectProperties)

    def saveGuiSettings(self):
        settings = QSettings()
        settings.beginGroup('PosiView')
        settings.setValue('Gui/TrackingVisible', self.tracking.isVisible())
        settings.setValue('Gui/GuidanceVisible', self.guidance.isVisible())
        settings.endGroup()

    def loadGuiSettings(self):
        settings = QSettings()
        settings.beginGroup('PosiView')
#         self.tracking.setVisible(settings.value('Gui/TrackingVisible', True) in ['True', 'true'])
        self.guidance.setVisible(settings.value('Gui/GuidanceVisible', False)  in ['True', 'true'])
        settings.endGroup()
