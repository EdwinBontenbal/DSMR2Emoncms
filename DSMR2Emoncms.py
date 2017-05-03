#This utility send a P1 (smartmeter) telegram to emoncsm
#  
# coded by:
# Auteur : Edwin Bontenbal
# Email  : Edwin.Bontenbal@Gmail.COM 
version = "v1.05"
# VERSION    DATE        ADDED FUNCTIONALITY
# 1.05	     03-05-2017  Config file added	


# if errors during executing this scrip make sure you installed phyton and the required modules/libraries
import ConfigParser
import serial
import datetime
import time
import logging
import re
import json
import crcmod
import urllib2

# Set variables for logging
LogFile              = "/var/log/DSMR2Emoncms.log"
LogFileLastTelegram  = "/tmp/DSMR2Emoncms_p1Telegram.log"
WatchdogFile         = "/tmp/DSMR2Emoncms_Watchdog"

# Set logging params
logging.basicConfig(filename=LogFile,format='%(asctime)s %(message)s',level=logging.DEBUG)

# Open and read config file
Config = ConfigParser.ConfigParser()
Config.read("/etc/DSMR2Emoncms/DSMR2Emoncms.cfg")

def ConfigSectionMap(section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            logging.debug("Reading config file : " + section + "," + option + " = " +  dict1[option] )
        except:
            dict1[option] = None
    return dict1

# Set emoncms variables
emon_privateKey = ConfigSectionMap("emoncms")['privatekey']
emon_node       = ConfigSectionMap("emoncms")['node']
emon_host       = ConfigSectionMap("emoncms")['host']
emon_protocol   = ConfigSectionMap("emoncms")['protocol']
emon_url        = ConfigSectionMap("emoncms")['url']

# Set COM port config
ser          = serial.Serial()
ser.baudrate = 115200
ser.bytesize = serial.EIGHTBITS
ser.parity   = serial.PARITY_NONE
ser.stopbits = serial.STOPBITS_ONE
ser.xonxoff  = 1
ser.rtscts   = 0
ser.timeout  = 20
ser.port     = ConfigSectionMap("serial")['port']

DSMR_List = [ [    "NightConsumption",  "1-0:1\.8\.1",            "\d{6}\.\d{3}", "NachtGebruik"    ] ] 
DSMR_List.append (["DayConsumption",    "1-0:1\.8\.2",            "\d{6}\.\d{3}", 'DagGebruik'      ] )  
DSMR_List.append (["NightGenerated",    "1-0:2\.8\.1",            "\d{6}\.\d{3}", 'NachtLevering'   ] )  
DSMR_List.append (["DayGenerated",      "1-0:2\.8\.2",            "\d{6}\.\d{3}", 'DagLevering'     ] )  
DSMR_List.append (["GasConsumption",    "0-1:24\.2\.1\(\d+\w\)",  "\d{5}\.\d{3}", 'GasGebruik'      ] )  
DSMR_List.append (["ActualTarif",       "0-0:96\.14\.0",          "\d{4}"       , 'ActueleTarief'   ] )  
DSMR_List.append (["ActualConsumption", "1-0:1\.7\.0",            "\d{2}\.\d{3}", 'ActueleGebruik'  ] )  
DSMR_List.append (["ActualGenerated",   "1-0:2\.7\.0",            "\d{2}\.\d{3}", 'ActueleLevering' ] )  


###############################################################################################################
# Main program
###############################################################################################################

# Initialize
p1_telegram  = False
p1_timestamp = ""
p1_log       = True

p1_complete_telegram_raw = ""
p1_complete_telegram     = ""

#Show startup arguments 
logging.warning("Port: (%s)" % (ser.name))

#Open COM port
try:
    ser.open()
except:
    sys.exit ("Error opening port %s. "  % ser.name)      
    logging.warning("Error opening port %s. "  % ser.name)

while p1_log:
    try:
        p1_raw = ser.readline()
    except:
        sys.exit ("Error readig port %s. " % ser.name )
        logging.warning("Error reading port %s. "  % ser.name)
        ser.close()

    p1_complete_telegram_raw += p1_raw 

    # see if telegram contains the complete telegram
    if re.search('/.*!\w{4}', p1_complete_telegram_raw, re.DOTALL ) != None :
       logging.warning("Telegram found") 
       # filter complete telegram 
       found_telegram = re.search('.*(?P<Y>/.*!\w{4})', p1_complete_telegram_raw, re.DOTALL ).group(1)
      
       # write time to watchdog file  
       f3=open(WatchdogFile, "w")
       timestamp = int(time.time())
       f3.write (str(timestamp))
       f3.close()

       # write telegram to file
       f1=open(LogFileLastTelegram, "w")
       f1.write (found_telegram)
       f1.close  

       logging.debug(p1_complete_telegram_raw)

       # get crc from telegram
       crc_in_telegram = re.search(r".*!(?P<Y>.{4})" , found_telegram, re.DOTALL).group(1) 

       # calculate crc of recieved telegram
       crcstring = re.search(r'(?P<Y>\/.*!)' , found_telegram, re.DOTALL)
       crc16 = crcmod.predefined.mkPredefinedCrcFun('crc16')
       crc_calculated = re.search(r'0X(?P<Y>\w{0,4})', hex(crc16(crcstring.group(1))).upper()).group(1) 

       # if calculated crc are equal then parse telegram and construct json string 
       if crc_calculated.lstrip("0") == crc_in_telegram.lstrip("0"): 
             logging.debug("ok    checksum. Calculated checksum: "+ crc_calculated + " checksum telegram: " + crc_in_telegram)
             DataJson = {}   
             for x in range(len(DSMR_List)):  
              matchObj = re.search(r"" + DSMR_List[x][1] + "\((?P<Y>" + DSMR_List[x][2] + ")" , p1_complete_telegram_raw, re.DOTALL)
              # if object has been found process it 
              if matchObj != None : 
               logging.debug("Item found     : " + DSMR_List[x][1])
               DataJson[DSMR_List[x][3]] =float(matchObj.group(1)) 
              else:
               logging.debug("Item NOT found : " + DSMR_List[x][1])
 
             url  = emon_protocol + emon_host + emon_url + "node=" + emon_node + "&apikey=" + emon_privateKey + "&json=" + str( json.dumps(DataJson, separators=(',', ':')))
             logging.debug(url)
             HTTPresult = urllib2.urlopen(url)
             logging.debug("Response code : " +  str(HTTPresult.getcode()))

             p1_complete_telegram_raw = ""
       else:
             logging.debug("wrong checksum. Calculated checksum: "+ crc_calculated + " checksum telegram: " + crc_in_telegram)
             p1_complete_telegram_raw = ""

#Close port and show status
try:
    ser.close()
except:
    sys.exit ("Error closing port, program terminated %s. " % ser.name )      
    logging.warning("Error closing port, program terminated %s. "  % ser.name)
