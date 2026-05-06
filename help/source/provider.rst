:orphan:

===============================
Configuring a provider in depth
===============================

**Configuration dialog**

  Open the configuration dialog and select the provider tab.

  .. index:: Provider; in depth

  .. image:: _static/config_provider.png
      :align: center

  #. To create a new provider, click the ``+``-Button.
  #. Assign a unique name.
  #. Select a device type from the following options:
     
     * UDP server socket
     * TCP client socket
     * TCP server
     * GPSD client, a TCP client for gpsd
     * SERIAL port (requires python module PyQt5.QtSerialPort)
     
  #. Specify the host address. For UDP sockets "0.0.0.0" is recommended, as it binds the socket to all available interfaces.
  #. Enter the port number. For UDP sockets, enable the SO_REUSEADDR socket option if you need to share datagrams across multiple applications.
  #. Alternatively, if using a serial port, configure the following settings: device, baud rate, data format and flow control.
  #. Select a parser. The following parsers are currently available: :doc:`protocol`

        ==============  ===============================================================  ============================= 
        Parser          Description                                                      Records
        ==============  ===============================================================  =============================
        IX_USBL         IXBlue USBL systems like GAPS or Posidonia                       $PTSAG, $PTSAH, $HEHDT
        PISE            Record used by ISE for their vehicles                            $PISE
        MINIPOS         Saab MiniPos3 output                                             $PSAAS
        GPS             Standard GPS sentences                                           $__RMC, $__GLL, $__VTG, $__GGA, $__HDT
        RANGER2         Sonardyne USBL system Ranger2                                    $PSONLLD, $PSONALL
        CP16            CP-16 compass                                                    $PCI
        AIS             Automatic Identification System                                  !AIVDM, !AIVDO
        MARUM           MARUM's own sentences                                            $PMTM___
        TARGET_POS      Simple non NMEA string containing Id, Lat, Lon and opt. values
        COMPASS         Heading and attitude provided by compass modules                 $C, $__HDT, $__HDM
        MOOS NODEREP    Report string from MOOS-IvP https://oceanai.mit.edu/moos-ivp
        ==============  ===============================================================  =============================
    
  #. Click  ``Apply Properties``
  #. Next, proceed with configuring vehicles/objects in detail:  :doc:`vehicle`
  

.. Indices and tables

==================

* :ref:`genindex`
* :ref:`search`
  
