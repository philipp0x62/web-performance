#!/bin/bash

echo "starting measurement process..."
date

# get vantage point info
vp=$(curl -s http://169.254.169.254/latest/meta-data/public-hostname | cut -d . -f2)
# increase UDP receive buffer size
sudo sysctl -w net.core.rmem_max=25000000
# stop systemd-resolved and edit resolv.conf
sudo systemctl stop systemd-resolved
sudo systemctl disable systemd-resolved
echo "nameserver 127.0.0.2" | sudo tee /etc/resolv.conf
# disable ipv6
sudo sysctl -w net.ipv6.conf.all.disable_ipv6=1
sudo sysctl -w net.ipv6.conf.default.disable_ipv6=1
sudo sysctl -w net.ipv6.conf.lo.disable_ipv6=1

declare -a protocols=("tls" "https" "quic" "tcp" "udp")

while read upstream; do
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
	
			if [ $p = "udp" ]
			then
				resolver="${upstream}"
			elif [ $p = "https" ]
			then
				resolver="${p}://${https_upstream}"
			elif [ $p = "quic" ]
			then
				resolver="quic://${upstream}:784"
			else
				resolver="${p}://${upstream}"
			fi
	
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
