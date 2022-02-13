#!/bin/bash

# This script creates a list of five reachable upstreams
i=0
while read upstream; do
  if [ $i -lt 5 ]
  then
    ping -c 1 ${upstream} 2>&1 >/dev/null ;
    ping_code=$?
    if [ $ping_code = 0 ]
    then
	    echo ${upstream} >> servers.txt
      ((i=i+1))
    fi
  fi
done < /home/ubuntu/web-performance/all_servers.txt