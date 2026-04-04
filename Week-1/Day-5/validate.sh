#!/bin/bash

LOG_FILE="validate.log"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

if [ ! -d "src" ]; then
  echo "[$TIMESTAMP] ERROR: src directory missing" >> $LOG_FILE
  exit 1
fi

if ! jq empty config.json 2>/dev/null; then
  echo "[$TIMESTAMP] ERROR: Invalid config.json" >> $LOG_FILE
  exit 1
fi

echo "[$TIMESTAMP] Validation successful" >> $LOG_FILE
exit 0
