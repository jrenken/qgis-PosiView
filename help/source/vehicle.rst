:orphan:

=====================================
Configuring a vehicle/object in depth
=====================================

**Go to the Mobiles/Vehicles tab.**

  .. image:: _static/config_vehicles.png
      :align: center

  .. index:: Vehicles; in depth

  #. Click the + button to create a new vehicle.
  #. Enter a unique name for the vehicle.
  #. Choose an appearance type: BOX, CROSS, X, or a custom shape.
  #. If using a custom shape, define its outline as a Python array of points in the format: ((x1, y1), (x2, y2), …, (xn, yn)).
     Right-click to select from predefined shapes. The shape should be normalized to (1, 1) in size, with a heading of 0° pointing upward.
  #. Enter the vehicle’s real-world size.
  #. To ensure visibility, the vehicle is not scaled down at small map scales. Instead, it may be replaced with a default icon for clarity.
  #. If the reference point is not the center (0, 0) of the shape, specify the offsets toward the bow and starboard.
  #. The Z-value determines the drawing order on the canvas. Vehicles with higher Z-values appear on top.
  #. Select colors for the outline and fill. Adjust transparency as needed.
  #. Set a timeout duration for incoming position messages. If a timeout occurs, the corresponding panel in the tracking dock turns red.
     If a notification timeout is set, a notification message will be triggered.
  #. Select the timeout behavior. If enabled, the vehicle will fade out when a timeout occurs.
  #. Choose the color and length of the track.
  #. Enable or disable the vehicle label.
  #. If enabled, additional text can be displayed (provided by the data source using the ``text`` key).
  #. Choose whether to store positions in a layer. If selected, a memory layer will be created (or assigned if one already exists).
  #. Enable ``Repaint`` to update the layer after each new point is added. **Warning**: This increases processing load.
  #. Select a provider from the list. If the provider supplies multiple position reports (e.g., USBL systems), apply a filter (e.g., Beacon ID for USBL or MMSI for AIS).
     Advanced filters allow finer control (e.g., ignoring course, displaying COG as heading or processing easting/northing positions).
     Click Refresh List to update available providers.
  #. Click on ``Apply Properties``

==================

* :ref:`genindex`
* :ref:`search`
  
  