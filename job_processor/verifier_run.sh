#!/bin/bash

PIDFILE=/home/forest/pyquil_intermediate/job_processor/job_verifier.pid
if [ -f $PIDFILE ]
then
  PID=$(cat $PIDFILE)
  ps -p $PID > /dev/null 2>&1
  if [ $? -eq 0 ]
  then
    echo "Process already running"
    exit 1
  else
    ## Process not found assume not running
    echo $$ > $PIDFILE
    if [ $? -ne 0 ]
    then
      echo "Could not create PID file"
      exit 1
    fi
  fi
else
  echo $$ > $PIDFILE
  if [ $? -ne 0 ]
  then
    echo "Could not create PID file"
    exit 1
  fi
fi


source /home/forest/pyquil_intermediate/job_processor/venv/bin/activate
python3 /home/forest/pyquil_intermediate/job_processor/job_verifier.py

rm $PIDFILE
