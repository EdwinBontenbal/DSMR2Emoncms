#
#Thiss utility send a P1 (smartmeter) telegram to emoncsm 
#  
# coded by:
# auteur : Edwin Bontenbal
# Email : Edwin.Bontenbal@Gmail.COM 
version = "v1.00"

import sys
import os
import stat
import serial
import datetime
import locale
import requests
import time
import logging

emon_privateKey="649a259114fbd741c3f95b64038d5fd1"
emon_node="99"

emon_host = "192.168.1.212";
emon_url  = "/emoncms/input/post.json?node=";

emon_ID_NachtGebruik    = "NachtGebruik:";
emon_ID_DagGebruik      = "DagGebruik:";
emon_ID_NachtLevering   = "NachtLevering:";
emon_ID_DagLevering     = "DagLevering:"; 
emon_ID_GasGebruik      = "GasGebruik:";
emon_ID_ActueleTarief   = "ActueleTarief:";
emon_ID_ActueleGebruik  = "ActueleGebruik:";
emon_ID_ActueleLevering = "ActueleLevering:";

###############################################################################################################
# Main program
###############################################################################################################

#Initialize
p1_telegram  = False
p1_timestamp = ""
p1_teller    = 0
p1_log       = True

#Set COM port config
ser          = serial.Serial()
ser.baudrate = 115200
ser.bytesize = serial.EIGHTBITS
ser.parity   = serial.PARITY_NONE
ser.stopbits = serial.STOPBITS_ONE
ser.xonxoff  = 1
ser.rtscts   = 0
ser.timeout  = 20
ser.port     = "/dev/serial/by-id/usb-FTDI_USB__-__Serial-if00-port0"
#ser.port     = "/dev/ttyUSB0"

LogFile              = '/var/log/DSMR2Emoncms.log'
LogFileLastTelegram  = "/tmp/DSMR2Emoncms_p1Telegram.log"
WatchdogFile         = "/tmp/DSMR2Emoncms_Watchdog"

logging.basicConfig(filename=LogFile,format='%(asctime)s %(message)s',level=logging.DEBUG)

#Show startup arguments 
print ("Poort: (%s)" % (ser.name) )

#Open COM port
try:
    ser.open()
except:
    sys.exit ("Error opening port %s. "  % ser.name)      
    logging.warning("Error opening port %s. "  % ser.name)

while p1_log:
    p1_line = ''
    try:
        p1_raw = ser.readline()
    except:
        sys.exit ("Error readig port %s. " % ser.name )
        logging.warning("Error reading port %s. "  % ser.name)
        ser.close()

    p1_str  = p1_raw
    p1_line = p1_str.strip()
    print (p1_line)

    # fill variables   
    if p1_line[0:9] == "1-0:1.8.1":
       NachtGebruik =  p1_line[11:20]
    if p1_line[0:9] == "1-0:1.8.2":
       DagGebruik =  p1_line[11:20]
    if p1_line[0:9] == "1-0:2.8.1":
       NachtLevering =  p1_line[11:20]
    if p1_line[0:9] == "1-0:2.8.1":
       DagLevering =  p1_line[11:20]
    if p1_line[0:11] == "0-0:96.14.0":
       ActueleTarief =  p1_line[13:16]
    if p1_line[0:9] == "1-0:1.7.0":
       ActueleGebruik =  p1_line[11:16]
    if p1_line[0:9] == "1-0:2.7.0":
       ActueleLevering =  p1_line[11:16]
    if p1_line[:10] == "0-1:24.2.1":
       GasGebruik =  p1_line[27:35]

    # if start of telegram has been found
    if p1_line[0:1] == "/":
        p1_telegram = True
        p1_teller   = p1_teller + 1
        f3=open(WatchdogFile, "w")
        f1=open(LogFileLastTelegram, "w")
        timestamp = int(time.time())
        print (timestamp)
        f3.write (str(timestamp))
        f3.close()

    # if end of telegram has been found
    elif p1_line[0:1] == "!":
        if p1_telegram:
            p1_teller   = 0
            p1_telegram = False 
            f1.write (p1_line)
            f1.write ('\r\n')
            f1.close  
            logging.info(p1_line)
            os.chmod(LogFileLastTelegram, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

            url = emon_url + emon_node + "&json={"
            if (NachtGebruik> 0):
              url += emon_ID_NachtGebruik + str(float(NachtGebruik)) + ","
            if (DagGebruik> 0):
              url += emon_ID_DagGebruik + str(float(DagGebruik)) + ","
            if (NachtLevering> 0):
              url += emon_ID_NachtLevering + str(float(NachtLevering)) + ","
            if (DagLevering> 0):
              url += emon_ID_DagLevering + str(float(NachtLevering)) + ","
            if (GasGebruik> 0):
              url += emon_ID_GasGebruik + str(float(GasGebruik)) + ","
            if (ActueleTarief> 0):
              url += emon_ID_ActueleTarief + str(int(ActueleTarief)) + ","
            if (ActueleGebruik> 0):
              url += emon_ID_ActueleGebruik + str(float(ActueleGebruik)) + ","
            if (ActueleLevering> 0):
              url += emon_ID_ActueleLevering + str(float(ActueleLevering))

            url += "}&apikey=" + emon_privateKey

            print "http://" + emon_host + url

            r=requests.get("http://" + emon_host + url)
            print r.status_code

    if p1_telegram:
        logging.info(p1_line)
        f1.write (p1_line)
        f1.write ('\r\n')

#Close port and show status
try:
    ser.close()
except:
    sys.exit ("Error closing port, program terminated %s. " % ser.name )      
    logging.warning("Error closing port, program terminated %s. "  % ser.name)


