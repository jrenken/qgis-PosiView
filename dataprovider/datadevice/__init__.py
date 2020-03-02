# -*- coding: utf-8 -*-
###############################################################################
#
# Copyright (C) 2015 Jens Renken (renken@marum.de)
#
# This source is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This code is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
###############################################################################

from .datadevice import DataDevice
from .udpdevice import UdpDevice
from .tcpdevice import TcpDevice

try:
    from PyQt5 import QtSerialPort
    from .serialdevice import SerialDevice
    DEVICE_TYPES = ('UDP', 'TCP', 'GPSD', 'SERIAL')
except (ModuleNotFoundError, ImportError):
    DEVICE_TYPES = ('UDP', 'TCP', 'GPSD')

NETWORK_TYPES = ('UDP', 'TCP', 'GPSD')


def createDataDevice(params={}, parent=None):
    deviceType = params.get('DataDeviceType', 'UDP').upper()
    if deviceType == 'UDP':
        return UdpDevice(params, parent)
    elif deviceType == 'TCP':
        return TcpDevice(params, parent)
    elif deviceType == 'GPSD':
        params['GpsdInit'] = True
        return TcpDevice(params, parent)
    elif deviceType == 'SERIAL':
        if 'SERIAL' in DEVICE_TYPES:
            return SerialDevice(params, parent)
    return DataDevice(params, parent)
