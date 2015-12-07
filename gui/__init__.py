import os
import qgis
from PyQt4 import uic

uic.widgetPluginPath.append(os.path.normpath(
    os.path.join(qgis.__path__[0], '..', 'PyQt4', 'uic', 'widget-plugins')))
