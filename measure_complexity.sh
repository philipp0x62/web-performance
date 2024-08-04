#!/bin/bash

echo "starting measurement process for complexity..."

# browser mob does not work with openjdk > 11
# workaround if openjdk is installed, but not the default version
echo 'export PATH="/usr/local/opt/openjdk@11/bin:$PATH"' >> ~/.zshrc

# reload environment
source ~/.zshrc
# check java version
java --version

# process is still getting killed, when the user is disconnected from the machine: otherwise use nohup
# write to log, to noticing errors
cd /Users/zitrusdrop/master_thesis/browsermob-proxy-2.1.4/bin/
#/Users/zitrusdrop/master_thesis/browsermob-proxy-2.1.4/bin/browsermob-proxy -port 8080 > browser_mob.log &
./browsermob-proxy -port 8080 &

# run python script
#python3 /Users/zitrusdrop/Desktop/Master/Semester_4/Masterarbeit_HPI/Experiments/forked/web-performance/measure_complexity.py
