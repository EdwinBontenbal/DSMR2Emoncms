# DSMR2Emoncms

prerequisites
```sh
apt-get install python
apt-get install pip
```


Install on rasberian
cd /var/tmp
git clone -b master https://github.com/EdwinBontenbal/DSMR2Emoncms.git
cd DSMR2Emoncms/
cp DSMR2Emoncms.py /usr/local/bin/DSMR2Emoncms.py
cp DSMR2EmoncmsWatchdog.sh /usr/local/bin/DSMR2EmoncmsWatchdog.sh

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
