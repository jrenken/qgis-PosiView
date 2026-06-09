# PosiView Plugin

PosiView is a plugin that allows you to track multiple vehicles and objects.

## Features

The plugin processes position and orientation data, typically provided in NMEA-0183 format by devices such as GPS, USBL systems, or other sensors, and displays the object as scaled symbol on the canvas. The connection to these devices is established via data providers, which link to network sockets (UDP/TCP) or serial interfaces.

Additionally the positions are displayed in several docked windows.

The main intention of this plugin is to turn QGIS into navigation software
for underwater equipment.

## Installation

#### via git

* Clone the repository
* Execute "make deploy"

#### via repo server

* Go to plugin manager and install PosiView

## Quickstart

* Enable plugin
* Open configuration dialog
* Create one or more dataprovider and select a suitable parser
* Create one or more mobiles/vehicles and assign the corresponding dataprovider
* Start tracking
* In the guidance dock select the vehicles to see distance and bearing

## Features

* Datalogging
* Writing the track data to point layers
* Following tool


## License

```
    PosiView tracks multiple vehicles and movable objects reporting
    their position via USBL, GPS or other navigation devices.

    Copyright (C) 2015-2026 MARUM - Center for Marine Environmental Sciences, University of Bremen

    PosiView Plugin is free software: you can redistribute it and/or
    modify it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with PosiView Plugin.  If not, see <http://www.gnu.org/licenses/>.
```
