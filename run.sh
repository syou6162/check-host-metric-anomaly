#!/bin/bash

OPTS=`getopt -o hmwcsn: --long host-id:,metric-name:,warning:,critical:,window-size:,n-neighbors: -n 'run.sh' -- "$@"`

if [ $? != 0 ] ; then echo "Failed parsing options." >&2 ; exit 3 ; fi

eval set -- "$OPTS"

HOST_ID=""
METRIC_NAME=""
WARNING=0.005
CRITICAL=0.001
WINDOW_SIZE=5
N_NEIGHBORS=20

while true; do
  case "$1" in
    -h | --host-id ) HOST_ID="$2"; shift; shift ;;
    -m | --metric-name ) METRIC_NAME="$2"; shift; shift ;;
    -w | --warning ) WARNING="$2"; shift; shift ;;
    -c | --critical ) CRITICAL="$2"; shift; shift ;;
    -s | --window-size ) WINDOW_SIZE="$2"; shift; shift ;;
    -n | --n-neighbors ) N_NEIGHBORS="$2"; shift; shift ;;
    -- ) shift; break ;;
    * ) break ;;
  esac
done

echo "HOST_ID: $HOST_ID"
echo "METRIC_NAME: $METRIC_NAME"
echo "WARNING: $WARNING"
echo "CRITICAL: $CRITICAL"
echo "WINDOW_SIZE: $WINDOW_SIZE"
echo "N_NEIGHBORS: $N_NEIGHBORS"

if [ "$HOST_ID" = "" ] ; then echo "Need host-id." >&2 ; exit 3 ; fi
if [ "$METRIC_NAME" = "" ] ; then echo "Need metric_name." >&2 ; exit 3 ; fi

# ホストメトリックのapiは最大で2000データポイントのみ返すので、5分粒度だとおよそ6日分が限度。よって、分割してリクエストする
./get_metrics.sh $HOST_ID $METRIC_NAME $(date --date "19 days ago" +%s) $(date --date "13 days ago" +%s) > train.txt
./get_metrics.sh $HOST_ID $METRIC_NAME $(date --date "13 days ago" +%s) $(date --date "7 days ago" +%s) >> train.txt
./get_metrics.sh $HOST_ID $METRIC_NAME $(date --date "7 days ago" +%s) $(date --date "1 days ago" +%s) >> train.txt
./get_metrics.sh $HOST_ID $METRIC_NAME $(date --date "1 days ago" +%s) $(date +%s) > test.txt

python lof.py train.txt test.txt $WARNING $CRITICAL $WINDOW_SIZE $N_NEIGHBORS
