# DSMR2Emoncms

install emoncms on a sever for example a raspberry pi

run the following commands on a raspberry py

# Prerequisites
```sh
# Install python
apt-get install python
apt-get -y install python-pip

# Update pip
pip install --upgrade pip

# Import crcmod
pip install -U crcmod

# Import serial 
pip install -U pyserial  
```

# Install on rasberian
```sh 
cd /var/tmp
git clone -b master https://github.com/EdwinBontenbal/DSMR2Emoncms.git
cd DSMR2Emoncms/
cp DSMR2Emoncms.py /usr/local/bin/DSMR2Emoncms.py
cp DSMR2EmoncmsWatchdog.sh /usr/local/bin/DSMR2EmoncmsWatchdog.sh
mkdir /etc/DSMR2Emoncms
cp DSMR2Emoncms_default.cfg  /etc/DSMR2Emoncms/DSMR2Emoncms.cfg

```` 

add to crontab
```sh 
crontab -e
```
add
```sh 
* * * * *       /usr/local/bin/DSMR2EmoncmsWatchdog.sh
```

set logrotate
``` sh
cd /etc/logrotate.d
vi DSMR2Emoncms
```
add
``` sh
/var/log/DSMR2Emoncms_Watchdog.log /var/log/DSMR2Emoncms.log {
        daily
        rotate 7
        compress
}
```

Now change the settings in the file DSMR2Emoncms.py
```
vi /etc/DSMR2Emoncms/DSMR2Emoncms.cfg
privateKey = <YOUR APIKEY OF EMONCMS INSTANCE> 
emon_host  = <YOUR IP OF EMONCMS INSTANCE>

If needed change the serial port "ser.port" preffered method is by-id. 
ls -l /dev/serial/by-id/
# results in "usb-FTDI_USB__-__Serial-if00-port0"
ser.port     = "/dev/serial/by-id/usb-FTDI_USB__-__Serial-if00-port0"
```

 
