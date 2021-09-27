#!/bin/bash

CNT=0
starttime=`date +%s`

if [ -n "$1" ]
then
   TIMEOUT=$1
else
   TIMEOUT=400
fi

if [ -n "$2" ]
then
   CHECKCNT=$2
else
   CHECKCNT=2
fi

while [ $CNT -lt $CHECKCNT ]
do 
   CNT=`docker-compose -f ./docker-compose-stage.yml logs 2>&1 | grep "LOG:  database system is ready to accept connections" | wc -l`
   curtime=`date +%s`
   let "delta=$curtime-$starttime"
   if [ "$delta" -ge "$TIMEOUT" ]
   then 
     exit -1
   fi
done;