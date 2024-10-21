#!/bin/bash

echo "starting measurement process..."
date

echo "------starting measurements------"

INSTANCES=14
WEBSITE_NUMBER=1000000
# quotient is rounded down, -1 makes sure, that the full length is covered
INTERVAL=$((WEBSITE_NUMBER/(INSTANCES-1)))
echo "Interval $INTERVAL"

LOOP=$((INSTANCES/2))
echo "Loop $LOOP"
for i in `seq 0 $((LOOP-1))`
do
    echo "$i"
done

for i in `seq $((LOOP)) $((2*LOOP-1))`
do
  echo "$i"

done
