:orphan:

===============================
Configuring a provider in depth
===============================

**Configuration dialog**

  Open the configuration dialog and select the provider tab.

  .. index:: Provider; in depth

  .. image:: _static/config_provider.png
      :align: center

  #. Create a new provider by clicking on the ``+``-Button.
  #. Assign a unique name.
  #. Select a device type, which is one of these:.

     * UDP server socket
     * TCP client socket
     * GPSD client, a TCP client for GPS daemon
     * SERIAL serial port (requires python module PyQt5.QtSerialPort)
  
  #. Select the host address. For UDP sockets 0.0.0.0 listens on any available interfaces. 
  #. Select the portnumber. For UDP sockets the socket option SO_REUSEADDR can be set for sharing datagrams across several applications.
  #. Or configure device, baud rate, data format and flow control of a serial port.
  #. Select a parser. Following parsers are available up to now: :doc:`protocol`

        ==========  ===============================================================  ============================= 
        Parser      Description                                                      Records
        ==========  ===============================================================  =============================
        IX_USBL     IXBlue USBL systems like GAPS or Posidonia                       $PTSAG, $PTSAH, $HEHDT
        PISE        Record used by ISE for their vehicles                            $PISE
        MINIPOS     Saab MiniPos3 output                                             $PSAAS
        GPS         Standard GPS Sentences                                           $__RMC, $__GLL, $__VTG, $__GGA
        RANGER2     Sonardyne USBL system Ranger2                                    $PSONLLD, $PSONALL
        CP16        CP-16 compass                                                    $PCI
        AIS         Automatic Identification System                                  !AIVDM, !AIVDO
        MARUM       Marum's own sentences                                            $PMTM___
        TARGET_POS  Simple non NMEA string containing Id, Lat, Lon and opt. values
        ==========  ===============================================================  =============================
    
  #. Click  ``Apply Properties``
  #. Continue with creating vehicles:  :doc:`vehicle`
  

.. Indices and tables

==================

* :ref:`genindex`
* :ref:`search`
  
