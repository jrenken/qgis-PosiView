:orphan:

===============================
Protocol description of available sentences
===============================

**IX_BLUE**

* $PTSAG,#NNNNN,hhmmss.sss,jj,mm,aaaa,BBB,DDMM.MMMM,H,DDDMM.MMMM,D,A,MMMM.M,A, MMMM.M*hh<CR><LF>
 $PTSAG,<frame number>,<time>,<day>,<month>,<year>,<beacon id>,<latitude>,<hemisphere>,<longitude>,<direction>,<validity>,<calculated depth>,<sensor depth>*hh<CR><LF>
* $PTSAH,0,DDD.DD,SS.SS*hh<CR><LF>
 $PTSAH,0,<heading>,<SOG>*hh<CR><LF>
* $HEHDT,x.xxx,T*hh<CR><LF>
 $HEHDT,<heading>,T*hh<CR><LF>
 
**PISE**

* $PISE,AUV,49.234567,-122.543211,20030716,122554,1,0000,074,0048,02.3*7d
 $PISE,<source>,<Latitude>,<Longitude>,<date>,<time>,<position_source>,<false>,<heading>,<depth>,<speed>*hh<CR><LF>
 
**MINIPOS**

* $PSAAS,101301.06,5832.74,N,01458.52,E,176.3,4.3,4.8,1.20,-1.00,-0.30*54<CR><LF>
 $PSAAS,<time>,<latitude>,<hemisphere>,<longitude>,<direction>,<depth>,<altitude>,<heading><velforw>,<velport>,<velup>*hh<CR><LF>
 
**GPS**
 https://www.gpsinformation.org/dale/nmea.htm

**RANGER2**

* $PSONLLD,153005.253,24,A,50.02495,8.873323,425.3,,,,,,,,*3e<CR><LF>
 $PSONLLD,<time>,<id>,<status>,<laatitude>,<longitude>,<depth>,,,,,,,,*hh<CR><LF>
* $PSONALL,Ship 1,CRP,134446.175,650879.00,5688874.16,0.00,180.00,,G,0.00,0.00,,0.109,0.001*51<CR><LF>
 $PSONALL,<name>,<offset>,<time>,<easting>,<northing>,<depth>,<heading>,<CMG>,<heading type>,<pitch>,<roll>,<velocity>,<pos accuratcity>,<depth accuracity>*hh<CR><LF>
 
**CP16**

* $PCI,<depth meter>,<depth feet>,<heading>,<CP data>,<pitch>,<roll><CR><LF>

**AIS**
 http://catb.org/gpsd/AIVDM.html
 
**MARUM**

* $PMTMGPO,HROV,180702,092343.92,-53.1234567,-152.1234567,P,0234.5,018.2,270*3B\r\n
 $PMTMGPO,<sender>,<date>,<time>,<Latitude>,<Longitude>,<position_source>,<depth>,<altitude>,<heading>*hh<CR><LF>
* $PMTMATT,HROV,1.2,3.5,273.4*6F
 $PMTMATT,<sender>,<pitch>,<roll>,<heading>*<checksum>
* $PMMTSPD,HROV,0.4,0.6,0.3*6F
 $PMTMSPD,HROV,<forward_speed><port_speed><up_speed>

**TARGET_POS**

* <target><latitude><longitude>[,<depth>,<altitude>,<heading>]<CR><LF>
 person1,53.625827,8.736457<CR><LF>
 