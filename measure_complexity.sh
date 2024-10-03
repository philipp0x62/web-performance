#!/bin/bash

echo "starting measurement process for complexity..."

## browser mob does not work with openjdk > 11
## workaround if openjdk is installed, but not the default version
#echo 'export PATH="/usr/local/opt/openjdk@11/bin:$PATH"' >> ~/.zshrc

## reload environment
#source ~/.zshrc
## check java version
#java --version
#
## process is still getting killed, when the user is disconnected from the machine: otherwise use nohup
## write to log, to noticing errors
#cd /Users/zitrusdrop/master_thesis/browsermob-proxy-2.1.4/bin/
##/Users/zitrusdrop/master_thesis/browsermob-proxy-2.1.4/bin/browsermob-proxy -port 8080 > browser_mob.log &
#./browsermob-proxy -port 8080 &
#
## run python script scaling must be at factor 30 to get all 5 mio in a under a week queried
#INSTANCES=30
#WEBSITE_NUMBER=5000000

INSTANCES=15
WEBSITE_NUMBER=1000000
# quotient is rounded down, -1 makes sure, that the full length is covered
INTERVAL=$((WEBSITE_NUMBER/(INSTANCES-1)))
echo "$INTERVAL"

for i in `seq 0 $((INSTANCES-1))`
do
    #echo "$i"
    # nohup python3 measure_complexity.py $((i*INTERVAL)) $INTERVAL > complexity_${i}.log &
    #if [[ $i==1 ]] || [[ $i==9 ]]; then
    #        continue
    #fi
    python3 measure_complexity.py $((i*INTERVAL)) $INTERVAL > complexity_${i}.log &

done
##python3 /Users/zitrusdrop/Desktop/Master/Semester_4/Masterarbeit_HPI/Experiments/forked/web-performance/measure_complexity.py
