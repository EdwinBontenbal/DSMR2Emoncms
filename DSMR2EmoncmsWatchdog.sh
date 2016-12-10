#!/bin/bash
#
# Watchdog file for checking correct behaviour of main process
#
# Auter : Edwin Bontenbal
# Email : Edwin.Bontenbal@Gmail.COM

FILE="/tmp/DSMR2Emoncms_Watchdog"
LOGFILE="/var/log/DSMR2Emoncms_Watchdog.log"
PROCESS="python /usr/local/bin/DSMR2Emoncms.py"
TimeNow=$(date +%s)
ProcessID=$(ps -ef|grep -v grep|grep "$PROCESS"| cut -c 6-14)

WriteLog() {
        echo "$(date) $1" >> $LOGFILE
}

if [ -f "$FILE" ];
then
   # File exists
   TimeInWatchdogFile=`cat "$FILE"`
   TimeDifference=$((TimeNow-TimeInWatchdogFile))

   if [ "$TimeDifference" -gt "20" ];
   then
      # Time difference is to big  
      WriteLog "Time difference is to big ($TimeDifference), now it is $TimeNow and the file conatains $TimeInWatchdogFile)  
	if [ -z "$ProcessID" ];
      then
	 # No process found so start it
          WriteLog "No processID found, start it!"
         $PROCESS 2>&1 >/dev/null &
      else
	 # Process seems to be running, but something is wrong so kill it, and start is afterwards
         WriteLog "ProcessID ($ProcessID) found, but something is wrong, kill it hard, and start it!" 
         kill -9 "$ProcessID"
         $PROCESS 2>&1 >/dev/null &
      fi

   fi

else
   # File does not exist, start it if no process is running otherwise kill and start it
      WriteLog "Watchdog file does nog exist" 
      if [ -z "$ProcessID" ];
      then
         # No process found so start it
         WriteLog "No process found, so start the process, start it!"  
         $PROCESS 2>&1 >/dev/null &
      else
         # Process seems to be running, but something is wrong so kill it, and start is afterwards
         WriteLog "ProcessID found, but something is wrong, kill it hard, and start it!" 
         kill -9 "$ProcessID"
         $PROCESS 2>&1 >/dev/null &
      fi
fi

