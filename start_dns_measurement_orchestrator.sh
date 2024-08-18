#!/bin/bash

echo "starting measurement process..."
date

# increase UDP receive buffer size
#sudo sysctl -w net.core.rmem_max=25000000
## stop systemd-resolved and edit resolv.conf
##sudo systemctl stop systemd-resolved
##sudo systemctl disable systemd-resolved
# disable ipv6
#sudo sysctl -w net.ipv6.conf.all.disable_ipv6=1
#sudo sysctl -w net.ipv6.conf.default.disable_ipv6=1
#sudo sysctl -w net.ipv6.conf.lo.disable_ipv6=1

# start dns proxy servers (one per protocol)
H3_SERVER="h3://dns.google/dns-query"
QUIC_SERVER="quic://dnsforge.de:853"
UDP_SERVER="dns.google.com"

echo "------starting dnsproxy servers------"
sudo ./../dnsproxy/dnsproxy -u ${H3_SERVER} -v --insecure --ipv6-disabled -l 127.0.0.1 --https-port=443 --tls-crt=local1.crt --tls-key=local1.key -o dnsproxy_h3.log &
PID_H3=$!
echo "H3 proxy up and running on 127.0.0.1, PID: ${PID_H3}"
#./dnsproxy -u ${QUIC_SERVER}  -v --insecure --ipv6-disabled -l 127.0.0.2 --https-port=443 --tls-crt=local2.crt --tls-key=local2.key -o dnsproxy_quic.log &
#PID_QUIC=$!
#echo "QUIC proxy up and running on 127.0.0.2, PID: ${PID_QUIC}"
#./dnsproxy -u ${UDP_SERVER} -v --insecure --ipv6-disabled -l 127.0.0.3 --https-port=443 --tls-crt=local3.crt --tls-key=local3.key -o dnsproxy_udp.log &
#PID_UDP=$!
#echo "UDP proxy up and running on 127.0.0.3, PID: ${PID_UDP}"


echo "------starting measurements------"
python3 run_measurement.py 127.0.0.1 ${PID_H3} h3 ${H3_SERVER}
echo "H3 measuremment running PID: $!"
#python3 run_measurement.py 127.0.0.2 ${PID_QUIC} quic ${QUIC_SERVER}
#echo "QUIC measuremment running PID: $!"
#python3 run_measurement.py 127.0.0.3 udp ${PID_UDP} udp ${UDP_SERVER}
#echo "UDP measuremment running PID: $!"