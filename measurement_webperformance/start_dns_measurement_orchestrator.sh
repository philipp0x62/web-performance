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
#H3_SERVER="h3://2f07i9strpu.dns.controld.com."
#QUIC_SERVER="quic://2f07i9strpu.dns.controld.com."
#UDP_SERVER="2f07i9strpu.dns.controld.com."

H3_SERVER="h3://resolver64.dns4all.eu"
QUIC_SERVER="quic://resolver64.dns4all.eu"
UDP_SERVER="resolver64.dns4all.eu"

echo "------starting dnsproxy servers------"
cd ../../dnsproxy
nohup ./dnsproxy -u h3://resolver64.dns4all.eu --ipv6-disabled -l 127.0.0.1 --https-port=443 --tls-crt=server.crt --tls-key=server.key > doh-webperformance.log &
nohup ./dnsproxy -u quic://resolver64.dns4all.eu --ipv6-disabled -l 127.0.0.2 --https-port=443 --tls-crt=server.crt --tls-key=server.key > doq-webperformance.log &
nohup ./dnsproxy -u resolver64.dns4all.eu --ipv6-disabled -l 127.0.0.3 --https-port=443 --tls-crt=server.crt --tls-key=server.key > dou-webperformance.log &

#cd ../../routedns/cmd/routedns
#nohup go run . doh-client-doh-out.toml > doh-webperformance.log &
#PID_H3=$!
#echo "H3 proxy up and running on 127.0.0.1, PID: ${PID_H3}"
#nohup go run . doq-client-doh-out.toml > doq-webperformance.log &
#PID_QUIC=$!
#echo "QUIC proxy up and running on 127.0.0.2, PID: ${PID_QUIC}"
#nohup go run . dou-client-doh-out.toml > dou-webperformance.log &
#PID_UDP=$!
#echo "UDP proxy up and running on 127.0.0.3, PID: ${PID_UDP}"

#nohup go run . doh-client-doh-out_2.toml > doh-webperformance.log &
#PID_H3_2=$!
#echo "H3 proxy up and running on 127.0.0.4, PID: ${PID_H3_2}"
#nohup go run . doq-client-doh-out_2.toml > doq-webperformance.log &
#PID_QUIC_2=$!
#echo "QUIC proxy up and running on 127.0.0.5, PID: ${PID_QUIC_2}"
#nohup go run . dou-client-doh-out_2.toml > dou-webperformance.log &
#PID_UDP_2=$!
#echo "UDP proxy up and running on 127.0.0.6, PID: ${PID_UDP_2}"
#
cd ../web-performance/measurement_webperformance

#sudo ./../dnsproxy/dnsproxy -u ${H3_SERVER} -v --ipv6-disabled -l 127.0.0.1 --https-port=443 --tls-crt=local.crt --tls-key=local.key -o dnsproxy_h3.log &
#sudo ./../dnsproxy/dnsproxy./dnsproxy -u ${QUIC_SERVER}  -v --ipv6-disabled -l 127.0.0.2 --https-port=443 --tls-crt=local.crt --tls-key=local.key -o dnsproxy_quic.log &
#sudo ./../dnsproxy/dnsproxy -u ${UDP_SERVER} -v --ipv6-disabled -l 127.0.0.3 --https-port=443 --tls-crt=local.crt --tls-key=local.key -o dnsproxy_udp.log &



echo "------starting measurements------"

INSTANCES=14
WEBSITE_NUMBER=1000000
# quotient is rounded down, -1 makes sure, that the full length is covered
INTERVAL=$((WEBSITE_NUMBER/(INSTANCES-1)))
echo "$INTERVAL"

#LOOP=$((INSTANCES/2))
#for i in `seq 0 $((LOOP-1))`
for i in `seq 0 $((INSTANCES-1))`
do
    nohup python3 -u run_measurement.py 127.0.0.1 h3 ${H3_SERVER} $((i*INTERVAL)) $INTERVAL > webperformance_h3_${i}.log 2>&1 &
    #echo "H3 measuremment running PID: $!"
    nohup python3 -u run_measurement.py 127.0.0.2 quic ${QUIC_SERVER} $((i*INTERVAL)) $INTERVAL > webperformance_quic_${i}.log 2>&1 &
    #echo "QUIC measuremment running PID: $!"
    nohup python3 -u run_measurement.py 127.0.0.3 udp ${UDP_SERVER} $((i*INTERVAL)) $INTERVAL > webperformance_udp_${i}.log 2>&1 &
    #echo "UDP measuremment running PID: $!"

done
#
#for i in `seq $((LOOP)) $((2*LOOP-1))`
#do
#    nohup python3 run_measurement.py 127.0.0.4 h3 ${H3_SERVER} $((i*INTERVAL)) $INTERVAL > webperformance_h3_${i}.log &
#    #echo "H3 measuremment running PID: $!"
#    nohup python3 run_measurement.py 127.0.0.5 quic ${QUIC_SERVER} $((i*INTERVAL)) $INTERVAL > webperformance_quic_${i}.log &
#    #echo "QUIC measuremment running PID: $!"
#    nohup python3 run_measurement.py 127.0.0.6 udp ${UDP_SERVER} $((i*INTERVAL)) $INTERVAL > webperformance_udp_${i}.log &
#    #echo "UDP measuremment running PID: $!"
#
#done
