#!/bin/bash

host_id=$1
metric_name=$2

# ホストメトリックのapiは最大で2000データポイントのみ返すので、5分粒度だとおよそ6日分が限度。よって、分割してリクエストする
./get_metrics.sh $host_id $metric_name $(date --date "19 days ago" +%s) $(date --date "13 days ago" +%s) > train.txt
./get_metrics.sh $host_id $metric_name $(date --date "13 days ago" +%s) $(date --date "7 days ago" +%s) >> train.txt
./get_metrics.sh $host_id $metric_name $(date --date "7 days ago" +%s) $(date --date "1 days ago" +%s) >> train.txt
./get_metrics.sh $host_id $metric_name $(date --date "1 days ago" +%s) $(date +%s) > test.txt

python lof.py train.txt test.txt
