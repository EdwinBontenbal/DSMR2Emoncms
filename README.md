# DSMR2Emoncms

install emoncms on a sever

run the following commands on a raspberry py

prerequisites
```sh
apt-get install python
apt-get install pip
```


Install on rasberian
```sh 
cd /var/tmp
git clone -b master https://github.com/EdwinBontenbal/DSMR2Emoncms.git
cd DSMR2Emoncms/
cp DSMR2Emoncms.py /usr/local/bin/DSMR2Emoncms.py
cp DSMR2EmoncmsWatchdog.sh /usr/local/bin/DSMR2EmoncmsWatchdog.sh
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

Now change the setting in the file DSMR2Emoncms.py
```
emon_privateKey="QQQ insert your key here"
emon_node="QQQ insert your node here" 
emon_host = "QQQ insert your ip-adress of you emoncms install here"
```

 
