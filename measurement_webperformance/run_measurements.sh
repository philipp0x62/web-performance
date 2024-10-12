#!/bin/bash

echo "starting measurement process..."
date

while read upstream; do
  qport=$(echo ${upstream} | cut -d: -f2)
  upstream=$(echo ${upstream} | cut -d: -f1)
  # skip server if it is unreachable
	ping -c 1 ${upstream} 2>&1 >/dev/null ;
	ping_code=$?
	if [ $ping_code = 0 ]
	then
		cd /home/ubuntu/dnsproxy
	
		https_upstream="${upstream}/dns-query"
		
		for p in "${protocols[@]}"
		do
			echo $p
	
			sleep 1
			echo "starting dnsproxy"
			./dnsproxy -u ${resolver} -v --insecure --ipv6-disabled -l "127.0.0.2" >& /home/ubuntu/web-performance/dnsproxy.log &
			dnsproxyPID=$!
	
			# measurements
			sleep 1
			echo "starting measurements"
			cd /home/ubuntu/web-performance
			python3 run_measurements.py $p $upstream $dnsproxyPID chrome $vp
	
			sleep 1
			echo "killing dnsproxy"
			sudo kill -SIGTERM $dnsproxyPID
			sudo rm dnsproxy.log
			cd /home/ubuntu/dnsproxy
		done
	else
		echo "${upstream} not reachable"
	fi
done < /home/ubuntu/web-performance/servers.txt

# restart systemd-resolved
sudo systemctl enable systemd-resolved
sudo systemctl start systemd-resolved

date
echo "FIN"
