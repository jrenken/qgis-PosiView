import os

if os.name == 'nt':
    ''' Workaround for windows platform.
            Currently the qgis_customwidgets plugin is moved from
            the directory where it is searched to another directory.
            I don't know why
    '''

    import qgis
    from PyQt4 import uic

    uic.widgetPluginPath.append(os.path.normpath(
        os.path.join(qgis.__path__[0], '..', 'PyQt4', 'uic', 'widget-plugins')))
