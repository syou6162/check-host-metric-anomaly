#!/bin/bash

host_id=$1
metric_name=$2

from=$3
to=$4
curl -s -H "X-Api-Key: ${MACKEREL_APIKEY}" "https://mackerel.io/api/v0/hosts/${host_id}/metrics?name=${metric_name}&from=${from}&to=${to}" | jq ".metrics[] | .value"
