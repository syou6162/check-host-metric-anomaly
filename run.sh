#!/bin/bash

OPTS=`getopt -o hmwcsn: --long host-id:,metric-name:,warning:,critical:,window-size:,n-neighbors: -n 'run.sh' -- "$@"`

if [ $? != 0 ] ; then echo "Failed parsing options." >&2 ; exit 3 ; fi

eval set -- "$OPTS"

HOST_ID=""
METRIC_NAME=""
WARNING=0.001
CRITICAL=0.0005
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

BASE_URL="https://mackerel.io"
ORG_NAME=$(curl -s -H "X-Api-Key: ${MACKEREL_APIKEY}" "https://mackerel.io/api/v0/org" | jq -r ".name")
echo HOST: "${BASE_URL}/orgs/${ORG_NAME}/hosts/${HOST_ID}"
echo "METRIC_NAME: $METRIC_NAME"
echo "WARNING: $WARNING"
echo "CRITICAL: $CRITICAL"
echo "WINDOW_SIZE: $WINDOW_SIZE"
echo "N_NEIGHBORS: $N_NEIGHBORS"

if [ "$HOST_ID" = "" ] ; then echo "Need host-id." >&2 ; exit 3 ; fi
if [ "$METRIC_NAME" = "" ] ; then echo "Need metric_name." >&2 ; exit 3 ; fi

MODEL_PREFIX="${HOST_ID}_${METRIC_NAME}_${WARNING}_${CRITICAL}_${WINDOW_SIZE}_${N_NEIGHBORS}"
MODEL_FILE_PATH="/tmp/${MODEL_PREFIX}_lof.pkl"

# 学習用のデータは1時間毎に新しく取得する
if [ ! -e $MODEL_FILE_PATH ] || [ ! $(find $MODEL_FILE_PATH -mmin -60) ]; then
  python train.py $HOST_ID $METRIC_NAME $WARNING $CRITICAL $WINDOW_SIZE $N_NEIGHBORS
fi

python test.py $HOST_ID $METRIC_NAME $MODEL_FILE_PATH $WINDOW_SIZE
