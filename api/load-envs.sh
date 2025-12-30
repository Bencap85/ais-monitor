#!/bin/bash

set -e

load_params() {
  local prefix=$1

  local params
  params=$(aws ssm get-parameters-by-path \
    --path "$prefix" \
    --with-decryption \
    --region us-east-2 \
    --query "Parameters[*].[Name,Value]" \
    --output text)

  while read -r name value; do
    key=$(basename "$name")
    export "$key"="$value"
  done <<< "$params"
}

load_params "/ais/ws-broadcaster/"
load_params "/ais/repository/"
load_params "/ais/ingestor/"

# Show what was exported
echo "Loaded environment variables:"
env | grep -E "DB_|WS_|AIS_|AWS_|SQS_"
