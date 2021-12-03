#!/bin/bash

echo "starting measurement process..."

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

cd /home/ubuntu/dnsproxy

declare -a protocols=("quic" "tls" "https" "tcp" "udp")
while read upstream; do
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
		else
			resolver="${p}://${upstream}"
		fi

		sleep 1
		echo "starting dnsproxy"
		./dnsproxy -u ${resolver} -v --ipv6-disabled -l "127.0.0.2" >& /home/ubuntu/web-performance/dnsproxy.log &
		dnsproxyPID=$!

		# measurements
		sleep 1
		echo "starting measurements"
		cd /home/ubuntu/web-performance
		python3 run_measurements.py $p $upstream $dnsproxyPID chrome
		cd /home/ubuntu/dnsproxy

		sleep 1
		echo "killing dnsproxy"
		sudo kill -SIGTERM $dnsproxyPID
	done
done < nameservers.txt

# restart systemd-resolved
sudo systemctl enable systemd-resolved
sudo systemctl start systemd-resolved

echo "FIN"
