#!/bin/bash

# takes the group name and enable disable and status as input and 
# updates the pihole gravity database accordingly
# then restarts the pihole dns and lists

# Data Monkey January 2021


case "$2" in
   "enable")
       sqlite3 /etc/pihole/gravity.db "update 'group' set 'enabled'=1 where name='$1'";
       # refresh PiHole
       /usr/local/bin/pihole restartdns reload-lists >/dev/null       
       ;;
   "disable")
       sqlite3 /etc/pihole/gravity.db "update 'group' set 'enabled'=0 where name='$1'";
       # refresh PiHole
       /usr/local/bin/pihole restartdns reload-lists >/dev/null
       ;;
   "status")
       stat=`sqlite3 /etc/pihole/gravity.db " select enabled from 'group' where name = '$1';"`
       echo $stat
       exit 0
       ;;
   *)
   echo $"Usage: $0 {GroupName enable|disable|status}"
   exit 1
esac

exit 0
