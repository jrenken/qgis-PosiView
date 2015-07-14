# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PosiView
                                 A QGIS plugin
 PosiView tracks multiple mobile object and vehicles and displays its position on the canvas
                             -------------------
        begin                : 2015-06-01
        copyright            : (C) 2015 by Jens Renken/Marum/University of Bremen
        email                : renken@marum.de
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""

__author__ = 'Jens Renken'
__date__ = 'June 2015'
__copyright__ = '(C) 2015, Marum, Jens Renke'

# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load PosiView class from file PosiView.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from PosiView.posi_view import PosiView
    return PosiView(iface)
