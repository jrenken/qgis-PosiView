.. PosiView documentation master file, created by
   sphinx-quickstart on Sun Feb 12 17:11:03 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

PosiView multi vehicle/object tracking tool
============================================


.. toctree::
   :maxdepth: 2
   
.. index:: Concpets



Concepts
==================

PosiView is a plugin that allows to track multiple vehicles and objects.
It accepts position and other data usually provided in NMEA format from devices 
like GPS, USBL systems or other systems.

Connection to those devices is established by data provider
connecting to network sockets (UDP/TCP). 
Future alternatives like file based inputs are planned.

.. index:: Configuaration
 
Configuration
==================

#. Enable PosiView and open configuration dialog
#. On Provider page create and configure providers as needed.
  * First add a new provider, give it a unique name and select the properties.
  * Don't forget to apply the changes.
#. On Vehicle/Object page create and configure vehicle as needed.
  * First add a new vehicle, give it a unique name and select the properties.
  * Select a type. For shape types a template shape can be selected by right clicking on the shape line edit. If needed modify the shape by hand.
  * For shape types set the real world size.
  * Select colors for outline, fill and track color.
  * The Z-value defines the vertical painting order.
  * Assign one ore more data providers. If a provider provides more then one position a filter is needed. This could be a beacon id or a string.
  * Don't forget to apply the changes.
#. Apply changes. Providers and vehicles will be shown in the tracking window.

.. index:: Tracking

Tracking
==================

#. Start online tracking. 
#. Open guidance window and select two vehicles/object to see distances and bearing. A compass is visible if the windows lower edge is pulled down.

.. index:: Recording

Recording
==================

#. Position and bearing of the vehicles and objects can be recorded to a text file. All objects are merged into one file. After 10000 lines a new file is created.
#. In properties dialogue select a path where to put the files.
#. Recording can be started automatically on tracking start or manually.

.. Indices and tables

==================

* :ref:`genindex`
* :ref:`search`

