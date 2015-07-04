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

PosiView is a plugin that allows to track multiple vehicle or objects.
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
#. On Vehicle/Object page create and configure vehicle as needed.
#. Assign a provider and define a filter if a provider delivers more than one position
#. Apply changes. Providers and vehicles will be shown in the tracking window.

.. index:: Tracking

Tracking
==================

#. Start online tracking. 
#. Open guidance window and select two vehicles/object to see distances and bearing. A compass is visible if the windows lower edge is pulled down.

.. Indices and tables

==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

