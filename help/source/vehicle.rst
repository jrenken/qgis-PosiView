:orphan:

=====================================
Configuring a vehicle/object in depth
=====================================

**Configuration dialog**

  Go to the Mobiles/Vehicles tab.

  .. image:: _static/config_vehicles.png
      :align: center

  .. index:: Vehicles; in depth

  #. Create a new vehicle  by clicking the ``+``-Button.
  #. Enter a unique name.
  #. Select an appearance, which can be BOX, CROSS, X or a shape.
  #. If a shape is used, select the outline as Python array of points in the form ((x1, y1), (x2, y2), ..., (xn, yn)).
     Right mouse click offers a selection of predefined shapes. The size of the shape should be normalised to (1, 1). A heading of zero points upwards.
  #. Enter the real world size of the vehicle.
  #. The vehicle is not scaled at small map scales so that it remains visible. To make this clear, the shape can be replaced by a default icon. 
  #. If the position reference point is not the center (0, 0) of the shape, enter the offsets towards bow and starboard.
  #. The Z-value defines the drawing order on the canvas. Vehicles with higher values are drawn on top.
  #. Select colors for outline and fill brush. Transparency can be applied.
  #. Select the timeout for incoming position messages. 
     The corresponding panel in the tracking dock turns red when a timeout occurs.
     A notification message is triggered if notification timeout is set.
  #. Select the timeout behavior. If checked, the vehicle will be faded out when a timeout occurs.
  #. Select the color and length of the track.
  #. Select wether the vehicle should be labeled.
  #. If the label is enabled, extra text can be shown. Text must be provided by the data provider using the 'text' key.
  #. Select whether a layer should be used to store the position. If so, a memory layer will be created or, if already available, assigned.
  #. Select ‘Repaint’ if the layer is to be updated after each point is added. But be careful: this increases the processing power required.
  #. Select a provider from the list. If a provider supplies multiple position reports, as is the case with USBL systems, enter a filter.
     Depending on the parser used, this can be the Beacon ID (USBL) or the MMSI (AIS).
     Advanced filters allow for more precise control over the data to be processed, e.g. ignoring the course or displaying the course (COG) as the heading.
     Finally, refresh the list.
  #. Click on ``Apply Properties``

==================

* :ref:`genindex`
* :ref:`search`
  
  