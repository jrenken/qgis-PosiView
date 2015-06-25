# PosiView Plugin

PosiView tracks multiple vehicles and movable objects reporting
their position via USBL, GPS or other navigation devices.


## Features

The Plugin reads usually NMEA formatted data from USBL or other navigation devices
and displays the object as scaled symbols on the canvas.

Additionally the positions are displayed in several docked windows.

The main intention of this plugin is to turn QGIS into a navigation software
for underwater devices.

## Installation

### via git

* Clone the repository
* Execute "make deploy"

### via repo server

Not available for the moment.

## Quickstart

* Enable plugin
* Open configuration dialog
* Create one or more dataprovider and select a suitable parser
* Create one or more mobile/vehicles and assign the corresponding dataprovider
* Start tracking
* In the guidance dock select the vehicles to see distance and heading

## Future extensions

* Datalogging
* Dashboard with compass
* Logging events/targets on a seperate layer


## License

```
    PosiView tracks multiple vehicles and movable objects reporting
    their position via USBL, GPS or other navigation devices.

    Copyright (C) 2015 MARUM - Center for Marine Environmental Sciences

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
